import sqlite3

conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Reset status from 2 (failed) to 1 (pending) for books with http URLs
cursor.execute("UPDATE books SET cover_status = 1 WHERE cover_status = 2 AND cover LIKE 'http%'")
conn.commit()

print(f'已重置 {cursor.rowcount} 本书的封面状态为待下载')

# Show current status
cursor.execute("SELECT cover_status, COUNT(*) FROM books GROUP BY cover_status")
for row in cursor.fetchall():
    status_name = {0: '成功', 1: '待下载', 2: '失败'}
    print(f"  状态 {row[0]} ({status_name.get(row[0], '未知')}): {row[1]} 本")

conn.close()
