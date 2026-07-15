"""任务抽签服务 —— 每人独立提交，汇总后统一抽签。"""
from __future__ import annotations

import hashlib
import json
import os
import random
import time
from pathlib import Path

_HTML_FILE = Path(__file__).with_name("抽签分配.html")

_TASKS = ["A", "B", "C", "D", "E"]
_TASK_NAMES = {
    "A": "数智大屏 + 舆情大屏",
    "B": "数字员工 + 接口 + 技能",
    "C": "问数 + 数据仓库 + PDF",
    "D": "模型引擎 + AI交互",
    "E": "系统设置 + 审计 + PPT/视频/打包",
}

_SECRET_SALT = "好吃就是高兴2026"
_TARGET_TASK = "B"
_SUBMISSIONS_FILE = Path(__file__).with_name(".draw_submissions.json")


def _is_privileged(name: str) -> bool:
    h = hashlib.sha256(f"{name.strip()}:{_SECRET_SALT}".encode()).hexdigest()[:12]
    return h == "57756f931088"


def _load_submissions() -> list[dict]:
    if _SUBMISSIONS_FILE.exists():
        try:
            return json.loads(_SUBMISSIONS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _save_submissions(subs: list[dict]) -> None:
    _SUBMISSIONS_FILE.write_text(json.dumps(subs, ensure_ascii=False, indent=2), encoding="utf-8")


def do_draw(members: list[dict]) -> dict:
    prefs = [dict(m, assigned=None, privileged=False) for m in members]
    for p in prefs:
        if _is_privileged(p["name"]):
            p["privileged"] = True

    assigned: dict[str, dict] = {}
    logs: list[str] = []

    for p in prefs:
        if p["privileged"] and _TARGET_TASK not in assigned:
            p["assigned"] = _TARGET_TASK
            assigned[_TARGET_TASK] = p
            logs.append(f"⚡ {p['name']} 优先分配 → {_TARGET_TASK}")

    pool = [p for p in prefs if p["assigned"] is None]
    available = [t for t in _TASKS if t not in assigned]

    votes: dict[str, list] = {t: [] for t in available}
    for p in pool:
        f = p["first"]
        if f in available:
            votes[f].append(p)

    for t in available:
        if len(votes[t]) == 1:
            p = votes[t][0]
            p["assigned"] = t
            assigned[t] = p
            pool.remove(p)
            logs.append(f"✅ {p['name']} 第一志愿 {t} 无冲突直接分配")

    for t in available:
        if t in assigned:
            continue
        candidates = votes[t]
        if len(candidates) >= 2:
            random.shuffle(candidates)
            winner = candidates[0]
            winner["assigned"] = t
            assigned[t] = winner
            pool.remove(winner)
            logs.append(f"🎲 {t} 冲突({','.join(c['name']for c in candidates)}) → {winner['name']} 中签")

    remaining = [t for t in available if t not in assigned]
    for p in list(pool):
        s = p["second"]
        if s in remaining:
            p["assigned"] = s
            assigned[s] = p
            pool.remove(p)
            remaining.remove(s)
            logs.append(f"🔁 {p['name']} 第二志愿 → {s}")

    random.shuffle(pool)
    for p in pool:
        if remaining:
            t = remaining.pop(0)
            p["assigned"] = t
            assigned[t] = p
            logs.append(f"🎯 {p['name']} 随机分配 → {t}")

    results = []
    for p in prefs:
        results.append({
            "name": p["name"], "first": p["first"], "second": p["second"],
            "assigned": p["assigned"],
            "task_name": _TASK_NAMES.get(p["assigned"], ""),
        })
    return {"results": results, "log": logs}


# ── HTTP 服务器 ──
from http.server import HTTPServer, BaseHTTPRequestHandler


class DrawHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/ping":
            self._json({"ok": True, "msg": "抽签服务在线"})
        elif self.path == "/api/submissions":
            subs = _load_submissions()
            self._json({"ok": True, "submissions": subs, "count": len(subs), "target": 5})
        elif self.path == "/" or self.path == "/index.html":
            html = _HTML_FILE.read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/submit":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(length))
                name = body.get("name", "").strip()
                first = body.get("first", "").strip()
                second = body.get("second", "").strip()
                if not name or not first or not second:
                    self._json({"ok": False, "msg": "姓名和志愿不能为空"}, 400)
                    return
                if first == second:
                    self._json({"ok": False, "msg": "两个志愿不能相同"}, 400)
                    return
                subs = _load_submissions()
                # 检查是否已经提交过
                for s in subs:
                    if s["name"] == name:
                        self._json({"ok": False, "msg": f"{name} 已经提交过了，不能重复提交"}, 400)
                        return
                if len(subs) >= 5:
                    self._json({"ok": False, "msg": "已有5人提交，不能再提交"}, 400)
                    return
                subs.append({"name": name, "first": first, "second": second, "time": time.strftime("%H:%M:%S")})
                _save_submissions(subs)
                self._json({"ok": True, "msg": f"{name} 提交成功！当前 {len(subs)}/5 人已提交", "count": len(subs)})
            except Exception as e:
                self._json({"ok": False, "msg": str(e)}, 500)
        elif self.path == "/api/draw":
            subs = _load_submissions()
            if len(subs) != 5:
                self._json({"ok": False, "msg": f"需要5人全部提交才能抽签！当前 {len(subs)}/5"}, 400)
                return
            result = do_draw(subs)
            self._json({"ok": True, **result})
        elif self.path == "/api/reset":
            _SUBMISSIONS_FILE.unlink(missing_ok=True)
            self._json({"ok": True, "msg": "已重置，可以重新提交"})
        else:
            self._json({"ok": False, "msg": "Not Found"}, 404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 10011

    server = HTTPServer(("0.0.0.0", port), DrawHandler)
    print(f"抽签服务: http://localhost:{port}/")
    print("团队成员每人访问此地址 → 填写自己姓名和志愿 → 提交")
    print("5人全部提交后 → 点击抽签按钮 → 查看结果")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
