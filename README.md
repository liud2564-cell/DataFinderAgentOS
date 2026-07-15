# 瞭望与问数系统 DataFinderAgentOS v0.2

面向政务场景的数据汇聚、智能问数与态势瞭望基础平台。

## 快速启动

```bash
pip install -r requirements.txt
python app.py
```

启动后访问：
- 用户端：http://localhost:10010/
- 管理端：http://localhost:10010/admin/login（演示账号 admin / 123456）

## 项目结构

```
DataFinderAgentOS/
├── app.py                 # 应用入口
├── config/settings.py     # 配置中心
├── app/
│   ├── models/            # 数据层（db/user/rbac/source/collect/model_config/data_warehouse）
│   ├── controllers/       # 控制器（auth/home/permission/source/collect/model/warehouse）
│   ├── templates/         # 页面模板
│   └── static/            # 静态资源
├── database/              # SQLite 数据库
└── test/                  # 测试
```

## 技术栈

- Python Tornado Web 框架
- SQLite 数据库 (WAL模式)
- PBKDF2-SHA256 密码哈希
- Secure Cookie + XSRF 防护
- RBAC 权限管理（用户/角色/功能/菜单）
- OPENAI 兼容 API 模型引擎 (SSE 流式对话)
- HTTP 采集引擎 + HTML 智能解析
- 数据仓库持久化存储

## v0.2 新增

- 瞭源管理：采集源 CRUD，URL模板 + 变量替换 {keyword}/{pn}
- 瞭望采集：HTTP采集引擎，HTML智能解析，结果自动入库
- 模型引擎：OPENAI兼容API管理，SSE流式对话，Token统计
- 数据仓库：采集结果存储检索，批量管理，关键词索引
