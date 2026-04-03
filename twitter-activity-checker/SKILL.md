---
name: twitter-activity-checker
description: 查询 X/Twitter 用户最近发过的推文、点赞过的推文和公开动态。当用户提到“查某人的推特”“看他最近发了什么”“看点赞过哪些推文”“看 X 账号最近动态”时使用。优先调用本地 TwitterGet 项目的分页脚本，不走浏览器自动化。
---

# Twitter Activity Checker

这个 skill 不走浏览器自动化，也不依赖手工打开 X 页面。
优先调用本地 `TwitterGet` 项目的脚本，直接拿分页后的结构化结果。

## 能做什么

- 查某个账号最近发过的推文
- 查某个账号公开可见的点赞推文
- 拿到 `nextCursor`，继续翻下一页
- 把结果整理成适合 AI 总结的 JSON

## 入口

优先运行这个 wrapper：
- `scripts/run-twitter-activity.sh <target> [flags]`

它会转发到本地项目脚本：
- `<TWITTERGET_ROOT>/scripts/query-twitter-activity.ts`

默认项目路径：
- `/Users/jiangjiwei/Code/Projects/TwitterGet`

如果部署路径不同，先设置环境变量 `TWITTERGET_ROOT`。

## 输入

支持以下形式：
- `@handle`
- `https://x.com/<handle>`
- `https://twitter.com/<handle>`
- 裸用户名 `handle`

如果用户只给人名，而且可能对应多个账号，先追问准确的 `@handle`。

## 默认流程

1. 先把输入规范成 `handle`。
2. 直接跑本地脚本，不要开浏览器。
3. 读取输出 JSON，分别总结 `tweets` 和 `likes`。
4. 如果用户要更多数据，优先复用返回的 `nextCursor` 继续翻页。
5. 如果 `likes` 为空或报错，要明确说明是接口/权限/公开性限制，不要编造结果。

## 常用命令

- 最近推文 + 点赞，各抓 1 页
  - `scripts/run-twitter-activity.sh @naval`
- 只查推文，多抓 3 页
  - `scripts/run-twitter-activity.sh @naval --mode tweets --tweets-pages 3`
- 只查点赞，每页 100 条
  - `scripts/run-twitter-activity.sh @naval --mode likes --likes-pages 2 --likes-page-size 100`
- 用游标继续翻下一批点赞
  - `scripts/run-twitter-activity.sh @naval --mode likes --likes-pages 1 --likes-cursor '<cursor>'`

参数细节看 `references/commands.md`。

## 输出要求

默认按这个结构回答：

```markdown
账号：@handle
检查时间：YYYY-MM-DD HH:mm

最近推文
- 时间 - 内容摘要 - 链接

最近点赞
- 推文发布时间 - 内容摘要 - 链接

结论
- 最近主要在聊什么
- 明显关注哪些话题

限制
- 哪些结果是公开可见数据
- 哪些部分拿不到，原因是什么
```

## 回答规则

- 明确区分“脚本返回的事实”和“你的归纳”。
- 不要把原创、转发、回复混在一起；输出里有 `isRetweet`、`isReply`、`isQuoteStatus` 可用。
- 优先附 `tweetUrl`。
- 如果只查了部分页，明确说“这是前 N 页结果”或“这是从某个 cursor 继续拿到的结果”。
- `likes.createdAt` 是被点赞那条推文的发布时间，不是点赞动作发生时间。

## 失败处理

- 账号不存在：提示用户确认 handle。
- 同名歧义：先追问准确账号。
- 点赞不可见：如实说明，不要假装拿到了。
- 脚本报错：优先保留错误信息，再决定是否缩小页数或改查单一模式。
