import json
import tornado.web

from app.controllers.base import BaseHandler
from app.models.function import FunctionRepository

class FunctionManagementHandler(BaseHandler):
    """功能管理页面"""
    @tornado.web.authenticated
    def get(self):
        self.render("admin/function_management.html", title="功能管理", username=self.current_user)

class FunctionListApiHandler(BaseHandler):
    """功能列表API"""
    @tornado.web.authenticated
    def get(self):
        functions = FunctionRepository.get_all_functions()
        self.write(json.dumps({
            "data": [dict(func) for func in functions],
            "total": len(functions)
        }))

class FunctionGetApiHandler(BaseHandler):
    """获取功能详情API"""
    @tornado.web.authenticated
    def get(self):
        func_id = self.get_argument("func_id", "")
        if not func_id:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "功能ID不能为空"}))
            return
        
        func = FunctionRepository.get_function_by_id(int(func_id))
        if func:
            self.write(json.dumps({"success": True, "data": dict(func)}))
        else:
            self.set_status(404)
            self.write(json.dumps({"success": False, "message": "功能不存在"}))

class FunctionCreateApiHandler(BaseHandler):
    """创建功能API"""
    @tornado.web.authenticated
    def post(self):
        name = self.get_argument("name", "")
        code = self.get_argument("code", "")
        icon = self.get_argument("icon", "")
        route = self.get_argument("route", "")
        sort_order = int(self.get_argument("sort_order", 0))
        parent_id = int(self.get_argument("parent_id", 0))
        status = int(self.get_argument("status", 1))
        
        if not name or not code:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "功能名称和编码不能为空"}))
            return
        
        if FunctionRepository.create_function(name, code, icon, route, sort_order, parent_id, status):
            self.write(json.dumps({"success": True, "message": "功能创建成功"}))
        else:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "功能编码已存在"}))

class FunctionUpdateApiHandler(BaseHandler):
    """更新功能API"""
    @tornado.web.authenticated
    def post(self):
        func_id = self.get_argument("func_id", "")
        name = self.get_argument("name", "")
        code = self.get_argument("code", "")
        icon = self.get_argument("icon", "")
        route = self.get_argument("route", "")
        sort_order = int(self.get_argument("sort_order", 0))
        parent_id = int(self.get_argument("parent_id", 0))
        status = int(self.get_argument("status", 1))
        
        updates = {
            "name": name,
            "code": code,
            "icon": icon,
            "route": route,
            "sort_order": sort_order,
            "parent_id": parent_id,
            "status": status
        }
        
        if FunctionRepository.update_function(int(func_id), **updates):
            self.write(json.dumps({"success": True, "message": "功能更新成功"}))
        else:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "更新失败"}))

class FunctionDeleteApiHandler(BaseHandler):
    """删除功能API"""
    @tornado.web.authenticated
    def post(self):
        func_id = self.get_argument("func_id", "")
        
        if FunctionRepository.delete_function(int(func_id)):
            self.write(json.dumps({"success": True, "message": "功能删除成功"}))
        else:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "删除失败"}))

class FunctionToggleApiHandler(BaseHandler):
    """启用/禁用功能API"""
    @tornado.web.authenticated
    def post(self):
        func_id = self.get_argument("func_id", "")
        action = self.get_argument("action", "")
        
        if action == "enable":
            FunctionRepository.enable_function(int(func_id))
            self.write(json.dumps({"success": True, "message": "功能已启用"}))
        elif action == "disable":
            FunctionRepository.disable_function(int(func_id))
            self.write(json.dumps({"success": True, "message": "功能已禁用"}))
        else:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "无效操作"}))
