"""
数据库模块 - SQLite3 连接和表结构初始化
"""
import sqlite3
import hashlib
from pathlib import Path
from contextlib import contextmanager

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent / "library.db"

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return get_password_hash(plain_password) == hashed_password

@contextmanager
def get_db():
    """获取数据库连接的上下文管理器"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """初始化数据库表结构"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'student',
                first_login INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 图书表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                category TEXT NOT NULL DEFAULT '其它',
                cover TEXT,
                cover_status INTEGER DEFAULT 1,
                total_count INTEGER DEFAULT 1,
                available_count INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 检查并添加 cover_status 列（数据库迁移）
        cursor.execute("PRAGMA table_info(books)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'cover_status' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN cover_status INTEGER DEFAULT 1")
            # 根据现有封面路径设置状态：本地路径设为0，其他设为1
            cursor.execute("""
                UPDATE books SET cover_status = CASE 
                    WHEN cover LIKE '/api/covers/%' THEN 0 
                    WHEN cover IS NULL OR cover = '' THEN 2
                    ELSE 1 
                END
            """)
        
        # 借阅记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrow_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP,
                return_date TIMESTAMP,
                status TEXT DEFAULT 'borrowed',
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        
        # 检查并创建管理员账号
        cursor.execute("SELECT id FROM users WHERE student_id = 'admin'")
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (student_id, password_hash, name, role, first_login)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', get_password_hash('admin123'), '系统管理员', 'admin', 0))
            conn.commit()
        
        # 创建测试学生账号
        test_students = [
            ('20210001', '张三'),
            ('20210002', '李四'),
            ('20210003', '王五'),
            ('20210004', '赵六'),
            ('20210005', '钱七'),
        ]
        
        for student_id, name in test_students:
            cursor.execute("SELECT id FROM users WHERE student_id = ?", (student_id,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO users (student_id, password_hash, name, role, first_login)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, get_password_hash('12345678'), name, 'student', 1))
        
        # 创建示例图书
        sample_books = [
            ('Python编程：从入门到实践', 'Eric Matthes', '9787115546081', '编程'),
            ('深入理解计算机系统', 'Randal E. Bryant', '9787111544937', '编程'),
            ('算法导论', 'Thomas H. Cormen', '9787111407010', '编程'),
            ('百年孤独', '加西亚·马尔克斯', '9787544291170', '文学'),
            ('三体', '刘慈欣', '9787536692930', '科幻'),
            ('人类简史', '尤瓦尔·赫拉利', '9787508647357', '科技'),
            ('设计心理学', '唐纳德·诺曼', '9787508648330', '艺术'),
        ]
        
        for title, author, isbn, category in sample_books:
            cursor.execute("SELECT id FROM books WHERE isbn = ?", (isbn,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO books (title, author, isbn, category, total_count, available_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (title, author, isbn, category, 3, 3))
        
        conn.commit()
        print("数据库初始化完成")

# 模块加载时自动初始化数据库
init_db()
