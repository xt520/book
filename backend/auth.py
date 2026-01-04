"""
JWT 认证模块
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .database import get_db, get_password_hash, verify_password

# JWT 配置
SECRET_KEY = "library-management-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """解码 JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 已过期"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Token"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """获取当前登录用户"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证信息"
        )
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, student_id, name, role, first_login FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        return {
            "id": row["id"],
            "student_id": row["student_id"],
            "name": row["name"],
            "role": row["role"],
            "first_login": bool(row["first_login"])
        }

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """要求管理员权限"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

def authenticate_user(student_id: str, password: str) -> Optional[dict]:
    """验证用户登录"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, student_id, password_hash, name, role, first_login FROM users WHERE student_id = ?",
            (student_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        if not verify_password(password, row["password_hash"]):
            return None
        
        return {
            "id": row["id"],
            "student_id": row["student_id"],
            "name": row["name"],
            "role": row["role"],
            "first_login": bool(row["first_login"])
        }

def change_user_password(user_id: int, old_password: str, new_password: str) -> bool:
    """修改用户密码"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row or not verify_password(old_password, row["password_hash"]):
            return False
        
        new_hash = get_password_hash(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = ?, first_login = 0 WHERE id = ?",
            (new_hash, user_id)
        )
        conn.commit()
        return True
