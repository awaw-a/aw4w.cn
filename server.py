#!/usr/bin/env python3
"""HTTP 服务器：静态文件 + /api/chat (先尝试 AstrBot，失败则用模拟回复)"""
import http.server
import json
import os
import urllib.request
import urllib.error

STATIC_DIR = "/www/wwwroot/hello_site"
PROXY_URL = "http://127.0.0.1:6185/api/v1/chat"
HOST = "0.0.0.0"
PORT = 31058

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

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            # 解析用户消息
            user_text = ""
            try:
                data = json.loads(body)
                user_text = data.get("messages", [{}])[-1].get("content", "")
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
    os.chdir(STATIC_DIR)
    server = http.server.HTTPServer((HOST, PORT), ProxyHandler)
    print(f"服务: http://{HOST}:{PORT}")
    print(f"静态: {STATIC_DIR}")
    print(f"API: POST /api/chat (AstrBot优先，模拟兜底)")
    server.serve_forever()
