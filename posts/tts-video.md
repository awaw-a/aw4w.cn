# tts-video：蓝底小视频一键生成器 Demo

> 写于 2026 年 5 月 27 日

## 简介

[tts-video](https://github.com/awaw-a/tts-video) 是我最近开发的一个静态角色口播视频生成器 Demo。它的目标很直接：给它一张图片、一段参考音频和一段文案，就能生成一个带字幕的 MP4 小视频。

当前版本主要面向“蓝底小视频”这类轻量口播内容，适合快速把角色图片、克隆语音和字幕合成为可直接发布的视频。

![tts-video 使用示意图](/posts/tts-video.jpg)

## 它能做什么

- 上传 png、jpg、jpeg、webp 格式的角色图片。
- 上传 wav、mp3、m4a 格式的参考音频或测试音频。
- 输入文案后自动切分字幕。
- 支持 16:9、4:3、9:16、3:4、1:1 五种视频比例。
- 支持图片模糊填充、纯白、纯红、纯蓝、渐变蓝、渐变红等背景样式。
- 支持多种 ASS 字幕样式，并用 FFmpeg 合成视频、烧录字幕。
- 输出文件保存在 `data/outputs/{task_id}/final.mp4`。

## 技术说明

语音部分默认接入开源的 IndexTTS2，通过参考音频和输入文案生成克隆语音；视频合成部分使用 FFmpeg，把静态图片、音频和字幕整理成最终 MP4。

项目里也保留了 `mock` 后端，方便在没有模型环境时先验证 WebUI 和视频合成流程。

## 使用方式

Windows 用户可以优先使用整合包版本。理论上解压后点击 `start_all.bat`，脚本会启动 IndexTTS API 和 tts-video WebUI，并自动打开浏览器。

如果从源码运行，可以参考仓库 README。完整链路一般需要先准备 Python 环境、IndexTTS 依赖、模型文件和 FFmpeg。

## 下载

目前整合包主要支持 Win10 / Win11。

- 百度网盘：[https://pan.baidu.com/s/1IKfD4nCeVrQEdc2_iKBppQ?pwd=aw4w](https://pan.baidu.com/s/1IKfD4nCeVrQEdc2_iKBppQ?pwd=aw4w)
- 夸克网盘：[https://pan.quark.cn/s/29b624315e7b](https://pan.quark.cn/s/29b624315e7b)

## 项目仓库

[https://github.com/awaw-a/tts-video](https://github.com/awaw-a/tts-video)

欢迎 Star 和 Issue 反馈。
