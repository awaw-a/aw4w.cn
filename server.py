#!/usr/bin/env python3
"""HTTP 服务器：静态文件 + /api/chat (先尝试 AstrBot，失败则用模拟回复)"""
import http.server
import json
import os
import re
import urllib.request
import urllib.error
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.environ.get("STATIC_DIR", BASE_DIR)
PROXY_URL = os.environ.get("PROXY_URL", "http://127.0.0.1:6185/api/v1/chat")
ASTRBOT_API_KEY = os.environ.get("ASTRBOT_API_KEY", "")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "31058"))

# AstrBot OpenAPI 基础地址（由 /chat 接口推导，用于会话管理等其它接口）
_p = PROXY_URL.rstrip("/")
ASTRBOT_BASE = _p[:-len("/chat")] if _p.endswith("/chat") else _p

from generate_posts_index import scan_posts

def clean_token(value, default=""):
    """校验 username / session_id，只允许字母数字和 _-，防止注入"""
    v = (value or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_\-]{1,64}", v):
        return v
    return default

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



def _parse_astrbot_response(raw: str):
    """解析 AstrBot /api/v1/chat 的响应，兼容 SSE 流与普通 JSON。"""
    if not raw:
        return None
    text = raw.strip()
    # 普通 JSON（非 SSE）
    if not text.startswith("data:"):
        try:
            backend_data = json.loads(text)
            reply = (backend_data.get("reply") or
                     backend_data.get("text") or
                     backend_data.get("message") or
                     (backend_data.get("data") or {}).get("reply") or
                     "")
            if isinstance(reply, dict):
                reply = reply.get("content") or reply.get("text") or str(reply)
            return reply or None
        except Exception:
            return None
    # SSE 流：逐行解析 data: {...}
    parts = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[len("data:"):].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            obj = json.loads(payload)
        except Exception:
            continue
        t = obj.get("type")
        d = obj.get("data")
        if t == "plain" and isinstance(d, str):
            parts.append(d)
        elif t == "message" and isinstance(d, dict):
            c = d.get("content") or d.get("message") or ""
            if isinstance(c, str):
                parts.append(c)
    return "\n".join(parts) if parts else None

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

    def _astrbot_headers(self):
        h = {"Content-Type": "application/json"}
        if ASTRBOT_API_KEY:
            h["Authorization"] = f"Bearer {ASTRBOT_API_KEY}"
        return h

    def _proxy_json(self, method, url):
        """转发到 AstrBot 并原样返回响应体，失败返回 None"""
        try:
            req = urllib.request.Request(url, headers=self._astrbot_headers(), method=method)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as e:
            print(f"AstrBot {method} {url} 失败: {e}")
            return None

    def _send_json(self, payload, status=200):
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/api/posts":
            # 实时扫描 posts/ 目录，返回文章列表
            posts = scan_posts(os.path.join(STATIC_DIR, "posts"))
            payload = json.dumps({"posts": posts}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(payload)
            return

        if path == "/api/chat/sessions":
            # 会话列表 -> AstrBot GET /api/v1/chat/sessions
            username = clean_token(qs.get("username", [""])[0], "web_guest")
            url = (f"{ASTRBOT_BASE}/chat/sessions?username={username}"
                   f"&page=1&page_size=50&platform_id=webchat")
            payload = self._proxy_json("GET", url)
            self._send_json(payload or {"status": "error", "data": {"sessions": []}})
            return

        if path == "/api/chat/history":
            # 会话历史 -> AstrBot GET /api/v1/chat/sessions/{session_id}
            sid = clean_token(qs.get("session_id", [""])[0])
            if not sid:
                self._send_json({"status": "error", "message": "missing session_id"}, 400)
                return
            payload = self._proxy_json("GET", f"{ASTRBOT_BASE}/chat/sessions/{sid}")
            self._send_json(payload or {"status": "error", "data": {"messages": []}})
            return

        super().do_GET()

    def do_DELETE(self):
        # 删除会话 -> AstrBot DELETE /api/v1/chat/sessions/{session_id}
        path = urllib.parse.urlsplit(self.path).path
        m = re.fullmatch(r"/api/chat/sessions/([A-Za-z0-9_\-]{1,64})", path)
        if m:
            payload = self._proxy_json("DELETE", f"{ASTRBOT_BASE}/chat/sessions/{m.group(1)}")
            self._send_json(payload or {"status": "error"})
        else:
            self.send_response(404)
            self.end_headers()

    def _open_astrbot(self, user_text, streaming, username="web_guest", session_id=""):
        """发起 AstrBot 请求，返回 HTTPResponse（调用方负责关闭）"""
        payload = {
            "message": user_text,
            "username": username,
            "enable_streaming": streaming
        }
        if session_id:
            payload["session_id"] = session_id
        astrbot_body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            PROXY_URL,
            data=astrbot_body,
            headers=self._astrbot_headers(),
            method="POST"
        )
        return urllib.request.urlopen(req, timeout=60)

    def _fetch_reply(self, user_text, username="web_guest", session_id=""):
        """非流式获取完整回复，失败返回 None"""
        try:
            with self._open_astrbot(user_text, False, username, session_id) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                return _parse_astrbot_response(raw)
        except Exception as e:
            print(f"AstrBot 调用失败: {e}")
            return None

    def _send_sse_headers(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        # 防止 Nginx 等反向代理缓冲流式响应
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def _write_sse_chunk(self, text):
        chunk = json.dumps({
            "choices": [{"delta": {"content": text}}]
        }, ensure_ascii=False)
        self.wfile.write(f"data: {chunk}\n\n".encode("utf-8"))
        self.wfile.flush()

    def _chat_stream(self, user_text, username="web_guest", session_id=""):
        """流式：优先实时透传 AstrBot SSE，失败则整段回复，再失败模拟兜底"""
        upstream = None
        fallback_reply = None
        try:
            upstream = self._open_astrbot(user_text, True, username, session_id)
            ctype = upstream.headers.get("Content-Type", "")
            if "event-stream" not in ctype:
                # 上游未返回 SSE：按普通响应解析后走整段下发
                raw = upstream.read().decode("utf-8", errors="replace")
                upstream.close()
                upstream = None
                fallback_reply = _parse_astrbot_response(raw)
        except Exception as e:
            print(f"AstrBot 流式调用失败: {e}")
            upstream = None

        self._send_sse_headers()
        try:
            if upstream is not None:
                # 逐行实时透传上游 SSE
                try:
                    for raw_line in upstream:
                        self.wfile.write(raw_line)
                        self.wfile.flush()
                except Exception as e:
                    print(f"AstrBot 流式转发中断: {e}")
                finally:
                    upstream.close()
            else:
                if not fallback_reply:
                    fallback_reply = self._fetch_reply(user_text, username, session_id)
                if not fallback_reply:
                    fallback_reply = mock_reply(user_text)
                self._write_sse_chunk(fallback_reply)
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass  # 客户端提前断开

    def _chat_plain(self, user_text, username="web_guest", session_id=""):
        """非流式：AstrBot 优先，模拟兜底"""
        reply = self._fetch_reply(user_text, username, session_id)
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

    def do_POST(self):
        if self.path == "/api/chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            # 解析用户消息与身份信息
            user_text = ""
            data = {}
            try:
                data = json.loads(body)
                user_text = extract_user_text(data)
            except:
                pass
            username = clean_token(data.get("username"), "web_guest")
            session_id = clean_token(data.get("session_id"))

            if data.get("enable_streaming"):
                self._chat_stream(user_text, username, session_id)
            else:
                self._chat_plain(user_text, username, session_id)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    if not os.path.isdir(STATIC_DIR):
        raise SystemExit(f"STATIC_DIR 不存在: {STATIC_DIR}")
    os.chdir(STATIC_DIR)
    # 流式 SSE 连接会长期占用连接，必须用多线程服务器
    server = http.server.ThreadingHTTPServer((HOST, PORT), ProxyHandler)
    print(f"服务: http://{HOST}:{PORT}")
    print(f"静态: {STATIC_DIR}")
    print(f"API: POST /api/chat (SSE流式透传，AstrBot优先，模拟兜底)")
    print(f"AstrBot: {PROXY_URL} (API Key: {'已配置' if ASTRBOT_API_KEY else '未配置'})")
    server.serve_forever()
