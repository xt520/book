"""
用户管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..database import get_db, get_password_hash
from ..models import UserCreate, UserInfo, MessageResponse
from ..auth import require_admin

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=dict)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """获取用户列表（仅管理员）"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 构建查询条件
        base_query = "FROM users WHERE 1=1"
        params = []
        
        if keyword:
            base_query += " AND (student_id LIKE ? OR name LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
            
        # 获取总数
        count_query = f"SELECT COUNT(*) {base_query}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 获取分页数据
        query = f"SELECT id, student_id, name, role, created_at {base_query} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([page_size, (page - 1) * page_size])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return {
            "items": [dict(row) for row in rows],
            "total": total
        }

@router.post("", response_model=MessageResponse)
async def create_user(
    user: UserCreate,
    current_user: dict = Depends(require_admin)
):
    """创建新用户（仅管理员）"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查学号是否已存在
        cursor.execute("SELECT id FROM users WHERE student_id = ?", (user.student_id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="该学号已存在")
            
        # 创建用户
        password_hash = get_password_hash(user.password or "12345678")
        
        cursor.execute('''
            INSERT INTO users (student_id, password_hash, name, role, first_login)
            VALUES (?, ?, ?, 'student', 1)
        ''', (user.student_id, password_hash, user.name))
        
        conn.commit()
        return MessageResponse(message=f"学生 {user.name} ({user.student_id}) 添加成功")

@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(require_admin)
):
    """删除用户（仅管理员）"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute("SELECT id, role FROM users WHERE id = ?", (user_id,))
        target_user = cursor.fetchone()
        
        if not target_user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        if target_user["role"] == "admin":
            raise HTTPException(status_code=400, detail="无法删除管理员账号")
            
        # 检查是否有未还书籍
        cursor.execute("SELECT id FROM borrow_records WHERE user_id = ? AND status = 'borrowed'", (user_id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="该用户还有未归还的图书，无法删除")
            
        # 删除用户（级联删除借阅记录通常由数据库外键处理，但这里我们先手动处理或保留记录）
        # 考虑到历史记录的重要性，通常不建议物理删除用户，这里做物理删除示范
        # 先删除借阅记录
        cursor.execute("DELETE FROM borrow_records WHERE user_id = ?", (user_id,))
        
        # 删除用户
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        return MessageResponse(message="用户已删除")
