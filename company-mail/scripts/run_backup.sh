#!/bin/bash
# 公司邮件增量备份 - 每日运行脚本
# 用法: ./run_backup.sh         # 仅本地备份
#       ./run_backup.sh --icloud # 同步到 iCloud

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "$(date '+%Y-%m-%d %H:%M:%S') 开始邮件备份..."

python3 "$SCRIPT_DIR/mail_backup.py" "$@"

echo ""
echo "$(date '+%Y-%m-%d %H:%M:%S') 备份完成"
