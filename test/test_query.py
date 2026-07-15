import sqlite3
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
db_path = os.path.join(project_root, "database", "finderos.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 测试查询
query = """
SELECT u.*, r.name as role_name, r.code as role_code 
FROM users u 
LEFT JOIN roles r ON u.role_id = r.id 
WHERE 1=1 
ORDER BY u.id DESC 
LIMIT 20 OFFSET 0
"""

print("=== 执行查询 ===")
print(query)
cursor.execute(query)
rows = cursor.fetchall()
print(f"\n返回 {len(rows)} 行数据:")
for row in rows:
    print(row)

# 测试计数
count_query = "SELECT COUNT(*) as total FROM users u WHERE 1=1"
cursor.execute(count_query)
total = cursor.fetchone()[0]
print(f"\n总记录数: {total}")

conn.close()
