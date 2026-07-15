"""应用配置中心。"""
from __future__ import annotations

import os
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APP_PORT = int(os.environ.get("PORT", 10010))
DEBUG = os.environ.get("DEBUG", "false").lower() in ("1", "true", "yes")
COOKIE_SECRET = os.environ.get("COOKIE_SECRET", uuid.uuid4().hex)

PROJECT_NAME = "瞭望与问数系统"
PROJECT_SHORT_NAME = "DataFinderAgentOS"
VERSION = "v0.3"

DATABASE_PATH = str(BASE_DIR / "database" / "data.db")

SESSION_COOKIE_NAME = "df_user"
SESSION_EXPIRES_DAYS = 7
COOKIE_SECURE = False
COOKIE_SAMESITE = "Lax"

ADMIN_LOGIN_URL = "/admin/login"

SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
}

LOGIN_RATE_LIMIT_MAX = 5
LOGIN_RATE_LIMIT_WINDOW = 300

DEFAULT_ADMIN = {"username": "admin", "password": "123456"}

# 采集配置
COLLECT_TIMEOUT = 15
COLLECT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
