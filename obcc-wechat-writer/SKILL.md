---
name: obcc-wechat-writer
description: Write, rewrite, archive, preview, and publish WeChat public account articles in the user's ObCc repository (`~/Documents/ObCc/05_WeChat`) using the “程序杂念” style. Use when drafting or polishing公众号文章, aligning tone to past published articles, managing `_草稿` and `.assets`, reconstructing a published `mp.weixin.qq.com` article back into local Markdown, or using `wechat-publisher` to create previews and publish to the official draft box.
---

# ObCc WeChat Writer

Use this skill for公众号内容工作 in `~/Documents/ObCc/05_WeChat`.

## Scope

- Default `main_article`: use the formal main corpus `0001-009x`. Prioritize the recent mature voice `0087-0096`; use earlier articles only for brand intro, older CTA patterns, or historical context.
- Optional `ai_showcase`: only when the user is writing `1000-优秀AI 作品` style content. Read [references/modes.md](references/modes.md).
- Optional `weekly_review`: only when writing `2000-周记`. Read [references/modes.md](references/modes.md).
- Never use `9999-*` as core style reference.

## Always do

1. Work locally first. Draft under `~/Documents/ObCc/05_WeChat/_草稿`.
2. Keep a same-named `.assets` folder for screenshots or illustrations.
3. Use the main corpus `0001-0096` as the style source, and prioritize `0087-0096`.
4. Do not publish to the WeChat draft box until the user explicitly confirms.

## Default writing target

- Sound like the author is sharing a real attempt, not giving an official product brief.
- Start from a concrete trigger, observation, or test.
- Let the judgment appear early, then support it with experience, screenshots, steps, or layered reasoning.
- Keep paragraphs short and phone-friendly.
- Prefer direct, useful conclusions over neutral encyclopedic explanation.

## File rules

- Main articles: once finalized, move from `_草稿` to `~/Documents/ObCc/05_WeChat/00xx-标题.md`.
- If the filename or `.assets` path contains spaces, use angle-bracket Markdown image paths: `![](<./path with spaces.png>)` so both Typora and Obsidian render correctly.
- If an already-published WeChat article is missing locally, archive it back into ObCc with a numbered `.md` file plus local `.assets` copies.

## Main voice

- Warm first-person voice. It should feel like a technically capable friend talking, not a distant expert lecturing.
- Core temperament: practical, experience-driven, willing to tinker, willing to judge.
- Common connectors: `其实`、`不过`、`我觉得`、`没想到`、`于是`、`如果你也`、`这件事`。
- Subjectivity is allowed, but every judgment should be backed by a real scene, an experiment, or layered reasoning.

## Opening rules

- Start with a trigger, not a definition.
- In the first 1-3 paragraphs, establish at least one clear hook:
  - a new discovery
  - a real test result
  - a pain point the reader already knows
  - a contrarian or sharper judgment
- Optional brand opener:
  - `大家好，我是程序杂念，专注分享程序带来的便利。`
- Do not force the opener if it makes the article feel templated. In recent articles, it is often lighter or omitted.

## Tool article pattern

Use this shape by default:

1. Trigger scene
2. Why test it now
3. Say the result early
4. Show the test chain and evidence
5. Explain what changed and why it matters
6. Give steps, prompts, or links to reproduce
7. End with a light invite or a next experiment

Rules:

- Do not list functions first.
- Show one real task.
- Prefer hard details when available: version, time cost, token count, file size, screenshots, exact workflow.
- Include at least one imperfection, boundary, or failed attempt if it matters.

## Viewpoint article pattern

Use this shape when the article is mainly making a judgment:

1. Start from a concrete observation, discussion, or familiar problem
2. Reveal the core judgment within the first 20%
3. Push the argument layer by layer
4. Use mirrored comparisons:
   - `表面问题 vs 根源问题`
   - `会用的人 vs 不会用的人`
   - `现在 vs 未来`
   - `工具端 vs 人这一端`
5. End on an action frame, a sharper takeaway, or the next question

