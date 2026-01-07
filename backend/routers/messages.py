"""
消息/通知 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from database import get_db
from models import NotificationCreate, NotificationResponse, MessageResponse
from auth import get_current_user, require_admin_or_super

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("")
async def get_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """获取我的消息列表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 获取总数
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE receiver_id = ?",
            (current_user["id"],)
        )
        total = cursor.fetchone()[0]
        
        # 获取消息
        cursor.execute("""
            SELECT id, sender_name, title, content, is_read, created_at
            FROM messages
            WHERE receiver_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (current_user["id"], page_size, (page - 1) * page_size))
        
        rows = cursor.fetchall()
        
        return {
            "items": [{
                **dict(row),
                "is_read": bool(row["is_read"])
            } for row in rows],
            "total": total
        }


@router.get("/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    """获取未读消息数量"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND is_read = 0",
            (current_user["id"],)
        )
        count = cursor.fetchone()[0]
        return {"count": count}


@router.post("/{message_id}/read", response_model=MessageResponse)
async def mark_read(
    message_id: int,
    current_user: dict = Depends(get_current_user)
):
    """标记消息为已读"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查消息是否属于当前用户
        cursor.execute(
            "SELECT id FROM messages WHERE id = ? AND receiver_id = ?",
            (message_id, current_user["id"])
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="消息不存在")
        
        cursor.execute(
            "UPDATE messages SET is_read = 1 WHERE id = ?",
            (message_id,)
        )
        conn.commit()
        
        return MessageResponse(message="已标记为已读")


@router.post("/read-all", response_model=MessageResponse)
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    """标记所有消息为已读"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE messages SET is_read = 1 WHERE receiver_id = ? AND is_read = 0",
            (current_user["id"],)
        )
        conn.commit()
        
        return MessageResponse(message="所有消息已标记为已读")


@router.post("/send", response_model=MessageResponse)
async def send_notification(
    notification: NotificationCreate,
    current_user: dict = Depends(require_admin_or_super)
):
    """发送通知（管理员/超管）"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 确定发送者名称
        sender_name = "admin" if current_user["role"] == "admin" else "system"
        
        # 确定接收者
        if not notification.receiver_ids:
            # 群发给所有学生
            cursor.execute("SELECT id FROM users WHERE role = 'student'")
            receiver_ids = [row["id"] for row in cursor.fetchall()]
        else:
            receiver_ids = notification.receiver_ids
        
        if not receiver_ids:
            raise HTTPException(status_code=400, detail="没有可发送的接收者")
        
        # 发送消息
        for receiver_id in receiver_ids:
            cursor.execute("""
                INSERT INTO messages (sender_name, receiver_id, title, content)
                VALUES (?, ?, ?, ?)
            """, (sender_name, receiver_id, notification.title, notification.content))
        
        conn.commit()
        
        count = len(receiver_ids)
        return MessageResponse(message=f"已向 {count} 位用户发送通知")


@router.get("/users-for-send")
async def get_users_for_send(
    keyword: Optional[str] = None,
    current_user: dict = Depends(require_admin_or_super)
):
    """获取可发送消息的用户列表（管理员/超管）"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = "SELECT id, student_id, name FROM users WHERE role = 'student'"
        params = []
        
        if keyword:
            query += " AND (student_id LIKE ? OR name LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        query += " ORDER BY name LIMIT 100"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
