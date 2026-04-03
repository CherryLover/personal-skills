#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.error
import urllib.request

BASE_URL = "https://todo-worker.jiwzdj.workers.dev"
API_TOKEN = "798929348b4a290185afe55464b7b6d422683145"


def build_due(args):
    if not args.due_date:
        return None, False
    if args.due_time:
        return f"{args.due_date}T{args.due_time}", True
    return args.due_date, False


def request_json(path, method="GET", payload=None):
    headers = {
        "User-Agent": "todo-api-client/1.0",
    }
    url = path + ("&" if "?" in path else "?") + "token=" + API_TOKEN
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE_URL + url, headers=headers, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        print(body or exc.reason, file=sys.stderr)
        raise SystemExit(exc.code)


def print_json(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def add_mutation_args(parser, *, require_title=False):
    parser.add_argument("--title", required=require_title)
    parser.add_argument("--description")
    parser.add_argument("--priority", choices=["low", "medium", "high", "critical"])
    parser.add_argument("--status", choices=["todo", "doing", "blocked", "done"])
    parser.add_argument("--due-date")
    parser.add_argument("--due-time")
    parser.add_argument("--parent-id")


def build_payload(args):
    payload = {}
    for name in ["title", "description", "priority", "status"]:
        value = getattr(args, name, None)
        if value is not None:
            payload[name] = value
    if getattr(args, "parent_id", None) is not None:
        payload["parentId"] = args.parent_id
    if args.due_date is not None:
        due_at, has_due_time = build_due(args)
        payload["dueAt"] = due_at
        payload["hasDueTime"] = has_due_time
    return payload


def main():
    parser = argparse.ArgumentParser(description="Task Atlas HTTP API client")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list")

    get_parser = sub.add_parser("get")
    get_parser.add_argument("todo_id")

    create_parser = sub.add_parser("create")
    add_mutation_args(create_parser, require_title=True)

    update_parser = sub.add_parser("update")
    update_parser.add_argument("todo_id")
    add_mutation_args(update_parser)

    subtask_parser = sub.add_parser("subtask")
    subtask_parser.add_argument("parent_id")
    add_mutation_args(subtask_parser, require_title=True)

    for name in ["complete", "reopen", "promote", "delete"]:
        single = sub.add_parser(name)
        single.add_argument("todo_id")

    args = parser.parse_args()

    if args.command == "list":
        print_json(request_json("/api/todos"))
        return

    if args.command == "get":
        print_json(request_json(f"/api/todos/{args.todo_id}"))
        return

    if args.command == "create":
        print_json(request_json("/api/todos", method="POST", payload=build_payload(args)))
        return

    if args.command == "update":
        print_json(request_json(f"/api/todos/{args.todo_id}", method="PATCH", payload=build_payload(args)))
        return

    if args.command == "subtask":
        payload = build_payload(args)
        payload.pop("parentId", None)
        print_json(request_json(f"/api/todos/{args.parent_id}/subtasks", method="POST", payload=payload))
        return

    if args.command == "complete":
        print_json(request_json(f"/api/todos/{args.todo_id}/complete", method="POST", payload={}))
        return

    if args.command == "reopen":
        print_json(request_json(f"/api/todos/{args.todo_id}/reopen", method="POST", payload={}))
        return

    if args.command == "promote":
        print_json(request_json(f"/api/todos/{args.todo_id}/promote", method="POST", payload={}))
        return

    if args.command == "delete":
        print_json(request_json(f"/api/todos/{args.todo_id}", method="DELETE"))
        return


if __name__ == "__main__":
    main()
