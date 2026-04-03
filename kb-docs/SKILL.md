---
name: kb-docs
description: |
  管理项目知识库（经验、功能、问题、计划），支持项目级和用户级作用域

  触发条件：
  - 用户输入 /kb-docs 命令（带参数 note/feature/issue/query/plan）
  - 完成功能实现、解决问题、需要暂存调试状态、或制定实施计划时
---

# 项目知识库管理工具 (kb-docs)

## 统一入口

**所有知识库操作通过一个命令完成**：`/kb-docs <action>`

支持的操作（action）：
- `note` - 保存开发笔记到 notes/index.md
- `feature` - 记录功能实现到 features/index.md
- `issue` - 暂存问题到 issues/{问题}.md
- `query` - **查询知识库（直接用 Grep 工具，不调用 Python 脚本）**
- `plan` - 管理计划（add/list/get/update/status/archive/delete/search/to-feature）

**注意**：
- 旧命令（`/kb-save`、`/kb-feature`、`/kb-issue`）已废弃，统一使用 `/kb-docs`
- **query 操作不使用 Python 脚本，直接用 Grep 工具搜索更快更灵活**

## Python 脚本自动化

**写入操作**（note/feature/issue）通过 Python 脚本 `kb_manager.py` 完成：
- 自动创建 `.kb-docs/` 目录结构
- 智能解析和更新 markdown 格式
- 避免重复条目、保持格式一致
- 处理边界情况（文件不存在、空内容等）

**查询操作**（query）直接使用 Grep 工具，更快更灵活：
- 支持正则表达式模糊匹配
- 自动扩展中英文同义词
- 实时搜索，无需启动 Python 进程

脚本位置：`~/.claude/skills/kb-docs/kb_manager.py`

## 目录结构

### 项目级知识库
位于项目根目录的 `.kb-docs/` 隐藏目录：

```
.kb-docs/
├── .gitignore         # 内容：issues/
├── features/
│   └── index.md       # 功能清单索引
├── issues/            # 临时问题（不提交 Git）
│   └── {问题}.md
└── notes/
    └── index.md       # 开发笔记索引
```

### 用户级知识库（跨项目）
位于用户目录的 `~/.claude/.kb-docs/`，结构相同：

```
~/.claude/.kb-docs/
├── features/
│   └── index.md       # 跨项目通用功能模式
├── issues/            # 跨项目问题（少用）
└── notes/
    └── index.md       # 跨项目笔记（Git、Kotlin 等通用技术）
```

---

## 命令 1: /kb-docs note - 保存开发笔记

### 使用场景
- 成功解决了一个棘手的问题后
- 完成了某个功能的实现，想记录实现路径
- 发现了某个坑或最佳实践
- 做出了重要的架构决策

### 执行流程

**1. 分析会话，提取关键信息**

识别以下类型的内容：
- 遇到的问题及解决方案
- 功能实现的关键步骤和决策
- 踩过的坑和规避方法
- 最佳实践和代码模式

提取以下字段：
```json
{
  "title": "简洁的标题描述",
  "tags": ["tag1", "tag2", "tag3"],
  "problem": "遇到了什么问题或要实现什么功能",
  "solution": "如何解决的，关键步骤是什么",
  "files": ["path/to/file1.kt", "path/to/file2.kt"],
  "lessons": "可复用的洞察，下次遇到类似情况的建议"
}
```

**2. 判断全局价值**

分析该经验是否适用于其他项目（跨项目通用性）。

**判断标准**：
- 关于 Git 操作、Kotlin 通用技巧、架构设计模式等 → 跨项目
- 关于本项目特定业务逻辑、设备协议、UI 实现等 → 项目级

如果是跨项目经验，询问用户：
> "这个经验看起来是跨项目通用的（关于 XXX），是否也添加到全局知识库 `~/.claude/.kb-docs/notes/index.md`？
> 1. 仅保存到项目级
> 2. 同时保存到全局库（推荐）"

**3. 调用 Python 脚本保存**

**使用 stdin 传递数据（推荐，避免命令行转义问题）**：

```bash
# 使用 heredoc 传递 JSON 数据（最稳定的方式）
cat <<'EOF' | python3 ~/.claude/skills/kb-docs/kb_manager.py add-note --project-root /path/to/project --scope project
{
  "title": "简洁的标题描述",
  "tags": ["tag1", "tag2"],
  "problem": "遇到了什么问题",
  "solution": "如何解决的",
  "files": ["path/to/file.kt"],
  "lessons": "可复用的经验"
}
EOF

# 如果用户同意，同时保存到全局库
cat <<'EOF' | python3 ~/.claude/skills/kb-docs/kb_manager.py add-note --project-root /path/to/project --user-home ~ --scope user
{...}
EOF
```