Rules:

- Prefer `不是 X，而是 Y` style re-framing when it is natural.
- Do not stay at shallow conclusions like `大家不重视`.
- If the claim is sharp, the reasoning must be concrete enough to carry it.

## Title rules

- Prefer one-glance value, tension, or stance.
- Common forms:
  - `我终于……`
  - `你需要的不是 X……`
  - `X 时代即将到来……`
  - number + concrete result
  - direct question or verdict
- Avoid vague titles like `关于……的一些思考` unless the user explicitly wants an older style.

## Ending rules

- Recent preferred ending: short, useful, and slightly open.
- Good ending patterns:
  - `如果你也……我觉得值得自己试一下`
  - `欢迎一起交流/讨论`
  - `下一篇我想继续聊……`
- Older heavy self-promo endings are historical patterns, not the current default.

## Workflow

### Default article flow

1. Determine the article mode.
   - Main article: `0001-009x`
   - AI showcase: `1000-优秀AI 作品`
   - Weekly review: `2000-周记`
2. Draft locally first under `~/Documents/ObCc/05_WeChat/_草稿`.
3. Create a same-named `.assets` folder if screenshots or illustrations are needed.
4. Write and revise locally. Keep the ObCc copy as the source of truth.
5. If local images exist, store them in the `.assets` folder and use relative Markdown paths.
6. If a path contains spaces, use `![](<./path with spaces.png>)`.
7. Create a preview with `wechat-publisher`.
8. If local images exist, upload them for preview.
9. If images do not exist yet, `wechat-publisher` can generate them first.
10. Return `preview_url` to the user.
11. Let the user review the preview URL.
12. Only after explicit confirmation:
    - publish to the WeChat draft box if asked
    - move the local file from `_草稿` into the formal directory
    - rename the `.assets` folder to the final article name if needed

### Recovering a published article into ObCc

If the user gives a public WeChat article link and wants it archived:

1. Extract title, publish time, body, and images from the published page.
2. Download images into a local `.assets` folder.
3. Create a numbered Markdown file in `~/Documents/ObCc/05_WeChat`.
4. Add `发布时间` and `原文链接` at the top if useful.
5. Use local image paths, not remote hotlinks, for long-term storage.

## Mode notes

### main_article

- Default mode.
- Use the main corpus `0001-009x`.
- Prioritize the recent mature voice `0087-0096`.
- Best for tool essays, practical walkthroughs, comparisons, and观点文.

### ai_showcase

Use only for `1000-优秀AI 作品`.

This series is not the same as the main公众号 voice. Treat it as a small template family:

- `short_card`
  - one opening line
  - prompt block
  - image group
  - short ending
- `expanded_prompt_feature`
  - title
  - two short descriptive paragraphs
  - `Base prompt`
  - English / Chinese prompt blocks
  - optional CTA
- `weekend_digest`
  - weekend / holiday opening
  - multiple `##` sections
  - each section shows one themed group
  - ending CTA

Do not let this series override the main文章 voice.

### weekly_review

Use only for `2000-周记`.

This branch is closer to:

- weekly recap
- 运营和个人状态复盘
- good news / bad news / next week focus

There are too few samples to learn a full free-form voice. Prefer using a direct weekly template rather than trying to statistically imitate the series.

### exclusions

- `9999-*` should not be used as training style references.
- Use them only as idea pool, memo pool, or unfinished drafts.

## Quick checklist

- Is the title specific and readable in one glance?
- Do the first 3 paragraphs explain why this is worth reading now?
- Is the middle built on real scenes, tests, or reasoning instead of feature dumping?
- Is the ending light, useful, and not over-operator-style?
- Has the local ObCc copy been updated before preview/publish?

## Avoid

- product manual tone
- pure parameter dumps
- giant taxonomies with weak payoff
- slogan endings
- copying the old fixed outro word for word
- pretending neutrality when the article clearly needs a judgment
- mixing `1000` or `2000` series style into main articles by default
