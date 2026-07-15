import sqlite3
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
db_path = os.path.join(project_root, "database", "finderos.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查users表是否有status字段
cursor.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cursor.fetchall()]

if 'status' not in columns:
    print("添加status字段到users表...")
    cursor.execute("ALTER TABLE users ADD COLUMN status INTEGER DEFAULT 1")
    print("✓ status字段已添加")
else:
    print("✓ status字段已存在")

# 检查roles表是否有status字段
cursor.execute("PRAGMA table_info(roles)")
columns = [row[1] for row in cursor.fetchall()]

if 'status' not in columns:
    print("添加status字段到roles表...")
    cursor.execute("ALTER TABLE roles ADD COLUMN status INTEGER DEFAULT 1")
    print("✓ status字段已添加")
else:
    print("✓ status字段已存在")

# 检查functions表是否有status字段
cursor.execute("PRAGMA table_info(functions)")
columns = [row[1] for row in cursor.fetchall()]

if 'status' not in columns:
    print("添加status字段到functions表...")
    cursor.execute("ALTER TABLE functions ADD COLUMN status INTEGER DEFAULT 1")
    print("✓ status字段已添加")
else:
    print("✓ status字段已存在")

# 检查menus表是否有status字段
cursor.execute("PRAGMA table_info(menus)")
columns = [row[1] for row in cursor.fetchall()]

if 'status' not in columns:
    print("添加status字段到menus表...")
    cursor.execute("ALTER TABLE menus ADD COLUMN status INTEGER DEFAULT 1")
    print("✓ status字段已添加")
else:
    print("✓ status字段已存在")

conn.commit()
conn.close()
print("\n数据库迁移完成！")
