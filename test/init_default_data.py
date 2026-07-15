import sqlite3
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
db_path = os.path.join(project_root, "database", "finderos.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查roles表是否有数据
cursor.execute("SELECT COUNT(*) FROM roles")
role_count = cursor.fetchone()[0]
print(f"Roles表记录数: {role_count}")

if role_count == 0:
    print("插入默认角色...")
    cursor.execute("INSERT INTO roles (name, code, description, status) VALUES (?, ?, ?, ?)", 
                   ("系统管理员", "admin", "系统管理员角色", 1))
    cursor.execute("INSERT INTO roles (name, code, description, status) VALUES (?, ?, ?, ?)", 
                   ("普通用户", "user", "普通用户角色", 1))
    print("✓ 默认角色已插入")
else:
    print("✓ 角色表已有数据")

# 检查functions表是否有数据
cursor.execute("SELECT COUNT(*) FROM functions")
func_count = cursor.fetchone()[0]
print(f"\nFunctions表记录数: {func_count}")

if func_count == 0:
    print("插入默认功能...")
    default_funcs = [
        ("用户管理", "user_mgmt", "layui-icon-user", "/admin/user-management", 1, 0, 1),
        ("角色管理", "role_mgmt", "layui-icon-group", "/admin/role-management", 2, 0, 1),
        ("功能管理", "func_mgmt", "layui-icon-component", "/admin/function-management", 3, 0, 1),
        ("菜单管理", "menu_mgmt", "layui-icon-auz", "/admin/menu-management", 4, 0, 1),
    ]
    for func in default_funcs:
        cursor.execute(
            "INSERT INTO functions (name, code, icon, route, sort_order, parent_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            func
        )
    print("✓ 默认功能已插入")
else:
    print("✓ 功能表已有数据")

conn.commit()

# 检查menus表是否有数据
cursor.execute("SELECT COUNT(*) FROM menus")
menu_count = cursor.fetchone()[0]
print(f"\nMenus表记录数: {menu_count}")

if menu_count == 0:
    print("插入默认菜单（系统管理员关联所有功能）...")
    # 获取系统管理员角色ID和功能ID
    cursor.execute("SELECT id FROM roles WHERE code='admin'")
    admin_role = cursor.fetchone()
    if admin_role:
        admin_role_id = admin_role[0]
        cursor.execute("SELECT id FROM functions ORDER BY sort_order")
        all_funcs = cursor.fetchall()
        for i, func in enumerate(all_funcs):
            func_id = func[0]
            cursor.execute(
                "INSERT INTO menus (role_id, func_id, sort_order) VALUES (?, ?, ?)",
                (admin_role_id, func_id, i + 1)
            )
        print(f"✓ 已为系统管理员(role_id={admin_role_id})创建 {len(all_funcs)} 个菜单")
    else:
        print("⚠ 未找到系统管理员角色，跳过菜单创建")
else:
    print("✓ 菜单表已有数据")

conn.commit()
conn.close()
print("\n数据库初始化完成！")
