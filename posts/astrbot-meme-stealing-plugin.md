# AstrBot 插件：astrbot_plugin_meme_stealing

> 写于 2026 年 5 月 23 日

## 简介

[astrbot_plugin_meme_stealing](https://github.com/awaw-a/astrbot_plugin_meme_stealing) 是我最近给 AstrBot 写的 QQ 群表情包采集与自动回复插件。

它会按配置概率保存群友发送的图片/表情包，调用 AstrBot 已配置的多模态 LLM 生成描述、标签和情绪场景，再通过关键词匹配，在群聊里自动发送合适的表情包。

## 它能做什么

- 自动采集群聊 Image 消息，并用 SHA-256 去重。
- 支持 `/meme_save latest` 等管理员指令，手动保存最近或被回复的图片。
- 保存前先判断图片是否更像表情包、贴纸、梗图或反应图，普通照片、文档、二维码、广告等会被跳过。
- 使用 SQLite 保存元数据，图片保存在本地插件数据目录。
- 支持 `/meme_on`、`/meme_off` 按群开关自动表情回复。
- 提供本地 FastAPI 管理面板，可以预览、搜索、编辑、审核、启用/禁用和删除表情包。

## 为什么写它

群聊里的表情包总是带着自己的语境。手动整理很麻烦，完全随机发送又很容易不对味，所以这个插件尝试把“偷图、理解、整理、再使用”串起来：让 bot 慢慢积累一套属于当前群的表情包库。

## 使用前提醒

插件默认不会保存发送者 QQ 号，但如果在群里启用自动采集，最好提前告知群成员。管理面板的 `admin_token` 也一定要改掉；如果需要公网访问，建议配合防火墙、VPN 或反向代理鉴权使用。

## 项目仓库

[https://github.com/awaw-a/astrbot_plugin_meme_stealing](https://github.com/awaw-a/astrbot_plugin_meme_stealing)

---

*欢迎 Star 和 Issue 反馈。*
