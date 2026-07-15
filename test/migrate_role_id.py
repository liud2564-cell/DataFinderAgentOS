import sqlite3
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
db_path = os.path.join(project_root, "database", "finderos.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查users表是否有role_id字段
cursor.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cursor.fetchall()]

if 'role_id' not in columns:
    print("添加role_id字段到users表...")
    cursor.execute("ALTER TABLE users ADD COLUMN role_id INTEGER DEFAULT 2")
    print("✓ role_id字段已添加，默认值为2（普通用户）")
else:
    print("✓ role_id字段已存在")

conn.commit()
conn.close()
print("\n数据库迁移完成！")
