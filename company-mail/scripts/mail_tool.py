#!/usr/bin/env python3
"""
公司邮件读取工具 - 统一入口
支持: list / read / search / folders / attachments
"""

import os
import sys
import json
import email
import argparse
from email.header import decode_header
from datetime import datetime, timedelta

# 硬编码配置（公司邮箱）
CONFIG = {
    'server': 'mail.anvizsys.com',
    'port': 993,
    'use_ssl': True,
    'user': 'jiangjiwei@xthings.com',
    'password': 'Se6p+*YQe?Q3',
}

def ensure_imapclient():
    try:
        from imapclient import IMAPClient
        return IMAPClient
    except ImportError:
        import subprocess
        # 尝试创建 skill 专属 venv 并安装
        venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv')
        if not os.path.exists(venv_dir):
            subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
        subprocess.check_call([pip_path, 'install', 'imapclient', '-q'])
        # 将 venv site-packages 加入 sys.path
        import glob
        site_pkgs = glob.glob(os.path.join(venv_dir, 'lib', 'python*', 'site-packages'))
        if site_pkgs:
            sys.path.insert(0, site_pkgs[0])
        from imapclient import IMAPClient
        return IMAPClient


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
        else:
            result.append(part)
    return ''.join(result)


def get_email_body(msg):
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition', ''))
            if 'attachment' in content_disposition:
                continue
            if content_type == 'text/plain':
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        body = payload.decode(charset)
                    except Exception:
                        body = payload.decode('utf-8', errors='ignore')
                    break
            elif content_type == 'text/html' and not body:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        body = payload.decode(charset)
                    except Exception:
                        body = payload.decode('utf-8', errors='ignore')
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or 'utf-8'
            try:
                body = payload.decode(charset)
            except Exception:
                body = payload.decode('utf-8', errors='ignore')
    return body


def get_attachment_names(msg):
    names = []
    if msg.is_multipart():
        for part in msg.walk():
            filename = part.get_filename()
            content_disposition = str(part.get('Content-Disposition', ''))
            if filename or 'attachment' in content_disposition:
                names.append(decode_str(filename) if filename else 'unnamed')
    return names


def connect():
    IMAPClient = ensure_imapclient()
    client = IMAPClient(CONFIG['server'], port=CONFIG['port'], ssl=CONFIG['use_ssl'])
    client.login(CONFIG['user'], CONFIG['password'])
    return client


