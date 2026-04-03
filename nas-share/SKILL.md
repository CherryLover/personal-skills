---
name: nas-share
description: 在 Synology NAS 上创建文件/文件夹分享链接。全自动认证（device_id + OTP secret 自动生成验证码）。当用户提到"NAS 分享"、"分享链接"、"创建 NAS 链接"、"nas share"、"/nas-share"时触发。
---

# Synology NAS 分享链接管理

通过 Synology Drive API 自动创建分享链接，无需打开网页。认证全自动（已保存 device_id 和 OTP secret）。

> 注意：NAS 的 FileStation Sharing 功能被管理员禁用（`support_sharing: false`），因此使用 Synology Drive API（`SYNO.SynologyDrive.Sharing`）来创建分享链接。

## NAS 信息

- NAS 地址: `https://work.anvizsys.com:6062/`
- 本地 SMB 挂载: `/Volumes/home`
- NAS 路径前缀: `/home`
- Drive 路径前缀: `/mydrive`
- 用户名: `jiangjiwei`
- 目录结构: `apk/`, `对外分享/`, `协议/`

## 脚本路径

```
/Users/jiangjiwei/.claude/skills/nas-share/scripts/nas_share.py
```

## 配置文件

- 路径: `~/.claude/nas-share-config.json`
- 已配置: username, password, otp_secret, device_id
- 认证方式: 优先 device_id 免 OTP，失效时自动用 otp_secret 生成验证码重新认证

## 常用命令

```bash
# 创建分享链接（本地路径自动转换为 Drive 路径）
python3 /Users/jiangjiwei/.claude/skills/nas-share/scripts/nas_share.py share /Volumes/home/对外分享/some-file.apk

# 直接用 NAS 路径（/home/... 自动转为 /mydrive/...）
python3 /Users/jiangjiwei/.claude/skills/nas-share/scripts/nas_share.py share /home/对外分享/some-file.apk

# 直接用 Drive 路径
python3 /Users/jiangjiwei/.claude/skills/nas-share/scripts/nas_share.py share /mydrive/对外分享/some-file.apk

# 列出所有分享链接
python3 /Users/jiangjiwei/.claude/skills/nas-share/scripts/nas_share.py list

# 删除分享链接
python3 /Users/jiangjiwei/.claude/skills/nas-share/scripts/nas_share.py delete <link_id>

# 查看配置和连接状态
python3 /Users/jiangjiwei/.claude/skills/nas-share/scripts/nas_share.py status
```

## 路径转换规则

| 输入路径 | 转换后 Drive 路径 |
|---|---|
| `/Volumes/home/对外分享/file.pdf` | `/mydrive/对外分享/file.pdf` |
| `/home/对外分享/file.pdf` | `/mydrive/对外分享/file.pdf` |
| `/mydrive/对外分享/file.pdf` | `/mydrive/对外分享/file.pdf` |

## API 流程

1. 登录获取 SID（`SYNO.API.Auth`）
2. 通过 Drive 路径获取文件 ID（`SYNO.SynologyDrive.Files.get`）
3. 用文件 ID 创建分享链接（`SYNO.SynologyDrive.Sharing.create_link`）

## 工作流程

1. 用户给出文件路径，运行 `share` 命令，返回分享链接
2. 路径转换: 本地 `/Volumes/home/xxx` → Drive `/mydrive/xxx`
3. 认证全自动，无需用户干预

## 依赖

- `pyotp` (已安装): TOTP 验证码生成
