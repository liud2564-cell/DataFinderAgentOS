import json
import tornado.web

from app.controllers.base import BaseHandler
from app.models.user import UserRepository


class ProfileApiHandler(BaseHandler):
    """获取当前登录用户个人信息"""
    @tornado.web.authenticated
    def get(self):
        username = self.current_user
        user_row = UserRepository.get_user_by_username(username)
        if not user_row:
            self.write({"success": False, "message": "用户不存在"})
            return
        user = dict(user_row)
        # 去除敏感字段
        user.pop("password_hash", None)
        user.pop("salt", None)
        self.write({"success": True, "data": user})


class ChangePasswordApiHandler(BaseHandler):
    """修改当前登录用户密码"""
    @tornado.web.authenticated
    def post(self):
        username = self.current_user
        old_password = self.get_body_argument("old_password", "")
        new_password = self.get_body_argument("new_password", "")

        if not old_password or not new_password:
            self.write({"success": False, "message": "旧密码和新密码不能为空"})
            return
        if len(new_password) < 6:
            self.write({"success": False, "message": "新密码长度不能少于6位"})
            return
        if old_password == new_password:
            self.write({"success": False, "message": "新密码不能与旧密码相同"})
            return

        # 验证旧密码
        if not UserRepository.verify_user(username, old_password):
            self.write({"success": False, "message": "旧密码错误"})
            return

        # 更新密码
        user_row = UserRepository.get_user_by_username(username)
        if not user_row:
            self.write({"success": False, "message": "用户不存在"})
            return

        UserRepository.update_password(user_row["id"], new_password)
        self.write({"success": True, "message": "密码修改成功"})
