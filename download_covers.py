"""
下载现有图书的封面到本地
"""
import sqlite3
import asyncio
import httpx
import hashlib
from pathlib import Path

# 封面存储目录
COVERS_DIR = Path(__file__).parent / "backend" / "covers"
COVERS_DIR.mkdir(exist_ok=True)

async def download_cover(url: str, isbn: str = None) -> str:
    """下载封面图片"""
    if not url or not url.startswith(('http://', 'https://')):
        return url
    
    try:
        if isbn:
            filename = f"{isbn}.jpg"
        else:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            filename = f"cover_{url_hash}.jpg"
        
        filepath = COVERS_DIR / filename
        
        if filepath.exists():
            print(f"  已存在: {filename}")
            return f"/api/covers/{filename}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type or len(response.content) > 1000:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"  ✓ 下载成功: {filename} ({len(response.content)} bytes)")
                    return f"/api/covers/{filename}"
        
        print(f"  ✗ 下载失败: {url}")
        return url
        
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return url

async def migrate_covers():
    """迁移所有封面到本地"""
    conn = sqlite3.connect('d:/tool/book/library.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取所有有外部封面URL的图书
    cursor.execute("""
        SELECT id, title, isbn, cover FROM books 
        WHERE cover LIKE 'http%' AND status = 'active'
    """)
    books = cursor.fetchall()
    
    print(f"\n找到 {len(books)} 本需要下载封面的图书\n")
    
    updated = 0
    for book in books:
        print(f"[{book['id']}] {book['title'][:30]}...")
        local_path = await download_cover(book['cover'], book['isbn'])
        
        if local_path != book['cover']:
            cursor.execute(
                "UPDATE books SET cover = ? WHERE id = ?",
                (local_path, book['id'])
            )
            updated += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 完成! 成功更新 {updated} 本图书的封面路径")

if __name__ == "__main__":
    asyncio.run(migrate_covers())
