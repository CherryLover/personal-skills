---
name: scrape
description: 抓取社交媒体帖子内容。当用户提供 X/Twitter、即刻、抖音的链接并希望抓取/保存/下载内容时触发。支持命令 /scrape <url>。
---

# 社交媒体内容抓取 Skill

从社交媒体链接中提取帖子内容（文本、图片、视频），保存为 Markdown 文件。

## 项目路径

```
/Users/jiangjiwei/Code/Projects/UrlColl
```

## 支持平台与 URL 匹配规则

| 平台 | URL 特征 | 对应脚本 |
|------|----------|----------|
| X/Twitter | 包含 `x.com` 或 `twitter.com` | `x_scraper.py` |
| 即刻 | 包含 `okjike.com` | `jike_scraper.py` |
| 抖音 | 包含 `douyin.com` | `douyin_scraper.py` |

## 执行步骤

1. **识别平台**：根据用户提供的 URL 匹配上述规则，确定使用哪个脚本。如果 URL 不匹配任何平台，告知用户当前不支持该平台。

2. **运行脚本**：
```bash
source /Users/jiangjiwei/Code/Projects/UrlColl/venv/bin/activate && python /Users/jiangjiwei/Code/Projects/UrlColl/<脚本名> "<用户提供的URL或分享文本>"
```

3. **展示结果**：脚本会输出 JSON 格式的抓取结果并保存 Markdown 文件。将关键信息以可读的方式展示给用户：
   - 作者和发布时间
   - 帖子正文内容（如果较长则展示摘要）
   - 图片/视频数量
   - 保存的文件路径

## 注意事项

- 抖音链接支持传入完整的分享文本（从 App 复制的），脚本会自动提取其中的短链接
- 抖音视频会自动下载无水印版本到 `output/videos/` 目录
- X/Twitter 支持普通推文和 Article 长文两种类型
- 如果用户只是贴了一个链接没说要干什么，默认执行抓取
