import hashlib
import secrets
import sqlite3

from app.models.db import get_connection

def _hash_password(password: str, salt: bytes) -> str:
    # 将明文相同+salt 计算为稳定的hash
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return dk.hex()

class UserRepository:
    # 用户数据访问类（面向Controller提供方法）
    @staticmethod  # 修饰可以保持方法的简洁，目的是不引入依赖注入，不维护链接池
    def create_user(username: str, password: str, role_id: int = 2) -> bool:
        salt = secrets.token_bytes(16)
        password_hash = _hash_password(password, salt)
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, salt, role_id) VALUES (?, ?, ?, ?)",
                    (username, password_hash, salt.hex(), role_id)
                )
                return True
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    def get_user_by_username(username: str):
        with get_connection() as conn:
            return conn.execute(
                "SELECT u.*, r.name as role_name, r.code as role_code FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE u.username=?",
                (username,)
            ).fetchone()
    
    @staticmethod
    def get_user_by_id(user_id: int):
        with get_connection() as conn:
            row = conn.execute(
                "SELECT u.*, r.name as role_name, r.code as role_code FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE u.id=?",
                (user_id,)
            ).fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_all_users(page=1, page_size=20, search=None, role_id=None, status=None):
        """获取用户列表（分页）"""
        # 转换空字符串为None
        if search == '': search = None
        if role_id == '' or role_id is None: role_id = None
        else: role_id = int(role_id)
        if status == '' or status is None: status = None
        else: status = int(status)
        
        with get_connection() as conn:
            # 获取总数
            count_query = "SELECT COUNT(*) as total FROM users u WHERE 1=1"
            count_params = []
            
            if search:
                count_query += " AND u.username LIKE ?"
                count_params.append(f"%{search}%")
            
            if role_id:
                count_query += " AND u.role_id = ?"
                count_params.append(role_id)
            
            if status is not None:
                count_query += " AND u.status = ?"
                count_params.append(status)
            
            total = conn.execute(count_query, count_params).fetchone()["total"]
            
            # 获取数据
            query = "SELECT u.*, r.name as role_name, r.code as role_code FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE 1=1"
            params = []
            
            if search:
                query += " AND u.username LIKE ?"
                params.append(f"%{search}%")
            
            if role_id:
                query += " AND u.role_id = ?"
                params.append(role_id)
            
            if status is not None:
                query += " AND u.status = ?"
                params.append(status)
            
            query += " ORDER BY u.id DESC LIMIT ? OFFSET ?"
            params.extend([page_size, (page - 1) * page_size])
            
            rows = conn.execute(query, params).fetchall()
            return {
                "data": [dict(row) for row in rows],
                "total": total,
                "page": page,
                "page_size": page_size
            }
    
    @staticmethod
    def verify_user(username:str, password:str) -> bool:
        row = UserRepository.get_user_by_username(username)
        # 先看用户名是否存在，如果用户名不存在，则后面验证没有必要
        if not row:
            return False
        salt = bytes.fromhex(row["salt"])
        return _hash_password(password, salt) == row["password_hash"]
    
    @staticmethod
    def update_user(user_id: int, **kwargs):
        allowed_fields = {"username", "role_id", "status"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k}=? " for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        
        with get_connection() as conn:
            conn.execute(
                f"UPDATE users SET {set_clause.strip()} WHERE id=?",
                values
            )
            return True
    
    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        """修改用户密码"""
        salt = secrets.token_bytes(16)
        password_hash = _hash_password(new_password, salt)
        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET password_hash=?, salt=? WHERE id=?",
                (password_hash, salt.hex(), user_id)
            )
            return True

    @staticmethod
    def delete_user(user_id: int) -> bool:
        with get_connection() as conn:
            conn.execute("DELETE FROM users WHERE id=?", (user_id,))
            return True
