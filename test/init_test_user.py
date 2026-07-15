# 初始化测试用户
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.models.db import init_db
from app.models.user import UserRepository

init_db()

username = "admin"
password = "123456"

# 检查用户是否存在，不存在则创建
if not UserRepository.get_user_by_username(username):
    created = UserRepository.create_user(username, password)
    if created:
        print(f"测试用户创建成功！用户名：{username}，密码：{password}")
    else:
        print(f"用户创建失败！用户名：{username}")
else:
    print(f"测试用户已存在！用户名：{username}")
