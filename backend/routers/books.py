"""
图书管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List

from database import get_db
from models import BookCreate, BookUpdate, BookResponse, MessageResponse
from auth import get_current_user, require_admin

router = APIRouter(prefix="/api/books", tags=["books"])

@router.get("")
async def get_books(
    search: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user)
):
    """获取图书列表（带分页）"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 构建基础查询条件
        where_clause = "WHERE status = 'active'"
        params = []
        
        if search:
            where_clause += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if category and category != "全部":
            where_clause += " AND category = ?"
            params.append(category)
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as count FROM books {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()["count"]
        
        # 获取分页数据
        query = f"SELECT * FROM books {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([page_size, (page - 1) * page_size])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return {
            "items": [dict(row) for row in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

@router.get("/categories", response_model=List[str])
async def get_categories(current_user: dict = Depends(get_current_user)):
    """获取所有分类"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM books WHERE status = 'active' ORDER BY category")
        rows = cursor.fetchall()
        return [row["category"] for row in rows]

@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """获取统计数据"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 总图书数
        cursor.execute("SELECT COUNT(*) as count FROM books WHERE status = 'active'")
        total_books = cursor.fetchone()["count"]
        
        # 分类数
        cursor.execute("SELECT COUNT(DISTINCT category) as count FROM books WHERE status = 'active'")
        total_categories = cursor.fetchone()["count"]
        
        # 作者数
        cursor.execute("SELECT COUNT(DISTINCT author) as count FROM books WHERE status = 'active'")
        total_authors = cursor.fetchone()["count"]
        
        # 当前借出数
        cursor.execute("SELECT COUNT(*) as count FROM borrow_records WHERE status = 'borrowed'")
        borrowed_count = cursor.fetchone()["count"]
        
        return {
            "total_books": total_books,
            "total_categories": total_categories,
            "total_authors": total_authors,
            "borrowed_count": borrowed_count
        }

@router.get("/{book_id}")
async def get_book(book_id: int, current_user: dict = Depends(get_current_user)):
    """获取单本图书详情"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ? AND status = 'active'", (book_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="图书不存在")
        
        return dict(row)

@router.post("", response_model=MessageResponse)
async def create_book(book: BookCreate, current_user: dict = Depends(require_admin)):
    """上架新图书（仅管理员）"""
    from covers_util import download_cover
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查 ISBN 是否重复
        if book.isbn:
            cursor.execute("SELECT id FROM books WHERE isbn = ?", (book.isbn,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="ISBN 已存在")
        
        # 下载封面到本地并获取状态
        local_cover = ""
        cover_status = 2  # 默认无法获取
        
        if book.cover:
            local_cover, cover_status = await download_cover(book.cover, book.isbn)
        
        cursor.execute('''
            INSERT INTO books (title, author, isbn, category, cover, cover_status, total_count, available_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (book.title, book.author, book.isbn, book.category, local_cover, cover_status, book.total_count, book.total_count))
        
        conn.commit()
        return MessageResponse(message="图书上架成功")

@router.put("/{book_id}", response_model=MessageResponse)
async def update_book(book_id: int, book: BookUpdate, current_user: dict = Depends(require_admin)):
    """更新图书信息（仅管理员）"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查图书是否存在
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="图书不存在")
        
        # 构建更新语句
        updates = []
        params = []
        
        if book.title is not None:
            updates.append("title = ?")
            params.append(book.title)
        if book.author is not None:
            updates.append("author = ?")
            params.append(book.author)
        if book.isbn is not None:
            updates.append("isbn = ?")
            params.append(book.isbn)
        if book.category is not None:
            updates.append("category = ?")
            params.append(book.category)
        if book.cover is not None:
            updates.append("cover = ?")
            params.append(book.cover)
        if book.total_count is not None:
            # 计算可借数量的变化
            diff = book.total_count - existing["total_count"]
            updates.append("total_count = ?")
            updates.append("available_count = available_count + ?")
            params.append(book.total_count)
            params.append(diff)
        
        if updates:
            query = f"UPDATE books SET {', '.join(updates)} WHERE id = ?"
            params.append(book_id)
            cursor.execute(query, params)
            conn.commit()
        
        return MessageResponse(message="图书信息更新成功")

@router.delete("/{book_id}", response_model=MessageResponse)
async def delete_book(book_id: int, current_user: dict = Depends(require_admin)):
    """下架图书（仅管理员）"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查是否有未归还的借阅
        cursor.execute(
            "SELECT COUNT(*) as count FROM borrow_records WHERE book_id = ? AND status = 'borrowed'",
            (book_id,)
        )
        if cursor.fetchone()["count"] > 0:
            raise HTTPException(status_code=400, detail="该图书有未归还的借阅记录，无法下架")
        
        # 软删除
        cursor.execute("UPDATE books SET status = 'deleted' WHERE id = ?", (book_id,))
        conn.commit()
        
        return MessageResponse(message="图书下架成功")
