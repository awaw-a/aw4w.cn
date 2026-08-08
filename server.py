#!/usr/bin/env python3
"""HTTP 服务器：静态文件 + /api/chat (先尝试 AstrBot，失败则用模拟回复)"""
import http.server
import json
import os
import urllib.request
import urllib.error
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.environ.get("STATIC_DIR", BASE_DIR)
PROXY_URL = os.environ.get("PROXY_URL", "http://127.0.0.1:6185/api/v1/chat")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "31058"))

from generate_posts_index import scan_posts

def mock_reply(user_text):
    """模拟回复"""
    replies = {
        "你好": "你好，我是若叶睦。今天也一起加油吧。",
        "hi": "嗯。",
        "hello": "hello world。",
        "你是谁": "若叶睦。月之森女子学园一年级。Ave Mujica 的吉他手。",
        "在吗": "在。",
        "晚安": "晚安。好好休息。",
        "谢谢": "不客气。",
    }
    for key, val in replies.items():
        if key in user_text:
            return val
    return f"收到。「{user_text[:20]}」\n…不知道该怎么回复。\n换个话题？"

def extract_user_text(data):
    """兼容网页请求和 OpenAI messages 请求格式"""
    if not isinstance(data, dict):
        return ""

    message = data.get("message")
    if isinstance(message, str):
        return message

    messages = data.get("messages") or []
    if messages and isinstance(messages[-1], dict):
        content = messages[-1].get("content", "")
        if isinstance(content, str):
            return content
    return ""

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def translate_path(self, path):
        parsed = urllib.parse.urlsplit(path)
        route = parsed.path.rstrip("/")
        if route and not os.path.splitext(route)[1]:
            candidate = route + ".html"
            candidate_path = super().translate_path(candidate)
            if os.path.isfile(candidate_path):
                path = candidate
        return super().translate_path(path)

    def do_GET(self):
        if urllib.parse.urlsplit(self.path).path == "/api/posts":
            # 实时扫描 posts/ 目录，返回文章列表
            posts = scan_posts(os.path.join(STATIC_DIR, "posts"))
            payload = json.dumps({"posts": posts}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(payload)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            # 解析用户消息
            user_text = ""
            data = {}
            try:
                data = json.loads(body)
                user_text = extract_user_text(data)
            except:
                pass

            # 尝试转发到 AstrBot (AstrBot 官方格式)
            reply = None
            try:
                # 将前端请求转为 AstrBot 格式
                astrbot_body = json.dumps({
                    "message": user_text,
                    "username": "web_guest",
                    "enable_streaming": False
                }).encode("utf-8")
                
                req = urllib.request.Request(
                    PROXY_URL,
                    data=astrbot_body,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    backend_data = json.loads(resp.read())
                    # 兼容多种返回格式
                    reply = (backend_data.get("reply") or 
                             backend_data.get("text") or 
                             backend_data.get("message") or
                             (backend_data.get("data") or {}).get("reply") or
                             "")
                    if isinstance(reply, dict):
                        reply = reply.get("content") or reply.get("text") or str(reply)
            except Exception as e:
                print(f"AstrBot 调用失败: {e}")

            # 模拟回复兜底
            if not reply:
                reply = mock_reply(user_text)

            if data.get("enable_streaming"):
                chunk = json.dumps({
                    "choices": [{"delta": {"content": reply}}]
                }, ensure_ascii=False)

                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(f"data: {chunk}\n\n".encode("utf-8"))
                self.wfile.write(b"data: [DONE]\n\n")
            else:
                resp_data = json.dumps({
                    "choices": [{"message": {"content": reply}}]
                }, ensure_ascii=False)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(resp_data.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    if not os.path.isdir(STATIC_DIR):
        raise SystemExit(f"STATIC_DIR 不存在: {STATIC_DIR}")
    os.chdir(STATIC_DIR)
    server = http.server.HTTPServer((HOST, PORT), ProxyHandler)
    print(f"服务: http://{HOST}:{PORT}")
    print(f"静态: {STATIC_DIR}")
    print(f"API: POST /api/chat (AstrBot优先，模拟兜底)")
    server.serve_forever()
