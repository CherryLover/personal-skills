#!/usr/bin/env bash
set -euo pipefail

TWITTERGET_ROOT="${TWITTERGET_ROOT:-/Users/jiangjiwei/Code/Projects/TwitterGet}"

if [ ! -d "$TWITTERGET_ROOT" ]; then
  echo "错误: 找不到 TwitterGet 项目目录: $TWITTERGET_ROOT" >&2
  exit 1
fi

cd "$TWITTERGET_ROOT"
exec bun scripts/query-twitter-activity.ts "$@"
