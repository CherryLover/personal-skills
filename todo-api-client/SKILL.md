---
name: todo-api-client
description: Manage Task Atlas todos through the deployed HTTP API instead of the web UI or MCP. Supports listing, creating, editing, subtasks, reparenting, completing, reopening, promoting, and deleting todo branches.
---

# Todo API Client

Use this skill when the user asks to query or operate the deployed Task Atlas todo system.

## Base configuration

- Base URL: `https://todo-worker.jiwzdj.workers.dev`
- Auth token: `798929348b4a290185afe55464b7b6d422683145`
- Query auth: append `?token=<Auth token>` to any route, including the web UI URL
- Preferred tool: `python3 /Users/jiangjiwei/.codex/skills/todo-api-client/scripts/todo_api.py ...`

## Preferred workflow

1. For read operations, start with `list` or `get`.
2. For creates and updates, prefer the bundled Python script over hand-written curl.
3. When the user says "子任务", use `subtask`.
4. When the user says "提升成顶级 todo", use `promote`.
5. When the user says "完成/重新打开/删除", use `complete` / `reopen` / `delete`.

## Common commands

```bash
python3 /Users/jiangjiwei/.codex/skills/todo-api-client/scripts/todo_api.py list
python3 /Users/jiangjiwei/.codex/skills/todo-api-client/scripts/todo_api.py create --title "整理产品路线图" --priority high --status doing
python3 /Users/jiangjiwei/.codex/skills/todo-api-client/scripts/todo_api.py subtask <parent_id> --title "补充验收标准"
python3 /Users/jiangjiwei/.codex/skills/todo-api-client/scripts/todo_api.py update <todo_id> --status blocked --priority critical
python3 /Users/jiangjiwei/.codex/skills/todo-api-client/scripts/todo_api.py complete <todo_id>
python3 /Users/jiangjiwei/.codex/skills/todo-api-client/scripts/todo_api.py promote <todo_id>
python3 /Users/jiangjiwei/.codex/skills/todo-api-client/scripts/todo_api.py delete <todo_id>
```

## Route semantics

- `GET /api/todos` - list current todo tree and flat items
- `POST /api/todos` - create root todo
- `GET /api/todos/:id` - fetch one todo
- `PATCH /api/todos/:id` - update a todo
- `DELETE /api/todos/:id` - soft delete the todo and all descendants
- `POST /api/todos/:id/subtasks` - create subtask under the given parent
- `POST /api/todos/:id/promote` - move a subtask to the root level
- `POST /api/todos/:id/complete` - mark done
- `POST /api/todos/:id/reopen` - reopen into `todo`

## Notes

- Every route also accepts `?token=<token>`, and the bundled script uses that mode by default.
- The API still accepts `Authorization: Bearer <token>`.
- Deadline payloads use either `YYYY-MM-DD` or `YYYY-MM-DDTHH:mm`.
- This skill is local-only because it intentionally includes the live auth token.
