import json
import tornado.web

from app.controllers.base import BaseHandler
from app.models.user import UserRepository

class UserManagementHandler(BaseHandler):
    """用户管理页面"""
    @tornado.web.authenticated
    def get(self):
        self.render("admin/user_management.html", title="用户管理", username=self.current_user)

class UserListApiHandler(BaseHandler):
    """用户列表API"""
    @tornado.web.authenticated
    def get(self):
        page = int(self.get_argument("page", 1))
        page_size = int(self.get_argument("page_size", 20))
        search = self.get_argument("search", "")
        role_id = self.get_argument("role_id", "")
        status = self.get_argument("status", "")
        
        # 转换空字符串为None
        if not search: search = None
        if not role_id: role_id = None
        else: role_id = int(role_id)
        if not status: status = None
        else: status = int(status)
        
        result = UserRepository.get_all_users(page, page_size, search, role_id, status)
        self.write(json.dumps(result, ensure_ascii=False))

class UserGetApiHandler(BaseHandler):
    """获取用户详情API"""
    @tornado.web.authenticated
    def get(self):
        user_id = self.get_argument("user_id", "")
        if not user_id:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "用户ID不能为空"}))
            return
        
        user = UserRepository.get_user_by_id(int(user_id))
        if user:
            self.write(json.dumps({"success": True, "data": user}))
        else:
            self.set_status(404)
            self.write(json.dumps({"success": False, "message": "用户不存在"}))

class UserCreateApiHandler(BaseHandler):
    """创建用户API"""
    @tornado.web.authenticated
    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        role_id = int(self.get_argument("role_id", 2))
        
        if not username or not password:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "用户名和密码不能为空"}))
            return
        
        if UserRepository.create_user(username, password, role_id):
            self.write(json.dumps({"success": True, "message": "用户创建成功"}))
        else:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "用户名已存在"}))

class UserUpdateApiHandler(BaseHandler):
    """更新用户API"""
    @tornado.web.authenticated
    def post(self):
        user_id = self.get_argument("user_id", "")
        username = self.get_argument("username", "")
        role_id = self.get_argument("role_id", "")
        status = self.get_argument("status", "")
        
        # 超级管理员不允许禁用自己
        if username == "admin" and status == "0":
            self.set_status(403)
            self.write(json.dumps({"success": False, "message": "超级管理员不允许禁用"}))
            return
        
        updates = {}
        if username:
            updates["username"] = username
        if role_id:
            updates["role_id"] = int(role_id)
        if status:
            updates["status"] = int(status)
        
        if UserRepository.update_user(int(user_id), **updates):
            self.write(json.dumps({"success": True, "message": "用户更新成功"}))
        else:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "更新失败"}))

class UserDeleteApiHandler(BaseHandler):
    """删除用户API"""
    @tornado.web.authenticated
    def post(self):
        user_id = self.get_argument("user_id", "")
        
        # 超级管理员不允许删除
        user = UserRepository.get_user_by_id(int(user_id))
        if user and user.get("username") == "admin":
            self.set_status(403)
            self.write(json.dumps({"success": False, "message": "超级管理员不允许删除"}))
            return
        
        if UserRepository.delete_user(int(user_id)):
            self.write(json.dumps({"success": True, "message": "用户删除成功"}))
        else:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "删除失败"}))
