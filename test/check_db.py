import sqlite3
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
db_path = os.path.join(project_root, "database", "finderos.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查users表结构
print("=== users表结构 ===")
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(col)

# 查询所有用户
print("\n=== 所有用户数据 ===")
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
for user in users:
    print(user)

# 检查roles表
print("\n=== roles表数据 ===")
cursor.execute("SELECT * FROM roles")
roles = cursor.fetchall()
for role in roles:
    print(role)

conn.close()
