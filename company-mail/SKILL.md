---
name: company-mail
description: 读取公司私有邮件（Xthings/Anviz 邮箱 jiangjiwei@xthings.com）。通过 IMAP 连接 mail.anvizsys.com 读取邮件。触发场景：(1) 用户提到"查邮件"、"看邮件"、"读邮件"、"最新邮件"、"公司邮件"、"收件箱"；(2) 用户说"搜索邮件"、"找邮件"、"某人发的邮件"；(3) 用户提到"/mail"或"check mail"。
---

# 公司邮件读取

通过 `scripts/mail_tool.py` 脚本读取公司邮箱（jiangjiwei@xthings.com）的邮件。

## 脚本路径

```
~/.claude/skills/company-mail/scripts/mail_tool.py
```

## 命令

### 查看最新邮件

```bash
python3 ~/.claude/skills/company-mail/scripts/mail_tool.py list -n 10
```

- `-n` 数量，默认 10
- `-f` 文件夹，默认 INBOX

### 读取指定邮件全文

```bash
python3 ~/.claude/skills/company-mail/scripts/mail_tool.py read <邮件ID>
```

- 邮件 ID 从 list 或 search 结果中获取

### 搜索邮件

```bash
python3 ~/.claude/skills/company-mail/scripts/mail_tool.py search --subject "关键词" --sender "发件人" --since "01-Mar-2026" --unseen -n 20
```

- `--subject` 按主题搜索
- `--sender` 按发件人搜索
- `--since` 起始日期（格式 DD-Mon-YYYY）
- `--before` 截止日期
- `--unseen` 仅未读
- `-n` 数量限制，默认 20

### 查看文件夹列表

```bash
python3 ~/.claude/skills/company-mail/scripts/mail_tool.py folders
```

### 查找带附件的邮件

```bash
python3 ~/.claude/skills/company-mail/scripts/mail_tool.py attachments -n 10
```

## 输出格式

所有命令输出 JSON，可直接解析。向用户展示时转为可读的中文摘要。

## 注意事项

- 首次运行会自动在 `scripts/.venv` 创建虚拟环境并安装 `imapclient`
- 可用文件夹：INBOX, Sent, Drafts, Trash, Junk, Archive, Templates
- 搜索日期格式必须是 IMAP 标准格式：`DD-Mon-YYYY`（如 `01-Jan-2026`）