def cmd_list(args):
    """列出最新邮件"""
    client = connect()
    folder = args.folder or 'INBOX'
    client.select_folder(folder)
    messages = client.search(['ALL'])
    total = len(messages)

    limit = args.limit or 10
    latest = messages[-limit:]
    latest.reverse()

    results = []
    for msg_id in latest:
        response = client.fetch([msg_id], ['RFC822', 'INTERNALDATE'])
        raw = response[msg_id][b'RFC822']
        msg = email.message_from_bytes(raw)
        subject = decode_str(msg.get('Subject', ''))
        from_addr = decode_str(msg.get('From', ''))
        date = msg.get('Date', '')
        body = get_email_body(msg)
        attachments = get_attachment_names(msg)
        results.append({
            'id': msg_id,
            'subject': subject,
            'from': from_addr,
            'date': date,
            'preview': body[:200].strip(),
            'has_attachments': len(attachments) > 0,
            'attachment_names': attachments,
        })

    client.logout()
    output = {
        'folder': folder,
        'total': total,
        'showing': len(results),
        'emails': results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_read(args):
    """读取指定邮件全文"""
    client = connect()
    folder = args.folder or 'INBOX'
    client.select_folder(folder)

    msg_id = args.id
    response = client.fetch([msg_id], ['RFC822', 'INTERNALDATE'])
    if msg_id not in response:
        print(json.dumps({'error': f'邮件 ID {msg_id} 不存在'}, ensure_ascii=False))
        client.logout()
        return

    raw = response[msg_id][b'RFC822']
    internal_date = response[msg_id][b'INTERNALDATE']
    msg = email.message_from_bytes(raw)

    subject = decode_str(msg.get('Subject', ''))
    from_addr = decode_str(msg.get('From', ''))
    to_addr = decode_str(msg.get('To', ''))
    cc_addr = decode_str(msg.get('Cc', ''))
    date = msg.get('Date', '')
    body = get_email_body(msg)
    attachments = get_attachment_names(msg)

    result = {
        'id': msg_id,
        'subject': subject,
        'from': from_addr,
        'to': to_addr,
        'cc': cc_addr,
        'date': date,
        'body': body,
        'has_attachments': len(attachments) > 0,
        'attachment_names': attachments,
    }
    client.logout()
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_search(args):
    """搜索邮件"""
    client = connect()
    folder = args.folder or 'INBOX'
    client.select_folder(folder)

    # 构建搜索条件
    criteria = []
    if args.subject:
        criteria.extend(['SUBJECT', args.subject])
    if args.sender:
        criteria.extend(['FROM', args.sender])
    if args.since:
        criteria.extend(['SINCE', args.since])
    if args.before:
        criteria.extend(['BEFORE', args.before])
    if args.unseen:
        criteria.append('UNSEEN')
    if not criteria:
        criteria = ['ALL']

    messages = client.search(criteria)
    # 最新的在前
    messages = list(reversed(messages))

    limit = args.limit or 20
    messages = messages[:limit]

    results = []
    for msg_id in messages:
        response = client.fetch([msg_id], ['RFC822', 'INTERNALDATE'])
        raw = response[msg_id][b'RFC822']
        msg = email.message_from_bytes(raw)
        subject = decode_str(msg.get('Subject', ''))
        from_addr = decode_str(msg.get('From', ''))
        date = msg.get('Date', '')
        body = get_email_body(msg)
        results.append({
            'id': msg_id,
            'subject': subject,
            'from': from_addr,
            'date': date,
            'preview': body[:200].strip(),
        })

    client.logout()
    output = {
        'folder': folder,
        'criteria': ' '.join(str(c) for c in criteria),
        'found': len(results),
        'emails': results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_folders(args):
    """列出所有文件夹及邮件数"""
    client = connect()
    folders = client.list_folders()
    results = []
    for flags, delimiter, name in folders:
        try:
            status = client.folder_status(name, ['MESSAGES', 'UNSEEN'])
            results.append({
                'name': name,
                'total': status[b'MESSAGES'],
                'unseen': status[b'UNSEEN'],
            })
        except Exception as e:
            results.append({'name': name, 'error': str(e)})
    client.logout()
    print(json.dumps({'folders': results}, ensure_ascii=False, indent=2))


def cmd_attachments(args):
    """查找带附件的邮件"""
    client = connect()
    folder = args.folder or 'INBOX'
    client.select_folder(folder)
    messages = client.search(['ALL'])

    limit = args.limit or 10
    found = []

    for msg_id in reversed(messages):
        response = client.fetch([msg_id], ['BODYSTRUCTURE', 'ENVELOPE'])
        envelope = response[msg_id][b'ENVELOPE']
        subject = decode_str(envelope.subject) if envelope.subject else '(无主题)'
        from_addr = envelope.from_[0] if envelope.from_ else None
        from_str = ''
        if from_addr:
            name = decode_str(from_addr.name) if from_addr.name else ''
            mailbox = from_addr.mailbox.decode() if from_addr.mailbox else ''
            host = from_addr.host.decode() if from_addr.host else ''
            from_str = f"{name} <{mailbox}@{host}>" if name else f"{mailbox}@{host}"

        bodystructure = response[msg_id][b'BODYSTRUCTURE']
        att_names = []

        def check_structure(struct):
            if isinstance(struct, tuple):
                if len(struct) > 8:
                    disposition = struct[8] if len(struct) > 8 else None
                    if disposition and isinstance(disposition, tuple):
                        disp_type = disposition[0]
                        if disp_type and disp_type.lower() == b'attachment':
                            if len(disposition) > 1 and disposition[1]:
                                params = disposition[1]
                                for j in range(0, len(params), 2):
                                    if params[j].lower() == b'filename':
                                        att_names.append(decode_str(params[j+1]))
                for item in struct:
                    if isinstance(item, (list, tuple)):
                        check_structure(item)

        check_structure(bodystructure)

        if att_names:
            found.append({
                'id': msg_id,
                'subject': subject,
                'from': from_str,
                'attachments': att_names,
            })
            if len(found) >= limit:
                break

    client.logout()
    print(json.dumps({'found': len(found), 'emails': found}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description='公司邮件读取工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # list
    p_list = subparsers.add_parser('list', help='列出最新邮件')
    p_list.add_argument('-n', '--limit', type=int, default=10, help='数量')
    p_list.add_argument('-f', '--folder', default='INBOX', help='文件夹')

    # read
    p_read = subparsers.add_parser('read', help='读取指定邮件')
    p_read.add_argument('id', type=int, help='邮件 ID')
    p_read.add_argument('-f', '--folder', default='INBOX', help='文件夹')

    # search
    p_search = subparsers.add_parser('search', help='搜索邮件')
    p_search.add_argument('-s', '--subject', help='按主题搜索')
    p_search.add_argument('--sender', help='按发件人搜索')
    p_search.add_argument('--since', help='起始日期 (DD-Mon-YYYY, 如 01-Jan-2026)')
    p_search.add_argument('--before', help='截止日期')
    p_search.add_argument('--unseen', action='store_true', help='仅未读')
    p_search.add_argument('-n', '--limit', type=int, default=20, help='数量')
    p_search.add_argument('-f', '--folder', default='INBOX', help='文件夹')

    # folders
    subparsers.add_parser('folders', help='列出所有文件夹')

    # attachments
    p_att = subparsers.add_parser('attachments', help='查找带附件的邮件')
    p_att.add_argument('-n', '--limit', type=int, default=10, help='数量')
    p_att.add_argument('-f', '--folder', default='INBOX', help='文件夹')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        'list': cmd_list,
        'read': cmd_read,
        'search': cmd_search,
        'folders': cmd_folders,
        'attachments': cmd_attachments,
    }
    commands[args.command](args)


if __name__ == '__main__':
    main()
