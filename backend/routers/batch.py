"""
批量操作 API 路由 (Excel 导入/导出)
需要安装: pandas, openpyxl, python-multipart
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import pandas as pd
import io
from datetime import datetime
import tempfile
import os
import shutil

from database import get_db, get_password_hash
from auth import require_admin_or_super
from models import MessageResponse, BookCreate, UserCreate

router = APIRouter(prefix="/api/batch", tags=["batch"])

# ==================== 导出功能 ====================

@router.get("/export/books")
async def export_books(current_user: dict = Depends(require_admin_or_super)):
    """导出所有图书"""
    with get_db() as conn:
        # 使用 pandas 直接读取 SQL
        df = pd.read_sql_query("SELECT * FROM books WHERE status != 'deleted'", conn)
        
        # 格式化日期
        # df['created_at'] = pd.to_datetime(df['created_at'])
        
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        temp_file.close()
        
        df.to_excel(temp_file.name, index=False)
        
        filename = f"books_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        return FileResponse(
            temp_file.name, 
            filename=filename, 
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            background=None # TODO: cleanup temp file
        )

@router.get("/export/users")
async def export_users(current_user: dict = Depends(require_admin_or_super)):
    """导出所有用户"""
    with get_db() as conn:
        df = pd.read_sql_query("SELECT id, student_id, name, role, created_at FROM users", conn)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        temp_file.close()
        
        df.to_excel(temp_file.name, index=False)
        
        filename = f"users_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        return FileResponse(
            temp_file.name, 
            filename=filename, 
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

# ==================== 导入功能 ====================

@router.post("/import/books", response_model=MessageResponse)
async def import_books(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin_or_super)
):
    """批量导入图书 (Excel)"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="请上传 Excel 文件")
    
    try:
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
        
        # 检查必要的列
        required_cols = ['title', 'author', 'isbn', 'category']
        for col in required_cols:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"缺少列: {col}")
        
        success_count = 0
        error_count = 0
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                try:
                    # 检查 ISBN 是否存在
                    isbn = str(row['isbn'])
                    cursor.execute("SELECT id FROM books WHERE isbn = ?", (isbn,))
                    if cursor.fetchone():
                        error_count += 1 # Skip existing
                        continue
                    
                    title = row['title']
                    author = row['author']
                    category = row.get('category', '其它')
                    total = int(row.get('total_count', 1))
                    
                    cursor.execute('''
                        INSERT INTO books (title, author, isbn, category, total_count, available_count)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (title, author, isbn, category, total, total))
                    
                    success_count += 1
                except Exception as e:
                    print(f"Row error: {e}")
                    error_count += 1
            
            conn.commit()
            
        return MessageResponse(
            message=f"导入完成: 成功 {success_count} 本, 失败/跳过 {error_count} 本"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件处理失败: {str(e)}")

@router.post("/import/users", response_model=MessageResponse)
async def import_users(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin_or_super)
):
    """批量导入用户 (Excel)"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="请上传 Excel 文件")
    
    try:
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
        
        # Check columns
        if 'student_id' not in df.columns or 'name' not in df.columns:
             raise HTTPException(status_code=400, detail="缺少列: student_id, name")
             
        success_count = 0
        error_count = 0
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                try:
                    student_id = str(row['student_id'])
                    
                    cursor.execute("SELECT id FROM users WHERE student_id = ?", (student_id,))
                    if cursor.fetchone():
                        error_count += 1
                        continue
                        
                    name = row['name']
                    password = str(row.get('password', '12345678')) # Default password
                    pwd_hash = get_password_hash(password)
                    
                    cursor.execute('''
                        INSERT INTO users (student_id, password_hash, name, role)
                        VALUES (?, ?, ?, 'student')
                    ''', (student_id, pwd_hash, name))
                    
                    success_count += 1
                except Exception:
                    error_count += 1
            
            conn.commit()
            
        return MessageResponse(
            message=f"导入完成: 成功 {success_count} 人, 失败/跳过 {error_count} 人"
        )
        
    except Exception as e:
         raise HTTPException(status_code=400, detail=f"文件处理失败: {str(e)}")
