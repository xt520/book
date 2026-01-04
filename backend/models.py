"""
Pydantic 数据模型定义
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ==================== 用户相关模型 ====================

class LoginRequest(BaseModel):
    student_id: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict
    first_login: bool

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UserInfo(BaseModel):
    id: int
    student_id: str
    name: str
    role: str

class UserCreate(BaseModel):
    student_id: str
    name: str
    password: Optional[str] = "12345678"  # 默认密码

# ==================== 图书相关模型 ====================

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    category: str = "其它"
    cover: Optional[str] = None
    total_count: int = 1

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    category: Optional[str] = None
    cover: Optional[str] = None
    total_count: Optional[int] = None

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str]
    category: str
    cover: Optional[str]
    total_count: int
    available_count: int
    status: str
    created_at: Optional[str] = None

# ==================== 借阅相关模型 ====================

class BorrowRequest(BaseModel):
    days: int = 30  # 借阅天数，默认30天

class BorrowRecordResponse(BaseModel):
    id: int
    book_id: int
    book_title: str
    book_author: str
    user_id: int
    user_name: str
    student_id: str
    borrow_date: str
    due_date: str
    return_date: Optional[str]
    status: str

# ==================== 通用响应模型 ====================

class MessageResponse(BaseModel):
    message: str
    success: bool = True
