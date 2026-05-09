# aw4w.cn

这是我的个人网站前端项目，包含首页、聊天页、博客页和更新日志页。站点以 `awaw_a` 为标识，整体风格偏轻量、柔和、二次元，主题角色为「若叶睦」。

## 在线地址

- 网站：<https://aw4w.cn>
- GitHub：<https://github.com/awaw-a>
- Bilibili：<https://space.bilibili.com/1605536939>

## 功能

- 首页：个人展示、角色头像、打字机气泡、社交链接。
- 聊天：前端聊天界面，向 `/api/chat` 发送消息，可对接 AstrBot 或其他后端服务。
- 博客：文章列表页与文章详情页，文章内容使用 Markdown 编写。
- 更新日志：用时间轴记录网站版本与更新内容。
- 响应式布局：适配桌面端和移动端导航。

## 技术栈

- HTML / CSS / JavaScript
- Tailwind CSS CDN
- Font Awesome 图标
- Google Fonts
- marked.js：用于 Markdown 渲染
- Python 标准库 HTTP Server：用于静态文件服务和 `/api/chat` 代理示例

## 项目结构

```text
.
├── index.html          # 首页
├── chat.html           # 聊天页
├── blog.html           # 博客列表页
├── article.html        # Markdown 文章详情页
├── changelog.html      # 更新日志页
├── 404.html            # 404 页面
├── server.py           # 静态服务 + /api/chat 代理示例
├── posts/
│   └── hello-world.md  # 博客文章
├── avatar_v2.png       # 角色头像
├── avatar.gif          # 动态头像资源
└── favicon.png         # 网站图标
```

## 本地预览

如果只预览静态页面，可以在项目目录启动一个简单的静态服务器：

```bash
python -m http.server 8000
```

然后访问：

```text
http://localhost:8000/index.html
http://localhost:8000/chat.html
http://localhost:8000/blog.html
http://localhost:8000/changelog.html
```

如果需要使用 `/chat`、`/blog`、`/article?id=hello-world` 这类无 `.html` 后缀的路径，需要在 Nginx 或其他 Web 服务器中配置重写规则，例如：

```nginx
try_files $uri $uri.html $uri/ =404;
```

## 博客文章

博客文章存放在 `posts/` 目录中，格式为 Markdown。

新增文章示例：

```text
posts/my-new-post.md
```

文章详情页通过查询参数加载 Markdown：

```text
/article?id=my-new-post
```

添加新文章后，需要在 `blog.html` 中补充对应的文章卡片入口。

## 聊天接口

`chat.html` 默认向下面的接口发送请求：

```text
POST /api/chat
```

`server.py` 提供了一个简单的后端示例：

- 静态文件目录：`STATIC_DIR`
- AstrBot 接口地址：`PROXY_URL`
- 监听端口：`PORT`
- 当 AstrBot 请求失败时，会返回内置的模拟回复

部署前请根据服务器实际路径修改：

```python
STATIC_DIR = "/www/wwwroot/hello_site"
PROXY_URL = "http://127.0.0.1:6185/api/v1/chat"
PORT = 31058
```

## 部署说明

推荐使用 Nginx 托管静态文件，并将 `/api/chat` 代理到后端服务。

一个常见的部署方式：

1. 将本项目文件放到服务器网站目录，例如 `/www/wwwroot/hello_site`。
2. 配置 Nginx 静态资源根目录。
3. 配置 `try_files $uri $uri.html $uri/ =404;` 支持无后缀访问。
4. 如果启用聊天功能，将 `/api/chat` 转发到 `server.py` 或实际聊天后端。
5. 配置 HTTPS 证书。

## 更新日志

当前站点已记录在 `changelog.html` 中：

- `v1.1.0`：博客功能上线，域名 `aw4w.cn` 实装。

## License

本项目为个人网站源码，内容与素材请勿未经允许直接商用或二次发布。
