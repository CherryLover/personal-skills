#!/usr/bin/env python3
"""
Synology NAS 分享链接管理工具（通过 Synology Drive API）

Usage:
  nas_share.py init -u <username> -p <password> -s <otp_secret>  # 初始化配置
  nas_share.py share <path> [--password PWD]                      # 创建分享链接
  nas_share.py list                                               # 列出分享链接
  nas_share.py delete <link_id>                                   # 删除分享链接
  nas_share.py status                                             # 查看配置状态
"""

import argparse
import json
import os
import sys
import ssl
import urllib.request
import urllib.parse

try:
    import pyotp
except ImportError:
    print("ERROR: 需要 pyotp 库，请运行: pip3 install --user --break-system-packages pyotp", file=sys.stderr)
    sys.exit(1)

CONFIG_PATH = os.path.expanduser("~/.claude/nas-share-config.json")
NAS_BASE_URL = "https://work.anvizsys.com:6062"
LOCAL_MOUNT = "/Volumes/home"
NAS_HOME_PREFIX = "/home"
DRIVE_PREFIX = "/mydrive"


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def api_call(api, method, version, params=None, sid=None):
    """调用 Synology Web API"""
    data = {
        "api": api,
        "method": method,
        "version": str(version),
    }
    if params:
        data.update(params)
    if sid:
        data["_sid"] = sid

    url = f"{NAS_BASE_URL}/webapi/entry.cgi"

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    encoded = urllib.parse.urlencode(data)
    req = urllib.request.Request(url, data=encoded.encode(), method="POST")

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"success": False, "error": {"code": -1, "message": str(e)}}


AUTH_ERROR_CODES = {
    400: "账号或密码错误",
    401: "账号已禁用或临时锁定",
    402: "权限不足",
    403: "需要 OTP 验证码",
    404: "OTP 验证码错误",
    406: "必须使用双因素认证",
    407: "IP 被封禁",
    408: "密码已过期",
    409: "密码已过期",
    410: "需要修改密码",
}


def generate_otp(config):
    """从保存的 secret 生成当前 TOTP 验证码"""
    secret = config.get("otp_secret")
    if not secret:
        return None
    return pyotp.TOTP(secret).now()


def login(config):
    """登录 Synology 获取 session ID（DSM 7 两步认证，全自动）"""
    params = {
        "account": config["username"],
        "passwd": config["password"],
        "enable_device_token": "yes",
        "device_name": "claude-code-nas-share",
    }

    # 优先用 device_id 跳过 OTP
    if config.get("device_id"):
        params["device_id"] = config["device_id"]

    result = api_call("SYNO.API.Auth", "login", 6, params)

    if result.get("success"):
        data = result["data"]
        if "did" in data:
            config["device_id"] = data["did"]
            save_config(config)
        return data.get("sid")

    error = result.get("error", {})
    code = error.get("code", "unknown")

    # DSM 7 两步认证：403 → 自动生成 OTP 完成第二步
    if code == 403:
        token = error.get("errors", {}).get("token", "")
        otp_code = generate_otp(config)

        if not token or not otp_code:
            print("ERROR: 需要 OTP 但无法自动生成（缺少 otp_secret 或 token）", file=sys.stderr)
            return None

        params2 = {
            "account": config["username"],
            "passwd": config["password"],
            "enable_device_token": "yes",
            "device_name": "claude-code-nas-share",
            "otp_code": otp_code,
            "token": token,
        }
        result2 = api_call("SYNO.API.Auth", "login", 6, params2)

        if result2.get("success"):
            data2 = result2["data"]
            if "did" in data2:
                config["device_id"] = data2["did"]
                save_config(config)
            return data2.get("sid")
        else:
            code2 = result2.get("error", {}).get("code", "unknown")
            msg2 = AUTH_ERROR_CODES.get(code2, "未知错误")
            print(f"ERROR: OTP 认证失败 — {msg2} (code: {code2})", file=sys.stderr)
            return None

    msg = AUTH_ERROR_CODES.get(code, "未知错误")
    print(f"ERROR: 登录失败 — {msg} (code: {code})", file=sys.stderr)
    return None


def logout(sid):
    """登出释放 session"""
    if sid:
        api_call("SYNO.API.Auth", "logout", 6, sid=sid)


def local_to_drive_path(path):
    """将本地挂载路径或 NAS 路径转换为 Synology Drive 路径

    本地路径: /Volumes/home/对外分享/file.pdf → /mydrive/对外分享/file.pdf
    NAS 路径: /home/对外分享/file.pdf → /mydrive/对外分享/file.pdf
    Drive 路径: /mydrive/对外分享/file.pdf → 不变
    """
    path = os.path.abspath(path) if not path.startswith("/mydrive") else path

    if path.startswith(LOCAL_MOUNT):
        return DRIVE_PREFIX + path[len(LOCAL_MOUNT):]
    if path.startswith(NAS_HOME_PREFIX + "/"):
        return DRIVE_PREFIX + path[len(NAS_HOME_PREFIX):]
    if path.startswith(DRIVE_PREFIX):
        return path
    return DRIVE_PREFIX + "/" + path


