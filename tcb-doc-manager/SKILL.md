---
name: tcb-doc-manager
description: 管理 TCB 指令分类文档。用于：(1) 查找第一个未实现的 TCB 指令，当用户说"查找未实现指令"、"下一个待实现"、"/find-first-unimplemented-tcb"时触发；(2) 标记指令为已实现，当用户说"标记已实现"、"/mark-tcb-implemented"时触发；(3) 生成 API 文档并关联，当用户说"生成 API 文档"、"/generate-tcb-api-doc"时触发。
---

# TCB 文档管理

管理 TCB 指令分类文档的查询和更新。

## 配置

- **文档路径**: `/Users/jiangjiwei/Code/Docs/xthing-docs-validation/docs/tcb/TCB指令分类文档.md`
- **API 文档目录**: `/Users/jiangjiwei/Code/Docs/xthing-docs-validation/docs/tcb/api/`
- **脚本路径**: `~/.claude/skills/tcb-doc-manager/scripts/tcb_doc.py`

## 命令

### 1. 查找未实现指令

```bash
python3 ~/.claude/skills/tcb-doc-manager/scripts/tcb_doc.py find-unimplemented --limit 10
```

参数：
- `--limit, -n`: 返回数量限制，默认 10，0 表示返回所有

输出 JSON 包含 `instructions` 数组，每项有：`requestCommand`, `commandCode`, `description`, `docPath`, `category`, `lineNumber`

### 2. 标记已实现

```bash
python3 ~/.claude/skills/tcb-doc-manager/scripts/tcb_doc.py mark-implemented <指令名> <实现文件名>
```

示例：
```bash
python3 ~/.claude/skills/tcb-doc-manager/scripts/tcb_doc.py mark-implemented REQ_GET_TEMPTIME GetTempTimeProtocol.kt
```

### 3. 添加 API 文档链接

```bash
python3 ~/.claude/skills/tcb-doc-manager/scripts/tcb_doc.py add-api-link <指令名> <API文档路径>
```

示例：
```bash
python3 ~/.claude/skills/tcb-doc-manager/scripts/tcb_doc.py add-api-link REQ_GET_TEMPTIME ./api/GetTempTimeProtocol.md
```

### 4. 获取指令信息

```bash
python3 ~/.claude/skills/tcb-doc-manager/scripts/tcb_doc.py get-info <指令名>
```

## 工作流

### /find-first-unimplemented-tcb

1. 执行 `find-unimplemented` 命令
2. 展示结果给用户

### /mark-tcb-implemented

参数：`<指令名> <实现文件名>`

1. 执行 `mark-implemented` 命令
2. 报告结果

### /generate-tcb-api-doc

参数：`<Protocol文件路径>`

1. 读取协议文件，分析 Request/Response 类
2. 在 `/Users/jiangjiwei/Code/Docs/xthing-docs-validation/docs/tcb/api/` 生成 API 文档
3. 执行 `add-api-link` 命令关联到分类文档

**API 文档模板参考**：见项目中 `/Users/jiangjiwei/Code/Kmp/main/bleDemo-third/.claude/commands/generate-tcb-api-doc.md`
