from app.models.db import get_connection

class RoleFunctionRepository:
    """角色-功能关联数据访问类"""

    @staticmethod
    def get_functions_by_role(role_id):
        """获取角色已分配的功能ID列表"""
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT func_id FROM role_functions WHERE role_id=?",
                (role_id,)
            ).fetchall()
            return [row["func_id"] for row in rows]

    @staticmethod
    def set_role_functions(role_id, func_ids):
        """设置角色的功能权限（先删后插）"""
        with get_connection() as conn:
            conn.execute("DELETE FROM role_functions WHERE role_id=?", (role_id,))
            for func_id in func_ids:
                conn.execute(
                    "INSERT OR IGNORE INTO role_functions (role_id, func_id) VALUES (?, ?)",
                    (role_id, func_id)
                )
            return True

    @staticmethod
    def delete_by_role(role_id):
        """删除角色的所有功能关联"""
        with get_connection() as conn:
            conn.execute("DELETE FROM role_functions WHERE role_id=?", (role_id,))
            return True