def get_file_id(sid, drive_path):
    """通过 Drive 路径获取文件 ID"""
    result = api_call(
        "SYNO.SynologyDrive.Files", "get", 2,
        {"path": json.dumps(drive_path)},
        sid=sid,
    )
    if result.get("success"):
        return result["data"].get("file_id")
    error = result.get("error", {})
    code = error.get("code", "unknown")
    msg = error.get("errors", {}).get("message", "") if isinstance(error.get("errors"), dict) else ""
    print(f"ERROR: 获取文件信息失败 (code: {code}) {msg}", file=sys.stderr)
    print(f"Drive 路径: {drive_path}", file=sys.stderr)
    return None


# ── 子命令 ──────────────────────────────────────────


def cmd_init(args):
    config = load_config()
    config["username"] = args.username
    config["password"] = args.password
    config["nas_url"] = NAS_BASE_URL
    if args.secret:
        config["otp_secret"] = args.secret
    save_config(config)
    print(f"配置已保存到 {CONFIG_PATH}")


def cmd_share(args):
    config = load_config()
    if not config.get("username"):
        print("ERROR: 请先运行 init 命令", file=sys.stderr)
        sys.exit(1)

    drive_path = local_to_drive_path(args.path)

    sid = login(config)
    if not sid:
        sys.exit(1)

    try:
        # Step 1: 获取文件 ID
        file_id = get_file_id(sid, drive_path)
        if not file_id:
            sys.exit(1)

        # Step 2: 创建分享链接
        result = api_call(
            "SYNO.SynologyDrive.Sharing", "create_link", 1,
            {"path": json.dumps(f"id:{file_id}")},
            sid=sid,
        )

        if result.get("success"):
            url = result["data"].get("url", "")
            print(f"分享链接: {url}")
            print(f"Drive 路径: {drive_path}")
            print(f"文件 ID: {file_id}")
        else:
            error = result.get("error", {})
            code = error.get("code", "unknown")
            print(f"ERROR: 创建分享链接失败 (code: {code})", file=sys.stderr)
            print(f"完整响应: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
    finally:
        logout(sid)


def cmd_list(args):
    config = load_config()
    if not config.get("username"):
        print("ERROR: 请先运行 init 命令", file=sys.stderr)
        sys.exit(1)

    sid = login(config)
    if not sid:
        sys.exit(1)

    try:
        result = api_call(
            "SYNO.SynologyDrive.Sharing", "list_link", 1,
            {"offset": "0", "limit": "100"},
            sid=sid,
        )

        if result.get("success"):
            items = result["data"].get("items", [])
            total = result["data"].get("total", len(items))
            print(f"共 {total} 个分享链接:\n")
            for item in items:
                link_id = item.get("link_id", "?")
                name = item.get("name", "?")
                url = item.get("url", "?")
                print(f"  [{link_id}] {name}")
                print(f"      链接: {url}")
                print()
            if not items:
                print("  (无)")
        else:
            error = result.get("error", {})
            print(f"ERROR: 获取列表失败 (code: {error.get('code', 'unknown')})", file=sys.stderr)
            print(f"完整响应: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
    finally:
        logout(sid)


def cmd_delete(args):
    config = load_config()
    if not config.get("username"):
        print("ERROR: 请先运行 init 命令", file=sys.stderr)
        sys.exit(1)

    sid = login(config)
    if not sid:
        sys.exit(1)

    try:
        result = api_call(
            "SYNO.SynologyDrive.Sharing", "delete_link", 1,
            {"link_id": json.dumps(args.id)},
            sid=sid,
        )

        if result.get("success"):
            print(f"分享链接 {args.id} 已删除")
        else:
            error = result.get("error", {})
            print(f"ERROR: 删除失败 (code: {error.get('code', 'unknown')})", file=sys.stderr)
    finally:
        logout(sid)


def cmd_status(args):
    """显示当前配置状态"""
    config = load_config()
    if not config:
        print("未初始化，请运行 init 命令")
        return

    print(f"NAS 地址:   {config.get('nas_url', NAS_BASE_URL)}")
    print(f"用户名:     {config.get('username', '未设置')}")
    print(f"密码:       {'已配置' if config.get('password') else '未设置'}")
    print(f"OTP Secret: {'已配置 (自动生成OTP)' if config.get('otp_secret') else '未设置'}")
    print(f"设备令牌:   {'已获取 (免OTP)' if config.get('device_id') else '未获取'}")
    print(f"API 模式:   Synology Drive Sharing")

    if config.get("username") and config.get("password"):
        sid = login(config)
        if sid:
            logout(sid)
            print(f"连接状态:   正常")
        else:
            print(f"连接状态:   登录失败")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synology NAS 分享链接管理（Synology Drive API）")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="初始化配置")
    p_init.add_argument("-u", "--username", required=True, help="NAS 用户名")
    p_init.add_argument("-p", "--password", required=True, help="NAS 密码")
    p_init.add_argument("-s", "--secret", default=None, help="OTP Secret (Base32)")

    p_share = sub.add_parser("share", help="创建分享链接")
    p_share.add_argument("path", help="文件或文件夹路径（本地挂载路径、NAS 路径或 Drive 路径）")
    p_share.add_argument("--password", default=None, help="为分享链接设置密码（暂不支持）")

    p_list = sub.add_parser("list", help="列出所有分享链接")

    p_delete = sub.add_parser("delete", help="删除分享链接")
    p_delete.add_argument("id", help="分享链接 ID（link_id）")

    p_status = sub.add_parser("status", help="查看当前配置和连接状态")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "share": cmd_share,
        "list": cmd_list,
        "delete": cmd_delete,
        "status": cmd_status,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
