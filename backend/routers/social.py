"""
社交功能 API 路由 (评论 & 收藏)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from database import get_db
from models import ReviewCreate, ReviewResponse, FavoriteResponse, MessageResponse
from auth import get_current_user

router = APIRouter(prefix="/api", tags=["social"])

# ==================== 评论功能 ====================

@router.post("/books/{book_id}/reviews", response_model=MessageResponse)
async def create_review(
    book_id: int,
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """发布/更新评论"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查图书是否存在
        cursor.execute("SELECT id FROM books WHERE id = ?", (book_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="图书不存在")
            
        # 检查是否已借阅过（可选：限制只有借过书的人才能评论？）
        # 这里暂时不做限制，所有登录用户都可评论
        
        # 检查是否已评论，如果是则更新
        cursor.execute(
            "SELECT id FROM reviews WHERE book_id = ? AND user_id = ?",
            (book_id, current_user["id"])
        )
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE reviews 
                SET rating = ?, content = ?, created_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (review.rating, review.content, existing["id"]))
            conn.commit()
            return MessageResponse(message="评论已更新")
        else:
            cursor.execute('''
                INSERT INTO reviews (book_id, user_id, rating, content)
                VALUES (?, ?, ?, ?)
            ''', (book_id, current_user["id"], review.rating, review.content))
            conn.commit()
            return MessageResponse(message="评论发布成功")

@router.get("/books/{book_id}/reviews", response_model=List[ReviewResponse])
async def get_reviews(book_id: int):
    """获取图书评论"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                r.id, r.book_id, r.user_id, u.name as user_name,
                r.rating, r.content, r.created_at
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.book_id = ?
            ORDER BY r.created_at DESC
        ''', (book_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# ==================== 收藏功能 ====================

@router.post("/books/{book_id}/favorite", response_model=MessageResponse)
async def toggle_favorite(
    book_id: int,
    current_user: dict = Depends(get_current_user)
):
    """收藏/取消收藏"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check existing
        cursor.execute(
            "SELECT id FROM favorites WHERE book_id = ? AND user_id = ?",
            (book_id, current_user["id"])
        )
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("DELETE FROM favorites WHERE id = ?", (existing["id"],))
            message = "已取消收藏"
        else:
            cursor.execute(
                "INSERT INTO favorites (book_id, user_id) VALUES (?, ?)",
                (book_id, current_user["id"])
            )
            message = "已收藏"
            
        conn.commit()
        return MessageResponse(message=message)

@router.get("/books/{book_id}/is-favorite", response_model=bool)
async def check_is_favorite(
    book_id: int,
    current_user: dict = Depends(get_current_user)
):
    """检查是否已收藏"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM favorites WHERE book_id = ? AND user_id = ?",
            (book_id, current_user["id"])
        )
        return bool(cursor.fetchone())

@router.get("/users/favorites", response_model=List[FavoriteResponse])
async def get_my_favorites(current_user: dict = Depends(get_current_user)):
    """获取我的收藏列表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                f.id, f.book_id, f.created_at,
                b.title as book_title,
                b.author as book_author,
                b.cover as book_cover
            FROM favorites f
            JOIN books b ON f.book_id = b.id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
        ''', (current_user["id"],))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
