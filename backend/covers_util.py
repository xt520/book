"""
封面图片下载和存储工具
"""
import os
import hashlib
import httpx
import asyncio
from pathlib import Path

# 封面存储目录
COVERS_DIR = Path(__file__).parent / "covers"
COVERS_DIR.mkdir(exist_ok=True)

# 封面状态常量
COVER_STATUS_SUCCESS = 0  # 存储成功
COVER_STATUS_PENDING = 1  # 未存储，待下载
COVER_STATUS_FAILED = 2   # 无法获取


async def download_cover(url: str, isbn: str = None) -> tuple[str, int]:
    """
    下载封面图片并保存到本地
    返回: (封面路径, 状态码)
        - 状态码 0: 存储成功
        - 状态码 1: 未存储（输入无效）
        - 状态码 2: 无法获取（下载失败）
    """
    if not url:
        return ("", COVER_STATUS_FAILED)
    
    # 已经是本地路径
    if url.startswith('/api/covers/'):
        return (url, COVER_STATUS_SUCCESS)
    
    # 不是有效URL
    if not url.startswith(('http://', 'https://')):
        return (url, COVER_STATUS_PENDING)
    
    # 生成文件名（基于URL的哈希或ISBN）
    if isbn:
        filename = f"{isbn}.jpg"
    else:
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        filename = f"cover_{url_hash}.jpg"
    
    filepath = COVERS_DIR / filename
    
    # 如果文件已存在，直接返回
    if filepath.exists():
        return (f"/api/covers/{filename}", COVER_STATUS_SUCCESS)
    
    # 尝试下载的URL列表
    urls_to_try = [url]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for try_url in urls_to_try:
            try:
                response = await client.get(try_url, follow_redirects=True)
                
                if response.status_code == 200:
                    content = response.content
                    
                    # 检查是否为有效图片（不是1x1像素的占位图）
                    # openlibrary 返回 1x1 像素的透明图作为"不存在"标记
                    if len(content) < 1000:
                        print(f"封面图片太小 ({len(content)} bytes)，跳过: {try_url}")
                        continue
                    
                    # 检查是否为有效图片格式
                    content_type = response.headers.get('content-type', '')
                    is_valid_image = (
                        'image' in content_type or 
                        content[:3] == b'\xff\xd8\xff' or  # JPEG
                        content[:8] == b'\x89PNG\r\n\x1a\n'  # PNG
                    )
                    
                    if is_valid_image:
                        # 保存文件
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        return (f"/api/covers/{filename}", COVER_STATUS_SUCCESS)
                        
            except Exception as e:
                print(f"下载封面出错: {try_url}, 错误: {e}")
                continue
    
    # 所有URL都失败
    print(f"无法获取封面: {url}")
    return (url, COVER_STATUS_FAILED)


def get_cover_path(filename: str) -> Path:
    """获取封面文件的完整路径"""
    return COVERS_DIR / filename


async def download_pending_covers():
    """
    下载所有状态为1（待下载）的封面
    应在应用启动时调用
    """
    from .database import get_db
    
    print("检查待下载的封面...")
    
    with get_db() as conn:
        cursor = conn.cursor()
        # 查询所有 cover_status=1 且有原始封面URL的书籍
        cursor.execute("""
            SELECT id, title, cover, isbn FROM books 
            WHERE cover_status = 1 AND cover IS NOT NULL AND cover != ''
            AND status = 'active'
        """)
        pending_books = cursor.fetchall()
    
    if not pending_books:
        print("没有待下载的封面")
        return
    
    print(f"发现 {len(pending_books)} 本书需要下载封面")
    
    for book in pending_books:
        book_id = book['id']
        title = book['title']
        cover_url = book['cover']
        isbn = book['isbn']
        
        print(f"正在下载封面: {title}...")
        
        local_cover, status = await download_cover(cover_url, isbn)
        
        # 更新数据库
        with get_db() as conn:
            cursor = conn.cursor()
            if status == COVER_STATUS_SUCCESS:
                cursor.execute(
                    "UPDATE books SET cover = ?, cover_status = 0 WHERE id = ?",
                    (local_cover, book_id)
                )
                print(f"  ✓ 成功: {title}")
            else:
                cursor.execute(
                    "UPDATE books SET cover_status = 2 WHERE id = ?",
                    (book_id,)
                )
                print(f"  ✗ 失败: {title}")
            conn.commit()
    
    print("封面下载队列处理完成")