**注意**：
- **推荐使用 `cat <<'EOF'` heredoc 方式**，最稳定，支持任意复杂的 JSON
- 复杂数据必须用 stdin 传递，简单数据可以用 `--data` 参数

**4. 反馈结果**

告知用户保存成功，显示保存位置和条目标题。

### 标签规范（参考）
- **模块**: `tcb`, `mqtt`, `jsbridge`, `ble`, `cloud-sync`, `ui`
- **类型**: `bug-fix`, `feature`, `architecture`, `performance`, `pattern`
- **设备**: `checkpoint`, `bolt-n`, `fox`, `bright`, `switch`, `plug`
- **通用**: `全设备`, `跨平台`, `android`, `ios`, `desktop`

---

## 命令 2: /kb-docs feature - 记录功能清单

### 使用场景
- 完成新功能的开发后
- 梳理现有功能的实现路径
- 记录功能的入口、流程和关键文件

### 执行流程

**1. 分析会话，提取功能信息**

识别功能实现相关信息：
- 功能名称和描述
- 触发入口（UI、JsBridge、API 等）
- 核心流程
- 关键文件

提取以下字段：
```json
{
  "name": "功能名称",
  "tags": ["tag1", "tag2", "tag3"],
  "description": "一句话说明功能作用",
  "entry": "从哪里触发（UI 按钮 / JsBridge 命令 / API 调用等）",
  "flow": [
    "步骤一",
    "步骤二",
    "步骤三"
  ],
  "files": [
    {"path": "path/to/file1.kt", "desc": "作用说明"},
    {"path": "path/to/file2.kt", "desc": "作用说明"}
  ],
  "notes": "可选，补充说明"
}
```

**2. 检查重复**

调用 Python 脚本，脚本会自动检测是否已存在同名功能。

如果检测到重复：
```json
{
  "success": false,
  "duplicate": true,
  "message": "功能 'XXX' 已存在"
}
```

询问用户处理方式：
> "功能 'XXX' 已存在于知识库中，如何处理？
> 1. 保留原有记录，放弃新记录
> 2. 更新原有记录（覆盖）
> 3. 重命名新记录后添加"

**3. 调用 Python 脚本保存**

**使用 stdin 传递数据（推荐）**：

```bash
# 使用 heredoc 传递 JSON 数据
cat <<'EOF' | python3 ~/.claude/skills/kb-docs/kb_manager.py add-feature --project-root /path/to/project --scope project
{
  "name": "功能名称",
  "tags": ["tag1", "tag2"],
  "description": "功能描述",
  "entry": "触发入口",
  "flow": ["步骤1", "步骤2", "步骤3"],
  "files": [
    {"path": "path/to/file.kt", "desc": "作用说明"}
  ],
  "notes": "可选备注"
}
EOF
```

**注意**：
- **必须使用 heredoc 方式**，功能数据包含数组、对象嵌套，命令行传递会出错
- heredoc 格式清晰，易于编辑和维护

**4. 反馈结果**

告知用户保存成功，显示功能名称和文件路径。

### 标签规范（参考）
- **模块**: `tcb`, `mqtt`, `jsbridge`, `ble`, `cloud-sync`, `ui`
- **设备**: `checkpoint`, `bolt-n`, `fox`, `bright`, `switch`, `plug`
- **范围**: `全设备`, `跨平台`, `android-only`, `ios-only`

---

## 命令 3: /kb-docs issue - 暂存临时问题

### 使用场景
- 当前问题一时半会无法解决，需要暂存状态以便新会话继续
- 会话过长需要重开，但不想丢失上下文
- 记录调试过程中的尝试和发现

### 执行流程

**1. 分析会话，提取问题信息**

识别问题相关信息：
- 问题主题和目标
- 背景上下文
- 已尝试的方案和结果
- 当前困境
- 关键发现

提取以下字段：
```json
{
  "title": "问题主题",
  "status": "🔴 阻塞",
  "goal": "一句话描述要解决的问题",
  "context": "背景信息、涉及的文件/模块",
  "attempts": [
    {
      "name": "方案名",
      "approach": "思路",
      "result": "❌ 失败",
      "findings": "发现了什么"
    }
  ],
  "blocker": "卡在哪里？什么问题没解决？",
  "discoveries": "调试过程中发现的重要信息",
  "next_steps": ["下一步 1", "下一步 2"],
  "files": [
    {"path": "path/to/file", "desc": "说明"}
  ]
}
```

