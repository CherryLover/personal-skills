---
name: preference
description: Manages user preferences and work habit settings with dual-location storage. ALWAYS stores preferences in BOTH CLAUDE.md ("## 工作流程偏好" section) AND the Memory MCP (entityType: "preference_setting") simultaneously. MANDATORY: When storing any preference, you MUST update both locations - never update only one. Use when the user explicitly expresses preference intent like "记住以后...", "下次自动...", "我喜欢用...", "设置成...", "remember to always...", "from now on use...". This is for work habits, tool configurations, interaction preferences, and workflow settings - NOT for general memory or project information.
---

# Preference Manager

## Overview

This skill manages user preferences and work habit settings with dual-location storage:
1. **CLAUDE.md** (`~/.claude/CLAUDE.md`) - "## 工作流程偏好" section
2. **Memory MCP** - Knowledge graph with entityType: "preference_setting"

**🚨 CRITICAL REQUIREMENT:** When storing ANY preference, you MUST update BOTH locations simultaneously. This is not optional.

## When to Use This Skill

Trigger this skill when the user expresses preference intent:

**Trigger Phrases:**
- "记住以后..." / "Remember to always..."
- "下次自动..." / "Next time automatically..."
- "我喜欢用..." / "I prefer to use..."
- "设置成..." / "Set it to..."
- "配置成..." / "Configure as..."
- "默认用..." / "Use by default..."

**Preference Categories:**
- **File Viewers**: Which applications to use for opening specific file types
- **Tool Usage**: Preferred tools for code search, git operations, etc.
- **Notification Rules**: When and how to send notifications
- **Interaction Style**: Language preference, verbosity level, proactive suggestions
- **Workflow Settings**: Commit message style, testing preferences, etc.

**NOT for:**
- General memory (facts, events, project info) - use natural conversation instead
- Project-specific knowledge - use kb-docs instead
- Temporary information - just keep in conversation

## Storage Strategy

**IMPORTANT:** Always store preferences in BOTH locations with appropriate formatting.

### CLAUDE.md Format

**Location:** `~/.claude/CLAUDE.md` → `## 工作流程偏好`

**Sub-sections:**
- `### 文件查看偏好` - File viewer preferences
- `### 通知规则` - Notification rules
- `### 工具使用偏好` - Tool usage preferences
- `### 交互偏好` - Interaction preferences
- `### 代码风格偏好` - Code style preferences
- `### Git 操作偏好` - Git workflow preferences

**Format Example:**
```markdown
## 工作流程偏好

### 文件查看偏好
- **Markdown 文件 (.md)**：使用 Typora 应用程序打开
  - 命令格式：`open -a Typora "文件路径"`
  - 设置时间：2026-01-23

### 通知规则
- **自动触发**：执行时间超过 3 分钟的任务自动发送通知
- **通知服务**：`/notify` skill
- **阈值**：3 分钟
```

### Memory MCP Format

**Entity Type:** `preference_setting`

**Observations Format:**
- Category (类别)
- Specific configuration (具体配置)
- Command or implementation detail (命令/实现细节)
- Timestamp (设置时间)

**Example:**
```javascript
{
  name: "Markdown文件查看器配置",
  entityType: "preference_setting",
  observations: [
    "文件类型: .md (Markdown)",
    "使用应用: Typora",
    "命令: open -a Typora \"文件路径\"",
    "类别: file_viewer",
    "设置时间: 2026-01-23"
  ]
}
```

## Workflow: Storing Preferences

When the user expresses a preference:

1. **Analyze the preference**
   - What category does it belong to?
   - What's the specific configuration?
   - Is there a command or implementation detail?

