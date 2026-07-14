import os
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer

from app.controllers.auth import LoginHandler, LogoutHandler, AdminLoginHandler, AdminLogoutHandler
from app.controllers.home import IndexHandler, AdminIndexHandler
from app.controllers.admin_user import (
    UserManagementHandler,
    UserListApiHandler,
    UserGetApiHandler,
    UserCreateApiHandler,
    UserUpdateApiHandler,
    UserDeleteApiHandler
)
from app.controllers.admin_role import (
    RoleManagementHandler,
    RoleListApiHandler,
    RoleCreateApiHandler,
    RoleUpdateApiHandler,
    RoleDeleteApiHandler,
    RoleFunctionsApiHandler,
    RoleFunctionsSaveApiHandler
)
from app.controllers.admin_function import (
    FunctionManagementHandler,
    FunctionListApiHandler,
    FunctionGetApiHandler,
    FunctionCreateApiHandler,
    FunctionUpdateApiHandler,
    FunctionDeleteApiHandler,
    FunctionToggleApiHandler
)
from app.controllers.admin_menu import (
    MenuManagementHandler,
    MenuListApiHandler,
    MenuCreateApiHandler,
    MenuUpdateApiHandler,
    MenuDeleteApiHandler,
    MenuPreviewApiHandler
)
from app.controllers.admin_profile import (
    ProfileApiHandler,
    ChangePasswordApiHandler
)
from app.models.db import init_db
from app.models.role import RoleRepository
from app.models.function import FunctionRepository
from app.models.menu import MenuRepository

def webapp():
    # 定义一个web应用程序，并配置访问各个模块/页面路由
    # 整个程序的安全配置也需要在此处完成
    base_dir = os.path.dirname(os.path.abspath(__file__))
    settings = dict(
        template_path=os.path.join(base_dir, "app", "templates"),
        static_path=os.path.join(base_dir, "app", "static"),
        cookie_secret="datafinderagentos-token",
        login_url="/",
        xsrf_cookies=True,
        debug=True,
        autoreload=True
    )
    return tornado.web.Application([
        # 前台路由
        (r"/", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/index", IndexHandler),
        # 后台路由
        (r"/admin/", AdminLoginHandler),
        (r"/admin/login", AdminLoginHandler),
        (r"/admin/logout", AdminLogoutHandler),
        (r"/admin/index", AdminIndexHandler),
        # 用户管理
        (r"/admin/user-management", UserManagementHandler),
        (r"/api/users/list", UserListApiHandler),
        (r"/api/users/get", UserGetApiHandler),
        (r"/api/users/create", UserCreateApiHandler),
        (r"/api/users/update", UserUpdateApiHandler),
        (r"/api/users/delete", UserDeleteApiHandler),
        # 角色管理
        (r"/admin/role-management", RoleManagementHandler),
        (r"/api/roles/list", RoleListApiHandler),
        (r"/api/roles/create", RoleCreateApiHandler),
        (r"/api/roles/update", RoleUpdateApiHandler),
        (r"/api/roles/delete", RoleDeleteApiHandler),
        (r"/api/roles/functions", RoleFunctionsApiHandler),
        (r"/api/roles/functions/save", RoleFunctionsSaveApiHandler),
        # 功能管理
        (r"/admin/function-management", FunctionManagementHandler),
        (r"/api/functions/list", FunctionListApiHandler),
        (r"/api/functions/get", FunctionGetApiHandler),
        (r"/api/functions/create", FunctionCreateApiHandler),
        (r"/api/functions/update", FunctionUpdateApiHandler),
        (r"/api/functions/delete", FunctionDeleteApiHandler),
        (r"/api/functions/toggle", FunctionToggleApiHandler),
        # 菜单管理
        (r"/admin/menu-management", MenuManagementHandler),
        (r"/api/menus/list", MenuListApiHandler),
        (r"/api/menus/create", MenuCreateApiHandler),
        (r"/api/menus/update", MenuUpdateApiHandler),
        (r"/api/menus/delete", MenuDeleteApiHandler),
        (r"/api/menus/preview", MenuPreviewApiHandler),
        # 个人信息 / 修改密码
        (r"/api/profile", ProfileApiHandler),
        (r"/api/profile/change-password", ChangePasswordApiHandler)
    ],
    **settings
    )

if __name__ == '__main__':
    init_db()
    # 初始化默认数据（角色、功能、菜单、角色-功能关联、默认用户）
    try:
        from app.models.db import get_connection
        import hashlib, secrets
        conn = get_connection()
        admin_role = conn.execute("SELECT id FROM roles WHERE code='admin'").fetchone()
        if admin_role:
            admin_role_id = admin_role["id"]
            funcs = conn.execute("SELECT id FROM functions ORDER BY sort_order").fetchall()
            # 为系统管理员分配所有功能（role_functions）
            rf_count = conn.execute("SELECT COUNT(*) FROM role_functions WHERE role_id=?", (admin_role_id,)).fetchone()[0]
            if rf_count == 0:
                for func in funcs:
                    conn.execute(
                        "INSERT OR IGNORE INTO role_functions (role_id, func_id) VALUES (?, ?)",
                        (admin_role_id, func["id"])
                    )
                print(f"✓ 已为系统管理员分配 {len(funcs)} 个功能")
            # 检查并插入默认菜单（系统管理员关联所有功能）
            menu_count = conn.execute("SELECT COUNT(*) FROM menus").fetchone()[0]
            if menu_count == 0:
                for i, func in enumerate(funcs):
                    conn.execute(
                        "INSERT INTO menus (role_id, func_id, sort_order) VALUES (?, ?, ?)",
                        (admin_role_id, func["id"], i + 1)
                    )
                print(f"✓ 已为系统管理员创建 {len(funcs)} 个默认菜单")
        # 创建默认 admin 用户（如果不存在）
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 0:
            salt = secrets.token_bytes(16)
            pwd_hash = hashlib.pbkdf2_hmac("sha256", b"123456", salt, 100_000).hex()
            conn.execute(
                "INSERT INTO users (username, password_hash, salt, role_id, status) VALUES (?, ?, ?, ?, ?)",
                ("admin", pwd_hash, salt.hex(), admin_role["id"] if admin_role else 1, 1)
            )
            print("✓ 已创建默认管理员用户（admin / 123456）")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠ 初始化默认数据出错: {e}")
    
    webapp = webapp()
    # 将应用程序部署到服务器
    server = HTTPServer(webapp)
    server.listen(10010)
    print("Server Started:http://localhost:10010/", flush=True)
    tornado.ioloop.IOLoop.current().start()