**2. 调用 Python 脚本保存**

**使用 stdin 传递数据（推荐）**：

```bash
# 使用 heredoc 传递 JSON 数据
cat <<'EOF' | python3 ~/.claude/skills/kb-docs/kb_manager.py add-issue --project-root /path/to/project
{
  "title": "问题主题",
  "status": "🔴 阻塞",
  "goal": "要解决的问题",
  "context": "背景信息",
  "attempts": [
    {
      "name": "方案名",
      "approach": "思路",
      "result": "❌ 失败",
      "findings": "发现了什么"
    }
  ],
  "blocker": "卡在哪里",
  "discoveries": "关键发现",
  "next_steps": ["下一步1", "下一步2"],
  "files": [
    {"path": "path/to/file", "desc": "说明"}
  ]
}
EOF
```

脚本会自动：
- 根据问题标题生成文件名（移除特殊字符，替换空格为 `-`）
- 创建 `.kb-docs/issues/{问题}.md` 文件
- 添加时间戳和状态标记

**注意**：
- **必须使用 heredoc 方式**，问题数据结构最复杂（多层嵌套）
- 包含 emoji 也能正常处理

**3. 反馈结果**

告知用户保存成功和文件路径：
> "已保存问题文档到：`.kb-docs/issues/{问题}.md`
> 新会话时可以说：'看看 .kb-docs/issues/{问题}.md 继续上次的问题'"

### 问题解决后的处理

当问题解决后：
1. 提示用户可以删除 issue 文件（因为已被 Git 忽略）
2. 建议使用 `/kb-docs note` 将解决方案保存为笔记

---

## 命令 4: /kb-docs query - 查询知识库

### 使用场景
- 开始新任务前，查找类似的实现经验
- 遇到问题时，搜索已有的解决方案
- 快速定位功能的实现位置

### 执行流程

**不使用 Python 脚本，直接用 Grep 工具查询更快更灵活！**

**1. 理解用户意图，扩展搜索关键词**

用户输入可能是中文或英文，需要自动扩展同义词：

例如用户说"蓝牙激活"：
- 扩展为多个关键词：`ble|bluetooth|active|activate|activation|蓝牙|激活`

常见扩展规则：
- **蓝牙** → ble, bluetooth
- **激活** → active, activate, activation
- **连接** → connect, connection
- **扫描** → scan, scanning
- **断开** → disconnect, disconnection
- **指令** → command, cmd
- **设备** → device
- **配置** → config, configuration
- **参数** → param, params, parameter
- **队列** → queue
- **缓存** → cache
- **超时** → timeout
- **重试** → retry

**2. 使用 Grep 工具搜索知识库**

使用正则表达式模糊匹配，搜索多个位置：

```bash
# 搜索项目级功能清单
Grep(pattern="ble|bluetooth|active|activate",
     path=".kb-docs/features/index.md",
     output_mode="content", -i=true, -C=2)

# 搜索项目级笔记
Grep(pattern="ble|bluetooth|active|activate",
     path=".kb-docs/notes/index.md",
     output_mode="content", -i=true, -C=2)

# 如果用户要求搜索全局库，还要搜索：
Grep(pattern="ble|bluetooth|active|activate",
     path="~/.claude/.kb-docs/features/index.md",
     output_mode="content", -i=true, -C=2)

Grep(pattern="ble|bluetooth|active|activate",
     path="~/.claude/.kb-docs/notes/index.md",
     output_mode="content", -i=true, -C=2)
```

**3. 展示结果并提供详情**

- 向用户展示匹配的功能/经验标题
- 简要说明匹配的位置（项目级/用户级）
- 询问用户是否需要查看详细内容
- 如果需要，使用 Read 工具读取完整条目

### 查询技巧

1. **多关键词搜索**：用 `|` 连接多个关键词（如 `active|activate|activation`）
2. **忽略大小写**：使用 `-i=true` 参数
3. **显示上下文**：使用 `-C=2` 显示匹配行前后 2 行
4. **先搜功能清单，再搜笔记**：features 是功能入口，notes 是经验总结
5. **根据用户意图决定搜索范围**：默认搜项目级，用户明确提到"通用"或"跨项目"时才搜全局库

---

## 初始化逻辑

首次执行任何命令时，Python 脚本会自动创建完整的目录结构：

