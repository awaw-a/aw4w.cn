#!/usr/bin/env python3
"""扫描 posts/ 目录下的 Markdown 文章，生成 posts/index.json。

- 本地开发时 server.py 的 /api/posts 会实时调用 scan_posts()，无需运行本脚本。
- 静态部署（如 Nginx）时，新增文章后运行一次：python generate_posts_index.py

文章元数据支持可选的 front matter（放在文件最顶部）：

    ---
    tags: [AstrBot, 插件]
    date: 2026-06-01
    ---

未提供 front matter 时，会自动从正文提取：
- 标题：第一个一级标题（# ...）
- 日期："> 写于 YYYY 年 M 月 D 日" 行，找不到则用文件修改时间
- 摘要：第一段正文（自动去除 Markdown 标记）
"""
import json
import os
import re
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE_DIR, "posts")
OUT_FILE = os.path.join(POSTS_DIR, "index.json")

EXCERPT_MAXLEN = 120


def parse_front_matter(text):
    """解析文件顶部的 --- front matter ---，返回 (meta, body)"""
    meta = {}
    if not text.startswith("---"):
        return meta, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return meta, text
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [t.strip().strip("'\"") for t in val[1:-1].split(",") if t.strip()]
        else:
            meta[key] = val.strip("'\"")
    return meta, text[m.end():]


def parse_date(body):
    """从 '> 写于 2026 年 6 月 1 日' 提取日期"""
    m = re.search(r"写于\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", body)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return None


def extract_title(body, fallback):
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# ") and not s.startswith("##"):
            return s[2:].strip()
    return fallback


def strip_md(text):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)      # 图片
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # 链接保留文字
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)       # 粗体
    text = re.sub(r"\*(.*?)\*", r"\1", text)              # 星号斜体（保留下划线，避免误伤 snake_case 标识符）
    text = re.sub(r"[`#>]", "", text)                     # 行内代码、标题、引用标记
    return re.sub(r"\s+", " ", text).strip()


def extract_excerpt(body):
    """取第一段普通正文作为摘要"""
    for block in re.split(r"\n\s*\n", body):
        s = block.strip()
        if not s or s[0] in "#>!-":
            continue
        plain = strip_md(s)
        if plain:
            return plain[:EXCERPT_MAXLEN]
    return ""


def scan_posts(posts_dir=POSTS_DIR):
    """扫描目录，返回按日期倒序的文章元数据列表"""
    posts = []
    if not os.path.isdir(posts_dir):
        return posts
    for name in sorted(os.listdir(posts_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(posts_dir, name)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        meta, body = parse_front_matter(text)
        pid = name[:-3]
        date = meta.get("date") or parse_date(body)
        if not date:
            date = datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()
        posts.append({
            "id": pid,
            "title": meta.get("title") or extract_title(body, pid),
            "date": date,
            "tags": meta.get("tags") or [],
            "excerpt": meta.get("excerpt") or extract_excerpt(body),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def main():
    posts = scan_posts()
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"posts": posts}, f, ensure_ascii=False, indent=2)
    print(f"已生成 {OUT_FILE}（{len(posts)} 篇文章）")
    for p in posts:
        print(f"  {p['date']}  {p['title']}")


if __name__ == "__main__":
    main()
