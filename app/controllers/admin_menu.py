import json
import tornado.web

from app.controllers.base import BaseHandler
from app.models.menu import MenuRepository
from app.models.role import RoleRepository
from app.models.function import FunctionRepository

class MenuManagementHandler(BaseHandler):
    """菜单管理页面"""
    @tornado.web.authenticated
    def get(self):
        roles = RoleRepository.get_all_roles()
        self.render("admin/menu_management.html", title="菜单管理", username=self.current_user, roles=[dict(r) for r in roles])

class MenuListApiHandler(BaseHandler):
    """菜单列表API"""
    @tornado.web.authenticated
    def get(self):
        role_id = self.get_argument("role_id", "")
        
        if role_id:
            menus = MenuRepository.get_menus_by_role(int(role_id))
        else:
            menus = MenuRepository.get_all_menus()
        
        self.write(json.dumps({
            "data": [dict(menu) for menu in menus],
            "total": len(menus)
        }))

class MenuCreateApiHandler(BaseHandler):
    """创建菜单API"""
    @tornado.web.authenticated
    def post(self):
        role_id = int(self.get_argument("role_id", 0))
        func_id = int(self.get_argument("func_id", 0))
        sort_order = int(self.get_argument("sort_order", 0))
        
        if MenuRepository.create_menu(role_id, func_id, sort_order):
            self.write(json.dumps({"success": True, "message": "菜单创建成功"}))
        else:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "菜单创建失败"}))

class MenuUpdateApiHandler(BaseHandler):
    """更新菜单API"""
    @tornado.web.authenticated
    def post(self):
        menu_id = self.get_argument("menu_id", "")
        sort_order = int(self.get_argument("sort_order", 0))
        
        if MenuRepository.update_menu(int(menu_id), sort_order):
            self.write(json.dumps({"success": True, "message": "菜单排序更新成功"}))
        else:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "更新失败"}))

class MenuDeleteApiHandler(BaseHandler):
    """删除菜单API"""
    @tornado.web.authenticated
    def post(self):
        menu_id = self.get_argument("menu_id", "")
        
        if MenuRepository.delete_menu(int(menu_id)):
            self.write(json.dumps({"success": True, "message": "菜单删除成功"}))
        else:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "删除失败"}))

class MenuPreviewApiHandler(BaseHandler):
    """菜单预览API"""
    @tornado.web.authenticated
    def get(self):
        role_id = self.get_argument("role_id", "")
        
        if not role_id:
            self.set_status(400)
            self.write(json.dumps({"success": False, "message": "请选择角色"}))
            return
        
        menus = MenuRepository.get_menus_by_role(int(role_id))
        self.write(json.dumps({
            "success": True,
            "data": [dict(menu) for menu in menus]
        }))