```bash
python3 ~/.claude/skills/kb-docs/kb_manager.py init \
  --project-root /path/to/project \
  --scope project
```

创建的结构：
```
.kb-docs/
├── .gitignore         # 内容：issues/
├── features/
│   └── index.md       # 带初始标题
├── issues/            # 空目录
└── notes/
    └── index.md       # 带初始标题
```

## CLAUDE.md 自动更新

### 新功能：自动为项目添加知识库说明

当首次在项目中使用 kb-docs 时（执行 note/feature/issue 命令），应该主动检查项目的 CLAUDE.md 是否包含知识库说明，如果没有则询问用户是否添加。

### 执行流程

**1. 检查 CLAUDE.md 状态**

在执行任何写入操作（note/feature/issue）之前，先检查 CLAUDE.md：

```bash
python3 ~/.claude/skills/kb-docs/kb_manager.py check-claude-md \
  --project-root /path/to/project
```

返回结果：
```json
{
  "exists": true,
  "has_kb_section": false,
  "needs_update": true,
  "message": "CLAUDE.md 需要添加知识库说明"
}
```

**2. 询问用户是否更新**

如果 `needs_update` 为 `true`，询问用户：
> "检测到项目的 CLAUDE.md 中没有知识库使用说明。是否自动添加标准的知识库说明？
> 这将在 CLAUDE.md 末尾追加知识库的使用方法和最佳实践。
>
> 1. 是，自动添加（推荐）
> 2. 否，跳过"

**3. 执行更新**

如果用户同意，执行更新命令：

```bash
python3 ~/.claude/skills/kb-docs/kb_manager.py update-claude-md \
  --project-root /path/to/project
```

更新成功后返回：
```json
{
  "success": true,
  "message": "已成功添加知识库说明到 CLAUDE.md"
}
```

**4. 继续执行原命令**

更新 CLAUDE.md 后，继续执行用户原本的命令（note/feature/issue）。

### 添加的内容

更新后，CLAUDE.md 末尾会添加完整的知识库说明，包括：
- 目录结构说明
- 统一命令入口（/kb-docs note/feature/issue/query）
- 开发笔记的使用方法和最佳实践
- 功能清单的查询优先级
- 临时问题暂存说明
- 跨项目知识库说明

### 注意事项

1. **仅首次询问**：同一项目只在首次使用时检查一次，后续不再重复询问
2. **检测机制**：通过搜索 `## 项目知识库` 标题判断是否已有说明
3. **追加方式**：内容追加到 CLAUDE.md 末尾，不修改现有内容
4. **可选操作**：用户可以选择跳过，不影响 kb-docs 的正常使用
5. **手动更新**：如果用户后续想添加，可以单独运行 `update-claude-md` 命令

---

## 命令 5: /kb-docs plan - 计划管理

### 使用场景

- 与 Claude Code 讨论需求和实现方案
- 讨论清楚后写成结构化的计划文档
- 按照计划文档逐步执行
- 执行过程中可能需要更新计划
- 完成后可以归档或删除

### 目录结构

```
.kb-docs/plans/
├── index.json                    # JSON 索引（结构化管理）
├── 001-tcb-cloud-sync.md        # 单文件计划
└── 002-ble-refactor/            # 多文件计划
    ├── main.md                   # 主文件（必需）
    ├── architecture.md
    └── api-design.md
```

### index.json 索引结构

```json
{
  "next_id": 3,
  "plans": [
    {
      "id": "001",
      "title": "TCB 云同步功能",
      "slug": "tcb-cloud-sync",
      "status": "in_progress",
      "priority": "high",
      "owner": "jiangjiwei",
      "created_at": "2025-01-14T10:30:00",
      "updated_at": "2025-01-14T15:20:00",
      "tags": ["tcb", "cloud-sync"],
      "type": "file",
      "path": "001-tcb-cloud-sync.md",
      "description": "实现云端设备指令同步功能"
    }
  ]
}
```

### 计划状态流转

```
pending → in_progress → completed → archived
         ↓
      (deleted)
```

### 子命令列表

#### 1. plan add - 添加计划

**使用场景**：与 Claude 讨论后，将方案写成计划文档

**数据结构**：

