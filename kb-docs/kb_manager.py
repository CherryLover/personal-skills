#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库管理脚本 - 处理 .kb-docs/ 目录的文件操作
支持功能清单、开发经验、临时问题、计划的增删改查
"""

import os
import sys
import json
import argparse
import re
import getpass
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def generate_slug(text: str) -> str:
    """
    生成 URL 友好的 slug

    Args:
        text: 原始文本（可能包含中文）

    Returns:
        小写、用连字符分隔的 slug
    """
    # 移除特殊字符，保留字母、数字、空格、连字符
    text = re.sub(r'[^\w\s-]', '', text)
    # 转小写
    text = text.lower()
    # 将空格和多个连字符替换为单个连字符
    text = re.sub(r'[-\s]+', '-', text)
    # 移除首尾的连字符
    text = text.strip('-')
    return text


class KBManager:
    """知识库管理器"""

    def __init__(self, project_root: str, user_home: Optional[str] = None):
        self.project_root = Path(project_root).resolve()
        self.project_kb = self.project_root / ".kb-docs"

        # 用户级知识库（可选）
        if user_home:
            self.user_kb = Path(user_home).resolve() / ".claude" / ".kb-docs"
        else:
            self.user_kb = None

    def init_structure(self, scope: str = "project") -> Dict[str, any]:
        """
        初始化知识库目录结构

        Args:
            scope: "project" 或 "user"

        Returns:
            {"success": bool, "created": List[str], "message": str}
        """
        target = self.project_kb if scope == "project" else self.user_kb

        if not target:
            return {"success": False, "message": "未指定用户级知识库路径"}

        created_items = []

        # 创建主目录
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created_items.append(str(target))

        # 创建子目录
        subdirs = ["features", "issues", "notes"]
        for subdir in subdirs:
            dir_path = target / subdir
            if not dir_path.exists():
                dir_path.mkdir(exist_ok=True)
                created_items.append(str(dir_path))

        # 创建 .gitignore (仅项目级)
        if scope == "project":
            gitignore_path = target / ".gitignore"
            if not gitignore_path.exists():
                gitignore_content = "# 临时问题文件，不提交到版本控制\nissues/\n"
                gitignore_path.write_text(gitignore_content, encoding="utf-8")
                created_items.append(str(gitignore_path))

        # 创建初始索引文件
        self._create_index_file(target / "features" / "index.md",
                                "# 功能清单\n\n记录项目已实现的功能、入口、流程和关键文件。\n")
        self._create_index_file(target / "notes" / "index.md",
                                "# 开发笔记\n\n记录项目开发过程中的问题、解决方案和最佳实践。\n")

        return {
            "success": True,
            "created": created_items,
            "message": f"已初始化 {scope} 级知识库结构"
        }

    def _create_index_file(self, path: Path, initial_content: str):
        """创建索引文件（如果不存在）"""
        if not path.exists():
            path.write_text(initial_content, encoding="utf-8")

    def add_feature(self, data: Dict[str, any], scope: str = "project") -> Dict[str, any]:
        """
        添加功能记录

        Args:
            data: {
                "name": str,
                "tags": List[str],
                "description": str,
                "entry": str,
                "flow": List[str],
                "files": List[Dict[str, str]],  # [{"path": "", "desc": ""}, ...]
                "notes": Optional[str]
            }
            scope: "project" 或 "user"

        Returns:
            {"success": bool, "message": str, "duplicate": bool}
        """
        target = self.project_kb if scope == "project" else self.user_kb
        if not target:
            return {"success": False, "message": "未指定用户级知识库路径"}

        # 确保目录存在
        self.init_structure(scope)

        index_file = target / "features" / "index.md"

        # 检查重复
        if index_file.exists():
            content = index_file.read_text(encoding="utf-8")
            if f"## {data['name']}" in content:
                return {
                    "success": False,
                    "duplicate": True,
                    "message": f"功能 '{data['name']}' 已存在"
                }

        # 生成功能条目
        entry = self._format_feature_entry(data)

        # 追加到文件
        with index_file.open("a", encoding="utf-8") as f:
            f.write("\n" + entry + "\n")

        return {
            "success": True,
            "duplicate": False,
            "message": f"已添加功能记录: {data['name']}"
        }

    def _format_feature_entry(self, data: Dict[str, any]) -> str:
        """格式化功能条目"""
        lines = [
            f"## {data['name']}",
            f"- **标签**: {', '.join(data.get('tags', []))}",
            f"- **描述**: {data['description']}",
            f"- **入口**: {data['entry']}",
            "- **核心流程**:"
        ]

        for i, step in enumerate(data.get('flow', []), 1):
            lines.append(f"  {i}. {step}")

        lines.append("- **关键文件**:")
        for file_info in data.get('files', []):
            lines.append(f"  - `{file_info['path']}` - {file_info['desc']}")

        if data.get('notes'):
            lines.append(f"- **备注**: {data['notes']}")

        return "\n".join(lines)

    def add_note(self, data: Dict[str, any], scope: str = "project") -> Dict[str, any]:
        """
        添加开发经验

        Args:
            data: {
                "title": str,
                "tags": List[str],
                "problem": str,
                "solution": str,
                "files": List[str],
                "lessons": str
            }
            scope: "project" 或 "user"

        Returns:
            {"success": bool, "message": str}
        """
        target = self.project_kb if scope == "project" else self.user_kb
        if not target:
            return {"success": False, "message": "未指定用户级知识库路径"}

        # 确保目录存在
        self.init_structure(scope)

        index_file = target / "notes" / "index.md"

        # 生成笔记条目
        entry = self._format_note_entry(data)

        # 追加到文件
        with index_file.open("a", encoding="utf-8") as f:
            f.write("\n" + entry + "\n")

        return {
            "success": True,
            "message": f"已添加笔记记录: {data['title']}"
        }

    def _format_note_entry(self, data: Dict[str, any]) -> str:
        """格式化笔记条目"""
        today = datetime.now().strftime("%Y-%m-%d")

        lines = [
            f"## {data['title']}",
            f"- **日期**: {today}",
            f"- **标签**: {', '.join(data.get('tags', []))}",
            f"- **问题**: {data['problem']}",
            f"- **解决方案**: {data['solution']}"
        ]

        if data.get('files'):
            lines.append("- **相关文件**:")
            for file_path in data['files']:
                lines.append(f"  - `{file_path}`")

        lines.append(f"- **经验教训**: {data['lessons']}")

        return "\n".join(lines)

    def add_issue(self, data: Dict[str, any]) -> Dict[str, any]:
        """
        添加临时问题

        Args:
            data: {
                "title": str,
                "status": str,  # "🔴 阻塞" / "🟡 进行中"
                "goal": str,
                "context": str,
                "attempts": List[Dict],  # [{"name": "", "approach": "", "result": "", "findings": ""}, ...]
                "blocker": str,
                "discoveries": str,
                "next_steps": List[str],
                "files": List[Dict[str, str]]
            }

        Returns:
            {"success": bool, "message": str, "file_path": str}
        """
        # 确保目录存在
        self.init_structure("project")

        # 生成文件名（移除特殊字符）
        filename = "".join(c for c in data['title'] if c.isalnum() or c in (' ', '-', '_'))
        filename = filename.strip().replace(' ', '-') + ".md"
        file_path = self.project_kb / "issues" / filename

        # 生成问题文档
        content = self._format_issue_document(data)

        # 写入文件
        file_path.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "message": f"已保存问题文档: {filename}",
            "file_path": str(file_path)
        }

    def _format_issue_document(self, data: Dict[str, any]) -> str:
        """格式化问题文档"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            f"# {data['title']}",
            "",
            "## 状态",
            f"- 时间: {now}",
            f"- 状态: {data['status']}",
            "",
            "## 目标",
            data['goal'],
            "",
            "## 上下文",
            data['context'],
            "",
            "## 尝试记录",
            ""
        ]

        for i, attempt in enumerate(data.get('attempts', []), 1):
            lines.extend([
                f"### 方案 {i}: {attempt['name']}",
                f"- 思路: {attempt['approach']}",
                f"- 结果: {attempt['result']}",
                f"- 发现: {attempt['findings']}",
                ""
            ])

        lines.extend([
            "## 当前困境",
            data['blocker'],
            "",
            "## 关键发现",
            data['discoveries'],
            "",
            "## 下一步计划"
        ])

        for i, step in enumerate(data.get('next_steps', []), 1):
            lines.append(f"{i}. {step}")

        lines.extend([
            "",
            "## 相关文件"
        ])

        for file_info in data.get('files', []):
            lines.append(f"- `{file_info['path']}` - {file_info['desc']}")

        return "\n".join(lines)

    def check_claude_md(self) -> Dict[str, any]:
        """
        检查项目的 CLAUDE.md 是否需要添加知识库说明

        Returns:
            {
                "exists": bool,           # CLAUDE.md 是否存在
                "has_kb_section": bool,   # 是否已有知识库说明
                "needs_update": bool,     # 是否需要更新
                "message": str
            }
        """
        claude_md = self.project_root / "CLAUDE.md"

        if not claude_md.exists():
            return {
                "exists": False,
                "has_kb_section": False,
                "needs_update": False,
                "message": "CLAUDE.md 不存在，无需更新"
            }

        content = claude_md.read_text(encoding="utf-8")

        # 检查是否已有知识库说明（通过搜索标题）
        has_kb_section = "## 项目知识库" in content

        return {
            "exists": True,
            "has_kb_section": has_kb_section,
            "needs_update": not has_kb_section,
            "message": "CLAUDE.md 已包含知识库说明" if has_kb_section else "CLAUDE.md 需要添加知识库说明"
        }

    def update_claude_md(self) -> Dict[str, any]:
        """
        向 CLAUDE.md 添加知识库说明

        Returns:
            {"success": bool, "message": str}
        """
        claude_md = self.project_root / "CLAUDE.md"

        if not claude_md.exists():
            return {
                "success": False,
                "message": "CLAUDE.md 不存在，无法更新"
            }

        content = claude_md.read_text(encoding="utf-8")

        # 检查是否已有知识库说明
        if "## 项目知识库" in content:
            return {
                "success": False,
                "message": "CLAUDE.md 已包含知识库说明，无需重复添加"
            }

        # 准备要添加的知识库说明模板
        kb_section = """
## 项目知识库

项目知识库采用本地化管理，所有文档存储在项目根目录的 `.kb-docs/` 隐藏文件夹中：

```
.kb-docs/
├── .gitignore         # 排除 issues/ 目录
├── features/
│   └── index.md       # 功能清单
├── issues/            # 临时问题（不提交 Git）
└── notes/
    └── index.md       # 开发笔记
```

### 统一命令入口

**所有知识库操作通过一个命令完成**：`/kb-docs <action>`

支持的操作：
- `/kb-docs note` - 保存开发笔记到 notes/index.md
- `/kb-docs feature` - 记录功能实现到 features/index.md
- `/kb-docs issue` - 暂存问题到 issues/{问题}.md
- `/kb-docs query` - 查询知识库内容

所有文件操作由 Python 脚本自动化处理，确保格式一致、避免重复。

### 开发笔记

项目开发过程中积累的问题、解决方案和成功经验存储在：`.kb-docs/notes/index.md`

**查询优先级**：遇到问题或开始新任务时，**先使用 `/kb-docs query` 查询**，看是否有类似的解决方案：
1. 执行 `/kb-docs query` 搜索相关关键词
2. 如果有相关笔记，参考其解决方案
3. 避免重复踩坑，复用已验证的模式

**在以下情况应主动查阅笔记**：
- 开始实现新功能前，查找类似的实现经验
- 遇到问题或报错时，查找类似问题的解决方案
- 进行架构决策时，参考历史决策经验
- 实现项目特定功能时，查找已有的模式和最佳实践

**积累新笔记**：使用 `/kb-docs note` 命令将当前会话中有价值的经验保存到知识库

### 功能清单

项目已实现功能的清单、实现流程和关键文件记录在：`.kb-docs/features/index.md`

**查询优先级**：当用户询问某个功能的实现时，**必须先使用 `/kb-docs query` 查询**，再决定是否需要查看实际代码：
1. 执行 `/kb-docs query` 查找是否有该功能的记录
2. 如果有记录，基于记录的信息回答（入口、流程、关键文件）
3. 只有在需要更详细的实现细节时，再去查看记录中列出的关键文件

**在以下情况应主动查阅功能清单**：
- 用户询问"XX功能是怎么实现的"
- 用户询问"XX功能在哪里"
- 需要了解项目现有功能时
- 修改或扩展某个功能前，了解其实现路径
- 实现类似功能时，参考已有的实现方式

**记录新功能**：使用 `/kb-docs feature` 命令将当前会话中实现的功能记录到清单

### 临时问题暂存

当遇到无法立即解决的问题时，可以使用 `/kb-docs issue` 命令将调试状态和尝试过程保存到 `.kb-docs/issues/{问题}.md`

- 问题文件不会提交到 Git（被 `.kb-docs/.gitignore` 排除）
- 新会话时可以通过引用问题文件继续调试
- 问题解决后建议使用 `/kb-docs note` 将解决方案保存为笔记

## 跨项目知识库

对于通用的开发经验（如 Git 操作、Kotlin 技巧、架构设计等），也存储在用户级全局知识库中：`~/.claude/.kb-docs/`

- 执行 `/kb-docs note` 时，如果判定经验具有跨项目价值，会询问是否同时保存到全局知识库
- 全局知识库采用相同的目录结构：`features/`、`issues/`、`notes/`
"""

        # 追加到文件末尾
        with claude_md.open("a", encoding="utf-8") as f:
            f.write("\n" + kb_section)

        return {
            "success": True,
            "message": "已成功添加知识库说明到 CLAUDE.md"
        }

    def add_plan(self, data: Dict[str, any]) -> Dict[str, any]:
        """
        添加计划

        Args:
            data: {
                "title": str,
                "description": str,
                "tags": List[str],
                "priority": str,  # low/medium/high
                "type": str,      # file/directory
                "background": str,
                "goal": str,
                "discussion": List[Dict],  # [{"decision": "", "reason": ""}, ...]
                "steps": List[str],
                "tech_plan": str,
                "files": List[str],
                "risks": str,
                "acceptance": List[str],
                "references": List[str]
            }

        Returns:
            {"success": bool, "plan_id": str, "file_path": str, "message": str}
        """
        # 确保 plans 目录存在
        plans_dir = self.project_kb / "plans"
        plans_dir.mkdir(parents=True, exist_ok=True)

        # 使用 PlanIndexManager 添加到索引
        index_mgr = PlanIndexManager(plans_dir)
        result = index_mgr.add_plan(
            title=data["title"],
            description=data["description"],
            tags=data.get("tags", []),
            priority=data.get("priority", "medium"),
            plan_type=data.get("type", "file")
        )

        if not result["success"]:
            return result

        # 生成计划文件
        plan_id = result["plan_id"]
        path = result["path"]

        if data.get("type") == "directory":
            # 多文件计划：创建目录和 main.md
            plan_dir = plans_dir / path
            plan_dir.mkdir(exist_ok=True)
            content = self._format_plan_document(data, plan_id, is_main=True)
            file_path = plan_dir / "main.md"
        else:
            # 单文件计划
            content = self._format_plan_document(data, plan_id, is_main=False)
            file_path = plans_dir / path

        file_path.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "plan_id": plan_id,
            "file_path": str(file_path),
            "message": f"已创建计划 {plan_id}: {data['title']}"
        }

    def _format_plan_document(self, data: Dict[str, any], plan_id: str, is_main: bool = False) -> str:
        """格式化计划文档"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        owner = getpass.getuser()

        lines = [
            f"# {data['title']}",
            "",
            f"**ID**: {plan_id}  ",
            f"**状态**: 待开始  ",
            f"**优先级**: {data.get('priority', 'medium')}  ",
            f"**负责人**: {owner}  ",
            f"**创建时间**: {now}  ",
            f"**更新时间**: {now}  ",
            f"**标签**: {', '.join(data.get('tags', []))}",
            ""
        ]

        # 如果是多文件计划的主文件，添加文档结构说明
        if is_main:
            lines.extend([
                "## 文档结构",
                "本计划包含多个文档：",
                "- [main.md](main.md) - 总体规划（本文件）",
                "",
                "---",
                ""
            ])

        lines.extend([
            "## 背景",
            data.get("background", ""),
            "",
            "## 目标",
            data.get("goal", ""),
            ""
        ])

        # 讨论记录
        if data.get("discussion"):
            lines.append("## 讨论记录")
            for item in data["discussion"]:
                lines.append(f"- **{item['decision']}**")
                lines.append(f"  - 原因：{item['reason']}")
            lines.append("")

        # 实施步骤
        lines.append("## 实施步骤")
        for step in data.get("steps", []):
            lines.append(f"- [ ] {step}")
        lines.append("")

        # 技术方案
        if data.get("tech_plan"):
            lines.extend([
                "## 技术方案",
                data["tech_plan"],
                ""
            ])

        # 文件清单
        if data.get("files"):
            lines.append("## 文件清单")
            for file_path in data["files"]:
                lines.append(f"- `{file_path}`")
            lines.append("")

        # 风险和依赖
        if data.get("risks"):
            lines.extend([
                "## 风险和依赖",
                data["risks"],
                ""
            ])

        # 验收标准
        if data.get("acceptance"):
            lines.append("## 验收标准")
            for criterion in data["acceptance"]:
                lines.append(f"- [ ] {criterion}")
            lines.append("")

        # 参考资料
        if data.get("references"):
            lines.append("## 参考资料")
            for ref in data["references"]:
                lines.append(f"- {ref}")
            lines.append("")

        return "\n".join(lines)

    def get_plan_content(self, plan_id: str) -> Dict[str, any]:
        """
        获取计划内容

        Args:
            plan_id: 计划 ID

        Returns:
            {"success": bool, "content": str, "message": str}
        """
        plans_dir = self.project_kb / "plans"
        index_mgr = PlanIndexManager(plans_dir)

        plan = index_mgr.get_plan(plan_id)
        if not plan:
            return {
                "success": False,
                "message": f"未找到计划 {plan_id}"
            }

        # 读取文件内容
        if plan["type"] == "directory":
            file_path = plans_dir / plan["path"] / "main.md"
        else:
            file_path = plans_dir / plan["path"]

        if not file_path.exists():
            return {
                "success": False,
                "message": f"计划文件不存在: {file_path}"
            }

        content = file_path.read_text(encoding="utf-8")

        return {
            "success": True,
            "content": content,
            "plan": plan,
            "message": "成功读取计划内容"
        }

    def plan_to_feature(self, plan_id: str, feature_data: Optional[Dict[str, any]] = None) -> Dict[str, any]:
        """
        将计划转换为 feature 记录

        Args:
            plan_id: 计划 ID
            feature_data: feature 数据（可选）
                         如果为 None，返回计划信息供 Claude 处理
                         如果提供，执行转换

        Returns:
            {"success": bool, "plan": Dict, "message": str}
            或
            {"success": bool, "feature_id": str, "message": str}
        """
        plans_dir = self.project_kb / "plans"
        index_mgr = PlanIndexManager(plans_dir)

        # 获取计划信息
        plan = index_mgr.get_plan(plan_id)
        if not plan:
            return {
                "success": False,
                "message": f"未找到计划 {plan_id}"
            }

        # 检查状态
        if plan["status"] != "completed":
            return {
                "success": False,
                "message": f"计划 {plan_id} 状态为 {plan['status']}，必须是 completed 才能转换为 feature",
                "current_status": plan["status"]
            }

        # 如果没有提供 feature_data，返回计划信息供处理
        if feature_data is None:
            # 读取计划内容
            plan_content_result = self.get_plan_content(plan_id)
            if not plan_content_result["success"]:
                return plan_content_result

            return {
                "success": True,
                "mode": "prepare",
                "plan": plan,
                "content": plan_content_result["content"],
                "message": "已准备计划信息，等待用户确认"
            }

        # 执行转换：添加 feature 记录
        feature_result = self.add_feature(feature_data, scope="project")

        if not feature_result["success"]:
            return {
                "success": False,
                "message": f"添加 feature 失败: {feature_result['message']}"
            }

        # 归档计划
        archive_result = index_mgr.update_plan_status(plan_id, "archived")

        if not archive_result["success"]:
            return {
                "success": False,
                "message": f"feature 已添加，但归档计划失败: {archive_result['message']}"
            }

        return {
            "success": True,
            "mode": "execute",
            "feature_name": feature_data["name"],
            "plan_id": plan_id,
            "message": f"已将计划 {plan_id} 转换为 feature '{feature_data['name']}'，计划已归档"
        }


class PlanIndexManager:
    """计划索引管理器 - 管理 plans/index.json"""

    def __init__(self, plans_dir: Path):
        self.plans_dir = plans_dir
        self.index_file = plans_dir / "index.json"

    def _ensure_dir(self):
        """确保 plans 目录存在"""
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> Dict:
        """加载索引文件"""
        if not self.index_file.exists():
            return {"next_id": 1, "plans": []}

        try:
            with self.index_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # 索引文件损坏，返回空索引
            return {"next_id": 1, "plans": []}

    def _save_index(self, index: Dict):
        """保存索引文件"""
        self._ensure_dir()
        with self.index_file.open("w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def add_plan(self, title: str, description: str, tags: List[str],
                 priority: str = "medium", plan_type: str = "file") -> Dict:
        """
        添加新计划到索引

        Args:
            title: 计划标题
            description: 计划描述
            tags: 标签列表
            priority: 优先级 (low/medium/high)
            plan_type: 类型 (file/directory)

        Returns:
            {"success": bool, "plan_id": str, "path": str, "message": str}
        """
        index = self._load_index()

        # 生成计划 ID
        plan_id = str(index["next_id"]).zfill(3)
        index["next_id"] += 1

        # 生成 slug
        slug = generate_slug(title)

        # 生成路径
        if plan_type == "file":
            path = f"{plan_id}-{slug}.md"
        else:
            path = f"{plan_id}-{slug}/"

        # 获取当前用户
        owner = getpass.getuser()

        # 创建计划条目
        now = datetime.now().isoformat()
        plan = {
            "id": plan_id,
            "title": title,
            "slug": slug,
            "status": "pending",
            "priority": priority,
            "owner": owner,
            "created_at": now,
            "updated_at": now,
            "tags": tags,
            "type": plan_type,
            "path": path,
            "description": description
        }

        # 添加到索引
        index["plans"].append(plan)
        self._save_index(index)

        return {
            "success": True,
            "plan_id": plan_id,
            "path": path,
            "slug": slug,
            "message": f"已创建计划 {plan_id}: {title}"
        }

    def get_plan(self, plan_id: str) -> Optional[Dict]:
        """根据 ID 获取计划"""
        index = self._load_index()
        for plan in index["plans"]:
            if plan["id"] == plan_id:
                return plan
        return None

    def list_plans(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        列出计划

        Args:
            status_filter: 状态过滤 (pending/in_progress/completed/archived)
                          None 表示默认只显示 pending 和 in_progress

        Returns:
            计划列表
        """
        index = self._load_index()
        plans = index["plans"]

        # 默认过滤
        if status_filter is None:
            plans = [p for p in plans if p["status"] in ["pending", "in_progress"]]
        elif status_filter:
            plans = [p for p in plans if p["status"] == status_filter]

        return plans

    def update_plan_status(self, plan_id: str, status: str) -> Dict:
        """
        更新计划状态

        Args:
            plan_id: 计划 ID
            status: 新状态

        Returns:
            {"success": bool, "message": str}
        """
        index = self._load_index()

        for plan in index["plans"]:
            if plan["id"] == plan_id:
                plan["status"] = status
                plan["updated_at"] = datetime.now().isoformat()
                self._save_index(index)
                return {
                    "success": True,
                    "message": f"已将计划 {plan_id} 状态更新为 {status}"
                }

        return {
            "success": False,
            "message": f"未找到计划 {plan_id}"
        }

    def update_plan_metadata(self, plan_id: str, updates: Dict) -> Dict:
        """
        更新计划元数据

        Args:
            plan_id: 计划 ID
            updates: 要更新的字段

        Returns:
            {"success": bool, "message": str}
        """
        index = self._load_index()

        for plan in index["plans"]:
            if plan["id"] == plan_id:
                # 允许更新的字段
                allowed_fields = ["title", "description", "tags", "priority"]
                for key, value in updates.items():
                    if key in allowed_fields:
                        plan[key] = value

                plan["updated_at"] = datetime.now().isoformat()
                self._save_index(index)
                return {
                    "success": True,
                    "message": f"已更新计划 {plan_id} 的元数据"
                }

        return {
            "success": False,
            "message": f"未找到计划 {plan_id}"
        }

    def delete_plan(self, plan_id: str) -> Dict:
        """
        删除计划

        Args:
            plan_id: 计划 ID

        Returns:
            {"success": bool, "message": str, "path": str}
        """
        index = self._load_index()

        for i, plan in enumerate(index["plans"]):
            if plan["id"] == plan_id:
                # 移除索引条目
                removed_plan = index["plans"].pop(i)
                self._save_index(index)

                return {
                    "success": True,
                    "message": f"已从索引中删除计划 {plan_id}",
                    "path": removed_plan["path"]
                }

        return {
            "success": False,
            "message": f"未找到计划 {plan_id}"
        }

    def search_plans(self, keyword: str) -> List[Dict]:
        """
        搜索计划

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的计划列表
        """
        index = self._load_index()
        keyword_lower = keyword.lower()

        results = []
        for plan in index["plans"]:
            # 在标题、描述、标签中搜索
            if (keyword_lower in plan["title"].lower() or
                keyword_lower in plan["description"].lower() or
                any(keyword_lower in tag.lower() for tag in plan["tags"])):
                results.append(plan)

        return results


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="知识库管理工具")
    parser.add_argument("action",
                        choices=["init", "add-feature", "add-note", "add-issue",
                                "check-claude-md", "update-claude-md",
                                "plan-add", "plan-list", "plan-get", "plan-update",
                                "plan-status", "plan-archive", "plan-delete",
                                "plan-search", "plan-to-feature"],
                        help="操作类型")
    parser.add_argument("--project-root", required=True, help="项目根目录")
    parser.add_argument("--user-home", help="用户主目录（可选）")
    parser.add_argument("--scope", default="project", choices=["project", "user", "all"],
                        help="作用域")
    parser.add_argument("--data", help="JSON 格式的数据（可选，不提供则从 stdin 读取）")
    parser.add_argument("--plan-id", help="计划 ID（用于 plan-get 等操作）")
    parser.add_argument("--status", help="状态过滤或新状态")
    parser.add_argument("--keyword", help="搜索关键词")

    args = parser.parse_args()

    # 创建管理器
    manager = KBManager(args.project_root, args.user_home)

    # 执行操作
    result = None

    if args.action == "init":
        result = manager.init_structure(args.scope)

    elif args.action == "add-feature":
        # 从命令行参数或 stdin 读取数据
        data = _get_json_data(args.data)
        if data is None:
            print(json.dumps({"success": False, "message": "缺少 JSON 数据"}))
            sys.exit(1)
        result = manager.add_feature(data, args.scope)

    elif args.action == "add-note":
        # 从命令行参数或 stdin 读取数据
        data = _get_json_data(args.data)
        if data is None:
            print(json.dumps({"success": False, "message": "缺少 JSON 数据"}))
            sys.exit(1)
        result = manager.add_note(data, args.scope)

    elif args.action == "add-issue":
        # 从命令行参数或 stdin 读取数据
        data = _get_json_data(args.data)
        if data is None:
            print(json.dumps({"success": False, "message": "缺少 JSON 数据"}))
            sys.exit(1)
        result = manager.add_issue(data)

    elif args.action == "check-claude-md":
        result = manager.check_claude_md()

    elif args.action == "update-claude-md":
        result = manager.update_claude_md()

    # Plan 相关命令
    elif args.action == "plan-add":
        data = _get_json_data(args.data)
        if data is None:
            print(json.dumps({"success": False, "message": "缺少 JSON 数据"}))
            sys.exit(1)
        result = manager.add_plan(data)

    elif args.action == "plan-list":
        plans_dir = manager.project_kb / "plans"
        index_mgr = PlanIndexManager(plans_dir)
        plans = index_mgr.list_plans(status_filter=args.status)
        result = {
            "success": True,
            "plans": plans,
            "count": len(plans)
        }

    elif args.action == "plan-get":
        if not args.plan_id:
            print(json.dumps({"success": False, "message": "缺少 --plan-id 参数"}))
            sys.exit(1)
        result = manager.get_plan_content(args.plan_id)

    elif args.action == "plan-update":
        # 更新计划内容（暂时先不实现，后续补充）
        result = {"success": False, "message": "plan-update 功能待实现"}

    elif args.action == "plan-status":
        if not args.plan_id or not args.status:
            print(json.dumps({"success": False, "message": "缺少 --plan-id 或 --status 参数"}))
            sys.exit(1)
        plans_dir = manager.project_kb / "plans"
        index_mgr = PlanIndexManager(plans_dir)
        result = index_mgr.update_plan_status(args.plan_id, args.status)

    elif args.action == "plan-archive":
        if not args.plan_id:
            print(json.dumps({"success": False, "message": "缺少 --plan-id 参数"}))
            sys.exit(1)
        plans_dir = manager.project_kb / "plans"
        index_mgr = PlanIndexManager(plans_dir)
        result = index_mgr.update_plan_status(args.plan_id, "archived")

    elif args.action == "plan-delete":
        if not args.plan_id:
            print(json.dumps({"success": False, "message": "缺少 --plan-id 参数"}))
            sys.exit(1)
        plans_dir = manager.project_kb / "plans"
        index_mgr = PlanIndexManager(plans_dir)
        delete_result = index_mgr.delete_plan(args.plan_id)

        if delete_result["success"]:
            # 同时删除文件
            file_path = plans_dir / delete_result["path"]
            if file_path.exists():
                if file_path.is_dir():
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()
                delete_result["message"] += f"，已删除文件 {delete_result['path']}"

        result = delete_result

    elif args.action == "plan-search":
        if not args.keyword:
            print(json.dumps({"success": False, "message": "缺少 --keyword 参数"}))
            sys.exit(1)
        plans_dir = manager.project_kb / "plans"
        index_mgr = PlanIndexManager(plans_dir)
        plans = index_mgr.search_plans(args.keyword)
        result = {
            "success": True,
            "plans": plans,
            "count": len(plans),
            "keyword": args.keyword
        }

    elif args.action == "plan-to-feature":
        if not args.plan_id:
            print(json.dumps({"success": False, "message": "缺少 --plan-id 参数"}))
            sys.exit(1)

        # 获取 feature 数据（可选）
        feature_data = _get_json_data(args.data) if args.data or not sys.stdin.isatty() else None

        result = manager.plan_to_feature(args.plan_id, feature_data)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


def _get_json_data(data_arg: Optional[str]) -> Optional[Dict]:
    """
    从命令行参数或 stdin 读取 JSON 数据

    Args:
        data_arg: 命令行 --data 参数的值

    Returns:
        解析后的 JSON 对象，失败返回 None
    """
    try:
        if data_arg:
            # 从命令行参数读取
            return json.loads(data_arg)
        elif not sys.stdin.isatty():
            # 从 stdin 读取（如果有管道输入）
            stdin_data = sys.stdin.read().strip()
            if stdin_data:
                return json.loads(stdin_data)
        return None
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "message": f"JSON 解析失败: {e}"}), file=sys.stderr)
        return None


if __name__ == "__main__":
    main()
