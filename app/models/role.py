import sqlite3
from app.models.db import get_connection

class RoleRepository:
    """角色数据访问类"""
    
    @staticmethod
    def get_all_roles():
        """获取所有角色"""
        with get_connection() as conn:
            return conn.execute("SELECT * FROM roles ORDER BY id").fetchall()
    
    @staticmethod
    def get_role_by_id(role_id):
        """根据ID获取角色"""
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM roles WHERE id=?", (role_id,)).fetchone()
            return row
    
    @staticmethod
    def get_role_by_code(code):
        """根据编码获取角色"""
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM roles WHERE code=?", (code,)).fetchone()
            return row
    
    @staticmethod
    def create_role(name, code, description="", status=1):
        """创建角色"""
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO roles (name, code, description, status) VALUES (?, ?, ?, ?)",
                    (name, code, description, status)
                )
                return True
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    def update_role(role_id, name, code, description, status):
        """更新角色"""
        with get_connection() as conn:
            conn.execute(
                "UPDATE roles SET name=?, code=?, description=?, status=?, updated_at=datetime('now', 'localtime') WHERE id=?",
                (name, code, description, status, role_id)
            )
            return True
    
    @staticmethod
    def delete_role(role_id):
        """删除角色"""
        with get_connection() as conn:
            conn.execute("DELETE FROM roles WHERE id=?", (role_id,))
            return True
    
    @staticmethod
    def disable_role(role_id):
        """禁用角色"""
        with get_connection() as conn:
            conn.execute(
                "UPDATE roles SET status=0, updated_at=datetime('now', 'localtime') WHERE id=?",
                (role_id,)
            )
            return True
    
    @staticmethod
    def enable_role(role_id):
        """启用角色"""
        with get_connection() as conn:
            conn.execute(
                "UPDATE roles SET status=1, updated_at=datetime('now', 'localtime') WHERE id=?",
                (role_id,)
            )
            return True
