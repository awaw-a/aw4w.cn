---
tags: [CS2, Windows, 开源]
---

# 烂梗喵：在 CS2 里一键发送随机烂梗

> 写于 2026 年 8 月 18 日

## 简介

[烂梗喵](https://github.com/awaw-a/langengmiao) 是我为 Windows 和 CS2 写的一个桌面小工具。它会从 sb6657 获取随机烂梗，再通过 CS2 原生 CFG 命令发送到全体聊天或队内聊天。

和模拟键盘输入的方案不同，它不会弹出聊天栏，不占用剪贴板，也不会模拟 `Y`、`U` 或 `Enter`。游戏内真正执行的是 CS2 自己的 `say` / `say_team` 命令，烂梗喵只负责准备内容、管理按键绑定，并在发送后补充下一条。

## 它能做什么

- 自动检测 Steam 与 CS2 安装目录，也支持手动选择并校验路径。
- 点击按钮后直接按键设置游戏内发送键，默认使用 `F8`。
- 支持全体聊天和队内聊天两种发送范围。
- 后台预取并缓存 2 至 32 条烂梗，发送后自动准备下一条。
- 安全更新当前 Steam 用户的 CS2 按键配置，并在换绑时恢复原有命令。
- 自动备份配置，只覆盖带有自身所有权标记的 CFG 文件。
- 支持接口连接测试、发送历史、本地配置持久化和一键清理绑定。

## 它是怎么发送的

烂梗喵会把当前内容写入 `lanmian_send.cfg`，其中保存一条经过清洗的 `say` 或 `say_team` 命令；再通过 `lanmian_bootstrap.cfg`、`autoexec.cfg` 和当前 Steam 用户的按键配置，把所选按键绑定为：

```text
exec lanmian_send
```

按键时，CS2 直接执行这份 CFG。烂梗喵在确认 CS2 位于前台后记录本次发送，并把缓存中的下一条内容写回 `lanmian_send.cfg`，供下一次按键使用。

这种方式不注入游戏、不读取游戏进程内存，也不向聊天窗口模拟输入。写入前还会移除控制字符、合并换行、替换分号并限制文本长度，避免接口返回内容被解释成额外的控制台命令。

## 使用方式

使用前需要让 Steam 登录目标账号，并至少成功启动过一次 CS2。首次应用绑定、修改已安装的绑定或删除绑定时，要先完全关闭 CS2，避免游戏退出时用内存中的旧配置覆盖文件。

Windows x64 用户可以前往项目的 [Releases](https://github.com/awaw-a/langengmiao/releases) 页面，下载最新的 `langengmiao-<版本>-windows-x64.zip` 和对应的 SHA-256 校验文件。完整解压后运行 `Lanmian.exe`，确认 CS2 路径、发送键、聊天范围和缓存数量，再点击“应用 CFG 绑定”即可。

当前发行版没有代码签名，Windows SmartScreen 可能会显示未知发布者。请只从项目 Releases 下载，并在运行前核对 SHA-256。

## 技术说明

项目使用 Godot 4.6.1 .NET、C# 和 .NET 8 开发，目前只支持 Windows x64。烂梗内容来自 sb6657 的公开随机接口，发布流程由 GitHub Actions 自动构建 Windows 便携版，并同时生成 ZIP 和校验文件。

源代码使用 MIT License 发布。项目不会尝试绕过 VAC、反作弊或服务器限制；自动化聊天是否可用仍取决于 Steam、服务器和赛事规则，建议先在离线、私人或明确允许的环境中测试，并在发送前确认内容是否合适。

## 项目仓库

[https://github.com/awaw-a/langengmiao](https://github.com/awaw-a/langengmiao)

---

*欢迎 Star 和 Issue 反馈。*
