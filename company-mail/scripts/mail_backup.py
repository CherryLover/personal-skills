#!/usr/bin/env python3
"""
公司邮件增量备份脚本
- 下载所有文件夹的所有邮件和附件到本地目录
- 支持增量备份（manifest 记录已下载的邮件 ID）
- 每天运行只下载新邮件
- 邮件 .eml 文件 + 附件分离存储
"""

import os
import sys
import json
import re
import email
import glob
import hashlib
import argparse
import unicodedata
from email.header import decode_header
from datetime import datetime
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────
CONFIG = {
    'server': 'mail.anvizsys.com',
    'port': 993,
    'use_ssl': True,
    'user': 'jiangjiwei@xthings.com',
    'password': 'Se6p+*YQe?Q3',
}

# 备份根目录（本地）
BACKUP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backup')
# manifest 文件路径
MANIFEST_PATH = os.path.join(BACKUP_ROOT, 'manifest.json')
# iCloud 同步目录
ICLOUD_ROOT = os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs/MailBackup')


def ensure_imapclient():
    try:
        from imapclient import IMAPClient
        return IMAPClient
    except ImportError:
        import subprocess
        venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv')
        if not os.path.exists(venv_dir):
            subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
        subprocess.check_call([pip_path, 'install', 'imapclient', '-q'])
        import glob as _g
        site_pkgs = _g.glob(os.path.join(venv_dir, 'lib', 'python*', 'site-packages'))
        if site_pkgs:
            sys.path.insert(0, site_pkgs[0])
        from imapclient import IMAPClient
        return IMAPClient


def connect():
    IMAPClient = ensure_imapclient()
    client = IMAPClient(CONFIG['server'], port=CONFIG['port'], ssl=CONFIG['use_ssl'])
    client.login(CONFIG['user'], CONFIG['password'])
    return client


def decode_str(s):
    if s is None:
        return ''
    if isinstance(s, bytes):
        try:
            return s.decode('utf-8')
        except Exception:
            try:
                return s.decode('gbk')
            except Exception:
                return s.decode('utf-8', errors='ignore')
    decoded_parts = decode_header(s)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            if charset:
                try:
                    result.append(part.decode(charset))
                except Exception:
                    result.append(part.decode('utf-8', errors='ignore'))
            else:
                result.append(part.decode('utf-8', errors='ignore'))
        elif part:
            result.append(str(part))
    return ''.join(result)


def sanitize_filename(name, max_len=100):
    """清理文件名，移除不合法字符"""
    if not name:
        return 'unnamed'
    # 替换不合法字符
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    name = unicodedata.normalize('NFC', name)
    if len(name) > max_len:
        name = name[:max_len]
    return name.strip()


def get_email_meta(msg):
    """提取邮件元数据"""
    subject = decode_str(msg.get('Subject', ''))
    from_addr = decode_str(msg.get('From', ''))
    to_addr = decode_str(msg.get('To', ''))
    cc_addr = decode_str(msg.get('Cc', ''))
    date_str = msg.get('Date', '')
    message_id = msg.get('Message-ID', '')
    # 尝试解析日期
    try:
        date_parsed = email.utils.parsedate_to_datetime(date_str)
    except Exception:
        date_parsed = None

    return {
        'subject': subject,
        'from': from_addr,
        'to': to_addr,
        'cc': cc_addr,
        'date': date_str,
        'date_parsed': date_parsed.isoformat() if date_parsed else None,
        'message_id': message_id,
    }


def extract_attachments(msg, attachments_dir, counter):
    """提取邮件附件，返回附件信息列表"""
    attachments = []
    if not msg.is_multipart():
        return attachments

    att_idx = 0
    for part in msg.walk():
        content_disposition = str(part.get('Content-Disposition', ''))
        if 'attachment' not in content_disposition and not part.get_filename():
            continue

        filename = part.get_filename()
        if not filename:
            continue

        filename = decode_str(filename)
        # 避免重名
        if att_idx > 0:
            name_part, ext = os.path.splitext(filename)
            filename = f"{name_part}_{att_idx}{ext}"
        filename = sanitize_filename(filename, max_len=150)
        att_idx += 1

        payload = part.get_payload(decode=True)
        if payload is None:
            continue

        filepath = os.path.join(attachments_dir, filename)
        # 如果同名文件存在，加序号后缀
        base, ext = os.path.splitext(filepath)
        cnt = 1
        while os.path.exists(filepath):
            filepath = f"{base}_{cnt}{ext}"
            cnt += 1

        with open(filepath, 'wb') as f:
            f.write(payload)

        # 计算 MD5
        md5_hash = hashlib.md5(payload).hexdigest()

        attachments.append({
            'filename': os.path.basename(filepath),
            'size': len(payload),
            'md5': md5_hash,
            'content_type': part.get_content_type(),
        })
    return attachments


