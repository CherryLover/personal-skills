# 命令说明

## Wrapper

优先执行：

```bash
~/.codex/skills/twitter-activity-checker/scripts/run-twitter-activity.sh @naval
```

如果部署目录不是默认值，先设置：

```bash
export TWITTERGET_ROOT=/path/to/TwitterGet
```

## 实际调用的项目脚本

```bash
cd "$TWITTERGET_ROOT"
bun scripts/query-twitter-activity.ts @naval --mode both
```

## 常用参数

- `--mode tweets|likes|both`：查推文、查点赞、或两者都查
- `--tweets-pages N`：推文抓取页数
- `--likes-pages N`：点赞抓取页数
- `--likes-page-size N`：每页点赞条数，最大 100
- `--tweets-cursor <cursor>`：从指定推文游标继续翻页
- `--likes-cursor <cursor>`：从指定点赞游标继续翻页
- `--delay-ms N`：分页请求间隔，默认 1200ms
- `--user-id <id>`：已知 user id 时可直接传入，跳过查 id
- `--output <file>`：指定 JSON 输出文件

## 输出 JSON 结构

顶层字段：
- `generatedAt`
- `target`
- `options`
- `tweets`
- `likes`

其中：
- `tweets.nextCursor` 可继续翻推文下一页
- `likes.nextCursor` 可继续翻点赞下一页
- `tweets.items[*].tweetUrl` / `likes.items[*].tweetUrl` 可直接引用原推文链接
- `tweets.error` / `likes.error` 不为空时，说明这一段抓取失败了
