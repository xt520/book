"""
超级管理员 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from database import get_db, get_password_hash
from models import (
    SystemSettingsUpdate, SystemSettingsResponse,
    AdminCreate, OperationLogResponse, MessageResponse
)
from auth import require_super_admin, get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


def log_operation(user_id: int, action: str, detail: str = None):
    """记录操作日志"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO operation_logs (user_id, action, detail)
            VALUES (?, ?, ?)
        ''', (user_id, action, detail))
        conn.commit()


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_settings(current_user: dict = Depends(require_super_admin)):
    """获取系统设置"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM system_settings")
        rows = cursor.fetchall()
        
        settings = {}
        for row in rows:
            key = row["key"]
            value = row["value"]
            if key in ["min_borrow_days", "max_borrow_days"]:
                settings[key] = int(value)
            elif key == "fine_per_day":
                settings[key] = float(value)
            else:
                settings[key] = value
        
        return SystemSettingsResponse(
            min_borrow_days=settings.get("min_borrow_days", 1),
            max_borrow_days=settings.get("max_borrow_days", 60),
            fine_per_day=settings.get("fine_per_day", 0.5)
        )


@router.put("/settings", response_model=MessageResponse)
async def update_settings(
    settings: SystemSettingsUpdate,
    current_user: dict = Depends(require_super_admin)
):
    """更新系统设置"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        updates = []
        if settings.min_borrow_days is not None:
            cursor.execute(
                "UPDATE system_settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
                (str(settings.min_borrow_days), "min_borrow_days")
            )
            updates.append(f"最短借阅天数={settings.min_borrow_days}")
            
        if settings.max_borrow_days is not None:
            cursor.execute(
                "UPDATE system_settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
                (str(settings.max_borrow_days), "max_borrow_days")
            )
            updates.append(f"最长借阅天数={settings.max_borrow_days}")
            
        if settings.fine_per_day is not None:
            cursor.execute(
                "UPDATE system_settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
                (str(settings.fine_per_day), "fine_per_day")
            )
            updates.append(f"每日罚款={settings.fine_per_day}")
        
        conn.commit()
        
        log_operation(current_user["id"], "更新系统设置", ", ".join(updates))
        
        return MessageResponse(message="系统设置已更新")


@router.get("/admins")
async def get_admins(current_user: dict = Depends(require_super_admin)):
    """获取管理员列表"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, student_id, name, role, created_at 
            FROM users 
            WHERE role = 'admin'
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


@router.post("/admins", response_model=MessageResponse)
async def create_admin(
    admin: AdminCreate,
    current_user: dict = Depends(require_super_admin)
):
    """创建管理员账号"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查学号是否已存在
        cursor.execute("SELECT id FROM users WHERE student_id = ?", (admin.student_id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="该学号已存在")
        
        # 创建管理员
        password_hash = get_password_hash(admin.password or "admin123")
        
        cursor.execute('''
            INSERT INTO users (student_id, password_hash, name, role, first_login)
            VALUES (?, ?, ?, 'admin', 0)
        ''', (admin.student_id, password_hash, admin.name))
        
        conn.commit()
        
        log_operation(current_user["id"], "创建管理员", f"{admin.name} ({admin.student_id})")
        
        return MessageResponse(message=f"管理员 {admin.name} 创建成功")


@router.delete("/admins/{admin_id}", response_model=MessageResponse)
async def delete_admin(
    admin_id: int,
    current_user: dict = Depends(require_super_admin)
):
    """删除管理员账号"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查管理员是否存在
        cursor.execute("SELECT id, name, student_id, role FROM users WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        
        if not admin:
            raise HTTPException(status_code=404, detail="管理员不存在")
        
        if admin["role"] == "super_admin":
            raise HTTPException(status_code=400, detail="无法删除超级管理员")
        
        if admin["role"] != "admin":
            raise HTTPException(status_code=400, detail="该用户不是管理员")
        
        cursor.execute("DELETE FROM users WHERE id = ?", (admin_id,))
        conn.commit()
        
        log_operation(current_user["id"], "删除管理员", f"{admin['name']} ({admin['student_id']})")
        
        return MessageResponse(message="管理员已删除")


@router.post("/admins/{admin_id}/reset-password", response_model=MessageResponse)
async def reset_admin_password(
    admin_id: int,
    current_user: dict = Depends(require_super_admin)
):
    """重置管理员密码"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查管理员是否存在
        cursor.execute("SELECT id, name, student_id, role FROM users WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        
        if not admin:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 重置密码为 admin123
        new_password_hash = get_password_hash("admin123")
        cursor.execute(
            "UPDATE users SET password_hash = ?, first_login = 1 WHERE id = ?",
            (new_password_hash, admin_id)
        )
        conn.commit()
        
        log_operation(current_user["id"], "重置密码", f"{admin['name']} ({admin['student_id']})")
        
        return MessageResponse(message=f"密码已重置为 admin123")


@router.get("/logs")
async def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(require_super_admin)
):
    """获取操作日志"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 获取总数
        cursor.execute("SELECT COUNT(*) FROM operation_logs")
        total = cursor.fetchone()[0]
        
        # 获取日志
        cursor.execute("""
            SELECT ol.id, ol.user_id, u.name as user_name, ol.action, ol.detail, ol.created_at
            FROM operation_logs ol
            LEFT JOIN users u ON ol.user_id = u.id
            ORDER BY ol.created_at DESC
            LIMIT ? OFFSET ?
        """, (page_size, (page - 1) * page_size))
        
        rows = cursor.fetchall()
        
        return {
            "items": [dict(row) for row in rows],
            "total": total
        }


@router.post("/batch-overdue-notify", response_model=MessageResponse)
async def batch_overdue_notify(current_user: dict = Depends(require_super_admin)):
    """一键发送逾期提醒"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 获取所有逾期记录
        cursor.execute("""
            SELECT br.user_id, b.title, br.due_date, 
                   julianday('now') - julianday(br.due_date) as overdue_days
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.status = 'borrowed' AND br.due_date < CURRENT_TIMESTAMP
        """)
        
        overdue_records = cursor.fetchall()
        
        if not overdue_records:
            return MessageResponse(message="暂无逾期记录")
        
        # 按用户分组发送消息
        user_overdues = {}
        for record in overdue_records:
            user_id = record["user_id"]
            if user_id not in user_overdues:
                user_overdues[user_id] = []
            user_overdues[user_id].append({
                "title": record["title"],
                "days": int(record["overdue_days"])
            })
        
        count = 0
        for user_id, books in user_overdues.items():
            book_list = "\n".join([f"- 《{b['title']}》已逾期 {b['days']} 天" for b in books])
            content = f"您有以下图书已逾期，请尽快归还：\n{book_list}"
            
            cursor.execute("""
                INSERT INTO messages (sender_name, receiver_id, title, content)
                VALUES ('system', ?, '逾期提醒', ?)
            """, (user_id, content))
            count += 1
        
        conn.commit()
        
        log_operation(current_user["id"], "一键逾期提醒", f"通知了 {count} 位用户")
        
        return MessageResponse(message=f"已向 {count} 位用户发送逾期提醒")
