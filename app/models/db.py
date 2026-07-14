import os
import sqlite3

def project_root():
    # 当前项目的 ../DataFinderAgentOS/
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

DB_PATH = os.path.join(project_root(), "database", "finderos.db")

def get_connection():
    # 获得一个数据库的连接，用于操作数据库完成事务和数据操作
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        # 用户表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role_id INTEGER NOT NULL DEFAULT 2,
                status INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (role_id) REFERENCES roles(id)
            )
            """
        )
        
        # 角色表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                code TEXT NOT NULL UNIQUE,
                description TEXT,
                status INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        
        # 功能表（一级+二级）
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS functions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER DEFAULT 0,
                name TEXT NOT NULL,
                code TEXT NOT NULL,
                icon TEXT,
                route TEXT,
                sort_order INTEGER NOT NULL DEFAULT 0,
                status INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (parent_id) REFERENCES functions(id)
            )
            """
        )
        
        # 菜单表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS menus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER NOT NULL,
                func_id INTEGER NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0,
                status INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (role_id) REFERENCES roles(id),
                FOREIGN KEY (func_id) REFERENCES functions(id),
                UNIQUE(role_id, func_id)
            )
            """
        )
        
        # 角色-功能关联表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS role_functions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER NOT NULL,
                func_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (role_id) REFERENCES roles(id),
                FOREIGN KEY (func_id) REFERENCES functions(id),
                UNIQUE(role_id, func_id)
            )
            """
        )
        
        # 插入默认角色（如果不存在）
        cursor = conn.execute("SELECT id FROM roles WHERE code = 'admin'")
        if not cursor.fetchone():
            conn.execute(
                "INSERT INTO roles (name, code, description, status) VALUES (?, ?, ?, ?)",
                ("系统管理员", "admin", "拥有系统所有权限", 1)
            )
            conn.execute(
                "INSERT INTO roles (name, code, description, status) VALUES (?, ?, ?, ?)",
                ("普通用户", "user", "只能登录前台用户侧", 1)
            )
        
        # 插入默认功能（如果不存在）
        func_count = conn.execute("SELECT COUNT(*) FROM functions").fetchone()[0]
        if func_count == 0:
            # 一级功能
            conn.execute(
                "INSERT INTO functions (name, code, icon, route, sort_order, parent_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("控制台", "dashboard", "layui-icon-home", "/admin/index", 1, 0, 1)
            )
            conn.execute(
                "INSERT INTO functions (name, code, icon, route, sort_order, parent_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("管理系统", "management", "layui-icon-set", "", 2, 0, 1)
            )
            mgmt_id = conn.execute("SELECT id FROM functions WHERE code='management'").fetchone()["id"]
            # 二级功能（管理系统下）
            conn.execute(
                "INSERT INTO functions (name, code, icon, route, sort_order, parent_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("用户管理", "user_management", "layui-icon-user", "/admin/user-management", 1, mgmt_id, 1)
            )
            conn.execute(
                "INSERT INTO functions (name, code, icon, route, sort_order, parent_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("角色管理", "role_management", "layui-icon-group", "/admin/role-management", 2, mgmt_id, 1)
            )
            conn.execute(
                "INSERT INTO functions (name, code, icon, route, sort_order, parent_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("功能管理", "func_management", "layui-icon-component", "/admin/function-management", 3, mgmt_id, 1)
            )
            conn.execute(
                "INSERT INTO functions (name, code, icon, route, sort_order, parent_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("菜单管理", "menu_management", "layui-icon-auz", "/admin/menu-management", 4, mgmt_id, 1)
            )
        
        conn.commit()
