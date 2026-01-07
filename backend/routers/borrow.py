"""
借阅管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import BorrowRequest, BorrowRecordResponse, MessageResponse
from auth import get_current_user, require_admin_or_super

router = APIRouter(prefix="/api/borrow", tags=["borrow"])

@router.post("/return-by-isbn", response_model=MessageResponse)
async def return_book_by_isbn(
    isbn: str = Query(..., description="图书ISBN"),
    student_id: str = Query(None, description="学号（管理员必填）"),
    current_user: dict = Depends(get_current_user)
):
    """通过ISBN扫码还书"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 通过 ISBN 找到图书
        cursor.execute("SELECT id, title FROM books WHERE isbn = ?", (isbn,))
        book = cursor.fetchone()
        
        if not book:
            raise HTTPException(status_code=404, detail=f"未找到 ISBN 为 {isbn} 的图书")
        
        book_id = book["id"]
        book_title = book["title"]
        
        # 确定要归还的用户
        target_user_id = None
        target_user_name = ""
        
        if student_id:
            # 通过学号查找用户
            cursor.execute("SELECT id, name FROM users WHERE student_id = ?", (student_id,))
            user_row = cursor.fetchone()
            if not user_row:
                raise HTTPException(status_code=404, detail=f"未找到学号为 {student_id} 的用户")
            target_user_id = user_row["id"]
            target_user_name = user_row["name"]
        elif current_user["role"] != "admin":
            # 非管理员默认归还自己的
            target_user_id = current_user["id"]
            target_user_name = current_user["name"]
        else:
            # 管理员必须指定学号
            raise HTTPException(status_code=400, detail="请输入借阅人学号")
        
        # 查找该用户对该书的借阅记录
        cursor.execute('''
            SELECT br.id
            FROM borrow_records br
            WHERE br.book_id = ? AND br.user_id = ? AND br.status = 'borrowed'
        ''', (book_id, target_user_id))
        
        record = cursor.fetchone()
        
        if not record:
            raise HTTPException(status_code=404, detail=f"学号 {student_id} 没有借阅《{book_title}》的记录")
        
        # 执行归还
        cursor.execute('''
            UPDATE borrow_records 
            SET status = 'returned', return_date = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (record["id"],))
        
        cursor.execute(
            "UPDATE books SET available_count = available_count + 1 WHERE id = ?",
            (book_id,)
        )
        
        conn.commit()
        
        return MessageResponse(message=f"《{book_title}》（{target_user_name}）归还成功")

@router.post("/{book_id}", response_model=MessageResponse)
async def borrow_book(
    book_id: int,
    request: BorrowRequest = BorrowRequest(),
    current_user: dict = Depends(get_current_user)
):
    """借阅图书"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 获取系统设置的借阅天数范围
        cursor.execute("SELECT key, value FROM system_settings WHERE key IN ('min_borrow_days', 'max_borrow_days')")
        settings = {row["key"]: int(row["value"]) for row in cursor.fetchall()}
        min_days = settings.get("min_borrow_days", 1)
        max_days = settings.get("max_borrow_days", 60)
        
        # 验证借阅天数
        if request.days < min_days or request.days > max_days:
            raise HTTPException(
                status_code=400, 
                detail=f"借阅天数必须在 {min_days} 到 {max_days} 天之间"
            )
        
        # 检查图书是否存在且可借
        cursor.execute("SELECT * FROM books WHERE id = ? AND status = 'active'", (book_id,))
        book = cursor.fetchone()
        
        if not book:
            raise HTTPException(status_code=404, detail="图书不存在")
        
        if book["available_count"] <= 0:
            raise HTTPException(status_code=400, detail="该图书已全部借出")
        
        # 检查用户是否已借阅该书（未归还）
        cursor.execute('''
            SELECT id FROM borrow_records 
            WHERE book_id = ? AND user_id = ? AND status = 'borrowed'
        ''', (book_id, current_user["id"]))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="您已借阅该书，请先归还")
        
        # 创建借阅记录
        due_date = datetime.now() + timedelta(days=request.days)
        cursor.execute('''
            INSERT INTO borrow_records (book_id, user_id, due_date, status)
            VALUES (?, ?, ?, 'borrowed')
        ''', (book_id, current_user["id"], due_date.strftime("%Y-%m-%d %H:%M:%S")))
        
        # 更新图书可借数量
        cursor.execute(
            "UPDATE books SET available_count = available_count - 1 WHERE id = ?",
            (book_id,)
        )
        
        conn.commit()
        return MessageResponse(message=f"借阅成功，请在 {due_date.strftime('%Y-%m-%d')} 前归还")

@router.post("/return/{record_id}", response_model=MessageResponse)
async def return_book(record_id: int, current_user: dict = Depends(get_current_user)):
    """归还图书"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查借阅记录
        cursor.execute('''
            SELECT br.*, b.title as book_title
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.id = ? AND br.status = 'borrowed'
        ''', (record_id,))
        
        record = cursor.fetchone()
        if not record:
            raise HTTPException(status_code=404, detail="借阅记录不存在或已归还")
        
        # 检查权限（只能归还自己的书，管理员可以帮别人归还）
        if current_user["role"] != "admin" and record["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="无权操作此借阅记录")
        
        # 更新借阅记录
        cursor.execute('''
            UPDATE borrow_records 
            SET status = 'returned', return_date = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (record_id,))
        
        # 更新图书可借数量
        cursor.execute(
            "UPDATE books SET available_count = available_count + 1 WHERE id = ?",
            (record["book_id"],)
        )
        
        conn.commit()
        return MessageResponse(message=f"《{record['book_title']}》归还成功")