def save_email(client, folder_name, msg_id, backup_root):
    """保存单封邮件到本地目录"""
    response = client.fetch([msg_id], ['RFC822', 'INTERNALDATE'])
    if msg_id not in response:
        return None

    raw = response[msg_id][b'RFC822']
    msg = email.message_from_bytes(raw)

    meta = get_email_meta(msg)

    # 创建邮件目录
    folder_safe = sanitize_filename(folder_name, max_len=50)
    email_dir = os.path.join(backup_root, folder_safe, f"uid_{msg_id}")
    os.makedirs(email_dir, exist_ok=True)
    attachments_dir = os.path.join(email_dir, 'attachments')
    os.makedirs(attachments_dir, exist_ok=True)

    # 保存 .eml 文件
    eml_path = os.path.join(email_dir, 'email.eml')
    with open(eml_path, 'wb') as f:
        f.write(raw)

    # 提取附件
    atts = extract_attachments(msg, attachments_dir, 0)

    # 保存 meta.json
    meta['uid'] = int(msg_id)
    meta['folder'] = folder_name
    meta['attachments'] = atts
    meta['has_attachments'] = len(atts) > 0
    meta['downloaded_at'] = datetime.now().isoformat()

    meta_path = os.path.join(email_dir, 'meta.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return meta


def load_manifest():
    """加载 manifest，返回已下载的 {folder: {uid: True}}"""
    if not os.path.exists(MANIFEST_PATH):
        return {}
    try:
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 转换为 set
        result = {}
        for folder, items in data.items():
            result[folder] = set(str(uid) for uid in items)
        return result
    except Exception:
        return {}


def save_manifest(manifest):
    """保存 manifest"""
    data = {folder: list(uids) for folder, uids in manifest.items()}
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sync_to_icloud(local_root, icloud_root):
    """将本地备份同步到 iCloud（rsync 方式，增量同步）"""
    import shutil
    if not os.path.exists(icloud_root):
        os.makedirs(icloud_root)

    for item in os.listdir(local_root):
        src = os.path.join(local_root, item)
        dst = os.path.join(icloud_root, item)
        if item == 'manifest.json':
            # manifest 单独同步
            shutil.copy2(src, dst)
            continue
        if os.path.isdir(src):
            if not os.path.exists(dst):
                shutil.copytree(src, dst)
            else:
                # 增量同步子目录
                for sub in os.listdir(src):
                    s_src = os.path.join(src, sub)
                    s_dst = os.path.join(dst, sub)
                    if os.path.isdir(s_src):
                        if not os.path.exists(s_dst):
                            shutil.copytree(s_src, s_dst)
                        else:
                            for email_dir in os.listdir(s_src):
                                e_src = os.path.join(s_src, email_dir)
                                e_dst = os.path.join(s_dst, email_dir)
                                if not os.path.exists(e_dst):
                                    shutil.copytree(e_src, e_dst)
                    else:
                        if not os.path.exists(s_dst):
                            shutil.copy2(s_src, s_dst)


def backup_folder(client, folder_name, manifest, stats, dry_run=False):
    """备份单个文件夹"""
    try:
        client.select_folder(folder_name)
    except Exception as e:
        print(f"  ⚠ 无法访问文件夹 '{folder_name}': {e}")
        return

    messages = client.search(['ALL'])
    if not messages:
        print(f"  📭 '{folder_name}' 无邮件")
        return

    print(f"  📬 '{folder_name}': {len(messages)} 封邮件")

    if folder_name not in manifest:
        manifest[folder_name] = set()

    new_count = 0
    skip_count = 0

    for msg_id in messages:
        msg_id_str = str(msg_id)
        if msg_id_str in manifest[folder_name]:
            skip_count += 1
            continue

        if dry_run:
            continue

        meta = save_email(client, folder_name, msg_id, BACKUP_ROOT)
        if meta:
            manifest[folder_name].add(msg_id_str)
            new_count += 1
            print(f"    ✅ UID {msg_id}: {meta['subject'] or '(无主题)'}")

    stats['total'] += len(messages)
    stats['new'] += new_count
    stats['skipped'] += skip_count
    print(f"  → 新增 {new_count}, 跳过 {skip_count}")


def main():
    parser = argparse.ArgumentParser(description='公司邮件增量备份工具')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不下载')
    parser.add_argument('--icloud', action='store_true', help='同步到 iCloud')
    parser.add_argument('--folders-only', action='store_true', help='仅列出文件夹，不备份')
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"📧 公司邮件备份工具")
    print(f"{'='*60}")
    print(f"备份目录: {BACKUP_ROOT}")
    print(f"iCloud:   {ICLOUD_ROOT}")
    print(f"Manifest: {MANIFEST_PATH}")
    print()

    manifest = load_manifest()
    client = connect()

    try:
        folders = client.list_folders()

        if args.folders_only:
            print("📁 文件夹列表:")
            for flags, delimiter, name in folders:
                status_info = ''
                try:
                    status = client.folder_status(name, ['MESSAGES'])
                    count = status.get(b'MESSAGES', 0)
                    already = len(manifest.get(name, set()))
                    status_info = f"  ({count} 封, 已下载 {already})"
                except Exception:
                    status_info = ''
                print(f"  {'✓' if name in manifest else '○'} {name}{status_info}")
            return

        print("📁 开始备份所有文件夹...\n")
        stats = {'total': 0, 'new': 0, 'skipped': 0}

        # 按固定顺序处理（INBOX 优先）
        def folder_priority(name):
            if name.upper() == 'INBOX':
                return '0_' + name
            return '1_' + name

        sorted_folders = sorted(folders, key=lambda x: folder_priority(x[2]))

        for flags, delimiter, name in sorted_folders:
            print(f"[{name}]")
            backup_folder(client, name, manifest, stats, dry_run=args.dry_run)

        print()
        print(f"{'='*60}")
        print(f"✅ 备份完成！")
        print(f"   总邮件数: {stats['total']}")
        print(f"   本次新增: {stats['new']}")
        print(f"   已跳过:   {stats['skipped']}")
        print(f"{'='*60}")

        if not args.dry_run:
            save_manifest(manifest)

            if args.icloud:
                print(f"\n☁️  正在同步到 iCloud...")
                sync_to_icloud(BACKUP_ROOT, ICLOUD_ROOT)
                print(f"✅ iCloud 同步完成！")

    finally:
        client.logout()


if __name__ == '__main__':
    main()
