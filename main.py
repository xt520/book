"""
图书管理系统 - 主入口
Vue + FastAPI + SQLite3
"""
from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# 导入后端模块
from backend.database import get_db, get_password_hash, verify_password
from backend.auth import create_access_token, authenticate_user, change_user_password, get_current_user
from backend.models import LoginRequest, LoginResponse, ChangePasswordRequest, MessageResponse
from backend.routers import books, borrow, users


# ==================== 生命周期管理 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    from backend.covers_util import download_pending_covers
    
    # 启动时：在后台任务中下载待处理的封面
    asyncio.create_task(download_pending_covers())
    
    yield
    
    # 关闭时（可选）

app = FastAPI(title="图书管理系统", version="2.0.0", lifespan=lifespan)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取当前绝对路径
base_path = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(base_path, "frontend", "dist")

# ==================== 认证 API ====================

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录"""
    user = authenticate_user(request.student_id, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="学号或密码错误")
    
    token = create_access_token({"user_id": user["id"], "role": user["role"]})
    
    return LoginResponse(
        token=token,
        user=user,
        first_login=user["first_login"]
    )

@app.post("/api/auth/change-password", response_model=MessageResponse)
async def change_password(request: ChangePasswordRequest, current_user: dict = None):
    """修改密码"""
    from fastapi import Depends
    from backend.auth import get_current_user
    
    # 这里需要手动获取 current_user，因为可能是首次登录的情况
    # 在实际调用时，前端会传递 token
    pass

@app.post("/api/auth/change-password-with-token")
async def change_password_with_token(
    request: ChangePasswordRequest,
    token: str
):
    """使用 token 修改密码"""
    from backend.auth import decode_token
    
    payload = decode_token(token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="无效的认证信息")
    
    success = change_user_password(user_id, request.old_password, request.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="原密码错误")
    
    return MessageResponse(message="密码修改成功")

# ==================== 注册路由 ====================

app.include_router(books.router)
app.include_router(borrow.router)
app.include_router(users.router)

# ==================== 封面图片服务 ====================

@app.get("/api/covers/{filename}")
async def serve_cover(filename: str):
    """提供本地封面图片"""
    from backend.covers_util import get_cover_path
    
    filepath = get_cover_path(filename)
    if filepath.exists():
        return FileResponse(filepath, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=404, detail="封面不存在")

# ==================== 静态文件服务 ====================

# Vue 前端静态文件
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    @app.get("/")
    async def serve_vue():
        return FileResponse(os.path.join(frontend_path, "index.html"))
    
    # Vue Router 的 history 模式支持
    @app.get("/{full_path:path}")
    async def serve_vue_routes(full_path: str):
        # 如果是 API 请求，不处理
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        
        # 检查是否是静态资源
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # 否则返回 index.html（Vue Router 处理）
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    # 开发模式：提示前端未构建
    @app.get("/")
    async def dev_mode():
        return {
            "message": "前端未构建，请运行 'cd frontend && npm run build'",
            "dev_url": "http://localhost:5173"
        }

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("图书管理系统 v2.0")
    print("=" * 50)
    print("后端 API: http://localhost:18050/docs")
    print("前端地址: http://localhost:18050 (需先构建)")
    print("开发模式: http://localhost:5173 (npm run dev)")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=18050)