@router.get("/records", response_model=List[dict])
async def get_borrow_records(
    status: Optional[str] = Query(None, description="状态筛选: borrowed, returned"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="搜索关键词：学号/姓名/ISBN"),
    current_user: dict = Depends(get_current_user)
):
    """获取借阅记录（管理员看全部，学生看自己的）"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                br.id,
                br.book_id,
                b.title as book_title,
                b.author as book_author,
                b.isbn as book_isbn,
                br.user_id,
                u.name as user_name,
                u.student_id,
                br.borrow_date,
                br.due_date,
                br.return_date,
                br.status
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            JOIN users u ON br.user_id = u.id
            WHERE 1=1
        '''
        params = []
        
        # 非管理员只能看自己的记录
        if current_user["role"] != "admin":
            query += " AND br.user_id = ?"
            params.append(current_user["id"])
        
        if status:
            query += " AND br.status = ?"
            params.append(status)
            
        if keyword:
            query += " AND (u.student_id LIKE ? OR u.name LIKE ? OR b.isbn LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        query += " ORDER BY br.borrow_date DESC LIMIT ? OFFSET ?"
        params.extend([page_size, (page - 1) * page_size])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]

@router.get("/my", response_model=List[dict])
async def get_my_borrows(current_user: dict = Depends(get_current_user)):
    """获取我的借阅记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                br.id,
                br.book_id,
                b.title as book_title,
                b.author as book_author,
                b.category,
                b.cover,
                br.borrow_date,
                br.due_date,
                br.return_date,
                br.status
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.user_id = ?
            ORDER BY br.borrow_date DESC
        ''', (current_user["id"],))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

@router.get("/overdue")
async def get_overdue_records(current_user: dict = Depends(require_admin_or_super)):
    """获取逾期未还记录（仅管理员）"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                br.id,
                br.book_id,
                b.title as book_title,
                u.name as user_name,
                u.student_id,
                br.borrow_date,
                br.due_date,
                julianday('now') - julianday(br.due_date) as overdue_days
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            JOIN users u ON br.user_id = u.id
            WHERE br.status = 'borrowed' AND br.due_date < CURRENT_TIMESTAMP
            ORDER BY br.due_date ASC
        ''')
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