```json
{
  "title": "计划标题（会自动生成 slug）",
  "description": "一句话描述",
  "tags": ["tag1", "tag2"],
  "priority": "high",  // low/medium/high
  "type": "file",      // file（单文件）或 directory（多文件）
  "background": "为什么要做这个功能？",
  "goal": "要达到什么效果？",
  "discussion": [
    {"decision": "决策1", "reason": "原因"}
  ],
  "steps": [
    "步骤1",
    "步骤2"
  ],
  "tech_plan": "技术方案说明",
  "files": [
    "path/to/file1.kt",
    "path/to/file2.kt"
  ],
  "risks": "风险和依赖说明",
  "acceptance": [
    "验收标准1",
    "验收标准2"
  ],
  "references": [
    "参考文档或链接"
  ]
}
```

**执行命令**：

```bash
cat <<'EOF' | python3 ~/.claude/skills/kb-docs/kb_manager.py plan-add --project-root /path/to/project
{...}
EOF
```

**返回结果**：

```json
{
  "success": true,
  "plan_id": "001",
  "file_path": "/path/.kb-docs/plans/001-tcb-cloud-sync.md",
  "message": "已创建计划 001: TCB 云同步功能"
}
```

#### 2. plan list - 列出计划

**默认行为**：只显示 `pending` 和 `in_progress` 的计划

**执行命令**：

```bash
# 默认列表（pending + in_progress）
python3 ~/.claude/skills/kb-docs/kb_manager.py plan-list --project-root /path/to/project

# 列出所有状态
python3 ~/.claude/skills/kb-docs/kb_manager.py plan-list --project-root /path/to/project --status all

# 只列出已完成
python3 ~/.claude/skills/kb-docs/kb_manager.py plan-list --project-root /path/to/project --status completed
```

**返回结果**：

```json
{
  "success": true,
  "plans": [
    {
      "id": "001",
      "title": "...",
      "status": "in_progress",
      ...
    }
  ],
  "count": 1
}
```

#### 3. plan get - 查看计划详情

**执行命令**：

```bash
python3 ~/.claude/skills/kb-docs/kb_manager.py plan-get --project-root /path/to/project --plan-id 001
```

**返回结果**：

```json
{
  "success": true,
  "content": "# 计划标题\n\n...",
  "plan": {
    "id": "001",
    "title": "...",
    ...
  },
  "message": "成功读取计划内容"
}
```

#### 4. plan update - 更新计划内容

**说明**：此功能待实现，目前可以手动编辑计划文件

#### 5. plan status - 更新状态

**执行命令**：

```bash
# 更新为进行中
python3 ~/.claude/skills/kb-docs/kb_manager.py plan-status \
  --project-root /path/to/project \
  --plan-id 001 \
  --status in_progress

# 更新为已完成
python3 ~/.claude/skills/kb-docs/kb_manager.py plan-status \
  --project-root /path/to/project \
  --plan-id 001 \
  --status completed
```

**可用状态**：`pending`, `in_progress`, `completed`, `archived`

#### 6. plan archive - 归档计划

**执行命令**：

```bash
python3 ~/.claude/skills/kb-docs/kb_manager.py plan-archive \
  --project-root /path/to/project \
  --plan-id 001
```

**效果**：将状态改为 `archived`，文件保留

#### 7. plan delete - 删除计划

**执行命令**：

```bash
python3 ~/.claude/skills/kb-docs/kb_manager.py plan-delete \
  --project-root /path/to/project \
  --plan-id 001
```

**效果**：从索引中删除，同时删除文件（单文件或整个目录）

#### 8. plan search - 搜索计划

**执行命令**：

```bash
python3 ~/.claude/skills/kb-docs/kb_manager.py plan-search \
  --project-root /path/to/project \
  --keyword mqtt
```

**搜索范围**：标题、描述、标签

#### 9. plan to-feature - 转换为 feature

**使用场景**：计划完成后，将其转换为 feature 记录

**两阶段流程**：

**阶段 1: 准备（不提供 feature 数据）**

```bash
python3 ~/.claude/skills/kb-docs/kb_manager.py plan-to-feature \
  --project-root /path/to/project \
  --plan-id 001
```

返回结果：
```json
{
  "success": true,
  "mode": "prepare",
  "plan": {
    "id": "001",
    "title": "...",
    "status": "completed",
    ...
  },
  "content": "# 计划完整内容...",
  "message": "已准备计划信息，等待用户确认"
}
```

**阶段 2: 执行（提供 feature 数据）**

```bash
cat <<'EOF' | python3 ~/.claude/skills/kb-docs/kb_manager.py plan-to-feature \
  --project-root /path/to/project \
  --plan-id 001
{
  "name": "功能名称",
  "tags": ["tag1", "tag2"],
  "description": "功能描述",
  "entry": "触发入口",
  "flow": ["步骤1", "步骤2"],
  "files": [
    {"path": "file.kt", "desc": "说明"}
  ],
  "notes": "从计划 001 转换而来"
}
EOF
```