2. **REQUIRED: Update BOTH storage locations simultaneously**

   **Step A: Update CLAUDE.md (MANDATORY)**
   - Read the current CLAUDE.md file first
   - Locate the "## 工作流程偏好" section (create if not exists)
   - Identify the appropriate sub-section (### 文件查看偏好, ### 通知规则, etc.)
   - Use Edit tool to add/update the preference
   - Include relevant details: command, threshold, timestamp
   - Keep entries concise and scannable
   - This step is REQUIRED for all preference storage operations

   **Step B: Update Memory MCP (MANDATORY)**
   - Create entity with entityType: "preference_setting"
   - Name format: "{Category}配置" (e.g., "Markdown文件查看器配置")
   - Add detailed observations including:
     - Category (类别)
     - Configuration details (配置详情)
     - Command or implementation (命令/实现)
     - Timestamp (设置时间)
   - This step is REQUIRED for all preference storage operations

3. **Confirm to the user**
   - Briefly summarize the preference that was saved
   - Mention BOTH storage locations were updated
   - Example: "✅ 已保存偏好设置到 ~/.claude/CLAUDE.md 和向量数据库"

**CRITICAL RULE:** You MUST update BOTH CLAUDE.md AND Memory MCP when storing any preference. Never update only one location.

## Workflow: Retrieving Preferences

When the user asks about preferences:

1. **Understand the query**
   - Which category? (file viewer, notification, tool, etc.)
   - All preferences or specific ones?

2. **Check CLAUDE.md**
   - Read the "## 工作流程偏好" section
   - This is always loaded in context

3. **Search Memory MCP**
   - Use `search_nodes` with the query keyword
   - Filter by entityType: "preference_setting"
   - Example: search_nodes("Typora") or search_nodes("通知")

4. **Present results**
   - Organize by category
   - Show relevant configuration details
   - Format as readable markdown

## Examples

### Example 1: File Viewer Preference

**User:** "记住以后打开 md 文件都用 Typora"

**Actions:**
1. Update CLAUDE.md:
   ```markdown
   ## 工作流程偏好

   ### 文件查看偏好
   - **Markdown 文件 (.md)**：使用 Typora 应用程序打开
     - 命令格式：`open -a Typora "文件路径"`
     - 设置时间：2026-01-23
   ```

2. Update Memory MCP:
   ```javascript
   create_entities({
     name: "Markdown文件查看器配置",
     entityType: "preference_setting",
     observations: [
       "文件类型: .md (Markdown)",
       "使用应用: Typora",
       "命令: open -a Typora \"文件路径\"",
       "类别: file_viewer",
       "设置时间: 2026-01-23"
     ]
   })
   ```

3. Confirm: "✅ 已保存偏好：以后打开 .md 文件将使用 Typora"

### Example 2: Notification Rule

**User:** "超过 3 分钟的任务自动发送通知，不用问我"

**Actions:**
1. Update CLAUDE.md under "### 通知规则":
   ```markdown
   ### 通知规则
   - **自动触发**：执行时间超过 3 分钟的任务自动发送通知
   - **通知服务**：`/notify` skill
   - **阈值**：3 分钟
   - **无需确认**：自动发送，不询问用户
   ```

2. Update Memory MCP:
   ```javascript
   create_entities({
     name: "任务完成通知规则",
     entityType: "preference_setting",
     observations: [
       "触发条件: 任务执行时间超过 3 分钟",
       "通知方式: /notify skill",
       "自动触发: 是",
       "无需确认: 是",
       "类别: notification"
     ]
   })
   ```

### Example 3: Tool Usage Preference

**User:** "我喜欢用 LSP 工具搜索代码，不要用 Grep"

**Actions:**
1. Update CLAUDE.md under "### 工具使用偏好":
   ```markdown
   ### 工具使用偏好
   - **代码搜索优先级**：LSP > Grep
   - **LSP 优势**：精确定位、理解代码语义、跨文件分析
   - **Grep 使用场景**：仅在 LSP 不可用或需要正则搜索时使用
   ```

2. Update Memory MCP:
   ```javascript
   create_entities({
     name: "代码搜索工具偏好",
     entityType: "preference_setting",
     observations: [
       "优先级: LSP > Grep",
       "LSP 优势: 精确定位、语义理解、跨文件分析",
       "Grep 场景: LSP 不可用或正则搜索",
       "类别: tool_usage"
     ]
   })
   ```

### Example 4: Interaction Style

**User:** "默认用中文回复，除非我指定用英文"

**Actions:**
1. Update CLAUDE.md:
   ```markdown
   ### 交互偏好
   - **默认语言**：中文
   - **例外情况**：用户明确指定时使用英文
   ```

2. Update Memory MCP:
   ```javascript
   create_entities({
     name: "语言偏好设置",
     entityType: "preference_setting",
     observations: [
       "默认语言: 中文",
       "例外: 用户明确指定时使用英文",
       "类别: interaction"
     ]
   })
   ```

### Example 5: Retrieving Preferences

**User:** "我设置过哪些偏好？"

**Actions:**
1. Read CLAUDE.md "## 工作流程偏好" section
2. Use `search_nodes("")` or `read_graph` to get all preference_setting entities
3. Present organized summary:
   ```markdown
   ## 你的偏好设置

   ### 文件查看偏好
   - Markdown 文件：使用 Typora

   ### 通知规则
   - 超过 3 分钟的任务自动通知

   ### 工具使用偏好
   - 代码搜索：优先使用 LSP

   ### 交互偏好
   - 默认语言：中文
   ```

### Example 6: Searching Specific Preference

**User:** "我设置过什么文件查看器？"

**Actions:**
1. Search CLAUDE.md "### 文件查看偏好" section
2. Use `search_nodes("文件查看")` with entityType filter
3. Present results:
   ```markdown
   ## 文件查看偏好

   - **Markdown (.md)**: Typora
     - 命令: `open -a Typora "文件路径"`
   ```

### Example 7: Updating Existing Preference

**User:** "改成用 VSCode 打开 md 文件"

**Actions:**
1. Read current preference from CLAUDE.md
2. Update both locations (Edit CLAUDE.md + add_observations to Memory MCP)
3. Confirm: "✅ 已更新：Markdown 文件查看器从 Typora 改为 VSCode"

## Important Notes

- **🚨 ALWAYS UPDATE BOTH LOCATIONS** - When storing preferences, you MUST update BOTH CLAUDE.md AND Memory MCP. Never update only one location.
- **Always read CLAUDE.md first** before updating to check existing preferences
- **Use consistent category names** - file_viewer, notification, tool_usage, interaction, code_style, git_workflow
- **Keep CLAUDE.md concise** - it's loaded in every conversation
- **Use Memory MCP for searchability** - enables vector search by semantic meaning
- **Include timestamps** - helps track when preferences were set or updated
- **Maintain clear structure** - use sub-sections in CLAUDE.md for easy navigation
- **Dual-storage is mandatory** - Both locations serve complementary purposes

## Preference Categories Reference

| Category | CLAUDE.md Section | Example |
|----------|-------------------|---------|
| File Viewers | ### 文件查看偏好 | Markdown 文件用 Typora 打开 |
| Notifications | ### 通知规则 | 超过 3 分钟自动通知 |
| Tool Usage | ### 工具使用偏好 | 代码搜索优先用 LSP |
| Interaction | ### 交互偏好 | 默认中文回复 |
| Code Style | ### 代码风格偏好 | 使用单引号 |
| Git Workflow | ### Git 操作偏好 | 简洁 commit message |

## CLAUDE.md File Location

The file is located at: `~/.claude/CLAUDE.md`

If the "## 工作流程偏好" section doesn't exist, create it:

```markdown
## 工作流程偏好

### 文件查看偏好

### 通知规则

### 工具使用偏好

### 交互偏好
```

## Memory MCP Tools Reference

**For Storing:**
- `create_entities` - Create new preference entities (entityType: "preference_setting")
- `add_observations` - Add observations to existing preference entities

**For Retrieving:**
- `search_nodes` - Search preferences by keyword (e.g., "Typora", "通知", "LSP")
- `open_nodes` - Retrieve specific preference by exact name
- `read_graph` - Read all preferences (use sparingly)

**For Managing:**
- `delete_entities` - Remove preference entities
- `delete_observations` - Remove specific observations from preferences
