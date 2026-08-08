---
tags: [AstrBot, 插件, JMComic]
---

# AstrBot 插件：astrbot_plugin_jmcomic

> 写于 2026 年 6 月 1 日

## 简介

[astrbot_plugin_jmcomic](https://github.com/awaw-a/astrbot_plugin_jmcomic) 是我最近写的 AstrBot 插件，基于 `JMComic-Crawler-Python`，可以在聊天里查询、搜索和下载 JMComic 内容。

它更像是把下载流程接进 AstrBot：用户发出指令后，插件把任务放进后台队列，不阻塞主事件循环；下载完成后可以自动压缩、发送文件，并按配置清理旧文件。

## 它能做什么

- 支持整本 album 下载，也支持单章节 photo 下载。
- 支持查看详情、关键词搜索、任务队列、取消任务和保存文件列表。
- 下载任务在后台执行，适合比较慢或文件比较大的场景。
- 下载完成后可自动打包为 zip，并支持压缩包密码。
- 可以在 zip 成功后删除原始下载目录，只保留导出的压缩包。
- 支持清理过期下载和导出文件，避免数据目录越堆越大。
- 内置 `JMComic-Crawler-Python`，不用额外手动拉取子仓库。

## 常用指令

- `/jm <album_id>`：下载整本。
- `/jmp <photo_id>`：下载单章节。
- `/jm_info <album_id>`：查看详情，不下载。
- `/jm_search <关键词>`：搜索内容。
- `/jm_queue`：查看最近任务。
- `/jm_cancel <任务ID>`：取消任务。
- `/jm_files [显示数量]`：查看保存的下载目录和导出文件。
- `/jm_clean`：清理过期文件。
- `/jm_help`：查看帮助和当前压缩包密码状态。

## 为什么写它

之前写 AstrBot 插件时，很多功能都是围绕“让 bot 能更自然地参与群聊”展开的。这个插件则更偏工具向：把查询、下载、打包、发送、清理这些步骤收进一套指令里，减少来回切工具的麻烦。

我也尽量把容易出问题的部分做得可检查：比如可以看队列、看文件、测主动推送、清理旧内容。这样一旦协议端不支持文件发送，或者 AstrBot 和 OneBot/NapCat/Lagrange 不在同一个容器里，也更容易知道问题卡在哪里。

## 使用前提醒

插件默认开启 zip 密码，可以在 AstrBot WebUI 的插件配置中修改或关闭。若要在群聊中使用，建议先确认当前平台是否支持文件消息，以及协议端能否读取插件生成的本地文件路径。

请遵守所在地法律法规和平台规则，只在合适、合规的场景中使用。

## 项目仓库

[https://github.com/awaw-a/astrbot_plugin_jmcomic](https://github.com/awaw-a/astrbot_plugin_jmcomic)

---

*欢迎 Star 和 Issue 反馈。*