返回结果：
```json
{
  "success": true,
  "mode": "execute",
  "feature_name": "功能名称",
  "plan_id": "001",
  "message": "已将计划 001 转换为 feature '功能名称'，计划已归档"
}
```

**执行流程**：
1. 检查计划状态（必须是 `completed`）
2. 如果没有 feature 数据，返回计划信息供 Claude 处理
3. Claude 询问用户实际实现与计划是否有变动
4. 基于用户反馈生成 feature 数据
5. 再次调用命令，提供 feature 数据
6. 添加 feature 记录
7. 自动将 plan 状态改为 `archived`

**错误处理**：
- 计划不存在 → 返回错误
- 计划状态不是 `completed` → 返回错误和当前状态
- feature 添加失败 → 返回错误，不归档计划

### 计划文件模板

**单文件计划**（`001-tcb-cloud-sync.md`）：

```markdown
# TCB 云同步功能

**ID**: 001
**状态**: 进行中
**优先级**: high
**负责人**: jiangjiwei
**创建时间**: 2025-01-14 10:30
**更新时间**: 2025-01-14 15:20
**标签**: tcb, cloud-sync, mqtt

## 背景
当前设备离线时无法接收指令，需要云端缓存机制

## 目标
实现从云端拉取离线指令并通过蓝牙执行

## 讨论记录
- **复用 shared-mqtt 模块**
  - 原因：避免重复代码，已有成熟的 MQTT 管理

## 实施步骤
- [ ] 实现 CloudSyncMqttService
- [ ] 实现 CommandAdapter
- [x] 集成 JsBridge

## 技术方案
采用分层架构：MQTT 层、适配层、编排层

## 文件清单
- `shared-biz/cloudsync/CloudSyncService.kt` - 核心服务
- `shared-mqtt/CloudSyncMqttClient.kt` - MQTT 客户端

## 风险和依赖
- 依赖 MQTT 服务器稳定性

## 验收标准
- [ ] 能从云端拉取任务列表
- [ ] 能执行 TCB 指令
- [x] 能上报执行结果

## 参考资料
- /docs/cloud-sync/architecture.md
```

**多文件计划的 main.md**：

```markdown
# BLE 连接队列重构

**ID**: 002
...（元信息同上）

## 文档结构
本计划包含多个文档：
- [main.md](main.md) - 总体规划（本文件）
- [architecture.md](architecture.md) - 架构设计
- [api-design.md](api-design.md) - API 设计

---

（后续结构同单文件）
```

### 使用最佳实践

1. **计划命名**：标题用英文或拼音，自动生成 slug
2. **多文件计划**：复杂方案才用多文件，必须包含 `main.md`
3. **状态管理**：及时更新状态，保持索引准确
4. **完成后处理**：
   - 标记为 `completed`
   - 询问用户是否转为 feature
   - 转换后自动归档
5. **查询 vs 搜索**：
   - `/kb-docs query` - 搜索 features 和 notes
   - `/kb-docs plan search` - 搜索 plans

### 注意事项

1. **plan-update 功能待实现**，目前可手动编辑计划文件
2. **plan-to-feature 已实现**，采用两阶段流程（准备 → 执行）
3. **slug 生成规则**：自动转小写、移除特殊字符、用连字符分隔
4. **并发安全**：单用户单会话，暂不考虑并发写入
5. **文件组织**：多文件计划主文件必须命名为 `main.md`
6. **转换条件**：只有 `completed` 状态的计划才能转为 feature

---

## 错误处理

如果 Python 脚本执行失败：
1. 显示脚本返回的错误信息
2. 提供手动操作的建议
3. 记录错误日志（如果需要）

## 注意事项

1. **目录优先级**：优先使用项目级 `.kb-docs/`，全局库仅用于跨项目经验
2. **Git 管理**：`.kb-docs/` 提交到项目 Git，`issues/` 被忽略，`plans/` 提交（包含 index.json）
3. **标签灵活**：标签仅供参考，不强制规范
4. **避免重复**：Python 脚本会自动检测重复功能记录
5. **查询优先**：
   - `/kb-docs query` - 搜索 features 和 notes（Grep 工具）
   - `/kb-docs plan search` - 搜索 plans（JSON 索引）
6. **职责分离**：Python 脚本负责写入和索引管理，查询用 Grep 或 JSON 索引
