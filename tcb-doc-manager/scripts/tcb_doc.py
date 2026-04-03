#!/usr/bin/env python3
"""
TCB 指令分类文档管理工具

用于操作 TCB 指令分类文档，支持：
- 查找未实现的指令
- 标记指令为已实现
- 添加 API 文档链接
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# 默认文档路径
DEFAULT_DOC_PATH = "/Users/jiangjiwei/Code/Docs/xthing-docs-validation/docs/tcb/TCB指令分类文档.md"

# 表格列索引
COL_REQUEST_CMD = 0      # 请求指令
COL_CMD_CODE = 1         # 指令码
COL_RESPONSE_CMD = 2     # 响应指令
COL_RESPONSE_CODE = 3    # 响应码
COL_DESCRIPTION = 4      # 功能说明
COL_DOC_LINK = 5         # 文档链接
COL_IMPL_STATUS = 6      # xthing 项目实现
COL_MODELS = 7           # 实际使用型号
COL_UNIT_TEST = 8        # 单元测试


def parse_table_row(line: str) -> Optional[list]:
    """解析表格行，返回各列内容"""
    if not line.strip().startswith('|'):
        return None

    # 分割列
    parts = line.split('|')
    if len(parts) < 8:  # 至少需要基础的几列
        return None

    # 去掉首列空值，保留尾部
    cols = [p.strip() for p in parts[1:]]
    # 如果最后一个是空的，去掉它
    if cols and cols[-1] == '':
        cols = cols[:-1]

    # 跳过表头分隔行
    if cols and all(c.replace('-', '').replace(':', '').strip() == '' for c in cols):
        return None

    # 确保至少有 7 列（到 xthing 项目实现）
    if len(cols) < 7:
        return None

    # 补齐到 9 列
    while len(cols) < 9:
        cols.append('')

    return cols


def has_doc_link(doc_link_col: str) -> bool:
    """检查是否有详细文档链接"""
    return '📄 详细文档' in doc_link_col and './指令文档/' in doc_link_col


def is_implemented(impl_col: str) -> bool:
    """检查是否已实现（xthing 项目实现列非空）"""
    # 清理 HTML 标签和空白
    clean = re.sub(r'<[^>]+>', ' ', impl_col).strip()
    return len(clean) > 0


def has_api_link(impl_col: str) -> bool:
    """检查是否有 API 文档链接"""
    return '🔍 查看接口详情' in impl_col


def extract_doc_path(doc_link_col: str) -> Optional[str]:
    """提取文档路径"""
    match = re.search(r'\[📄 详细文档\]\(([^)]+)\)', doc_link_col)
    return match.group(1) if match else None


def find_unimplemented(doc_path: str, limit: int = 10) -> dict:
    """查找未实现的指令

    Args:
        doc_path: 文档路径
        limit: 返回数量限制，0 表示返回所有
    """
    try:
        content = Path(doc_path).read_text(encoding='utf-8')
    except FileNotFoundError:
        return {"success": False, "error": f"文档不存在: {doc_path}"}

    lines = content.split('\n')
    current_category = ""
    current_subcategory = ""
    results = []

    for i, line in enumerate(lines):
        # 解析分类标题
        if line.startswith('## ') and not line.startswith('## 📊'):
            current_category = line[3:].strip()
            continue
        if line.startswith('### '):
            current_subcategory = line[4:].strip()
            continue

        # 解析表格行
        cols = parse_table_row(line)
        if not cols or len(cols) < 9:
            continue

        # 跳过表头
        if cols[COL_REQUEST_CMD] == '请求指令':
            continue

        request_cmd = cols[COL_REQUEST_CMD]
        cmd_code = cols[COL_CMD_CODE]
        response_cmd = cols[COL_RESPONSE_CMD]
        response_code = cols[COL_RESPONSE_CODE]
        description = cols[COL_DESCRIPTION]
        doc_link = cols[COL_DOC_LINK]
        impl_status = cols[COL_IMPL_STATUS]

        # 检查：有文档链接 + 未实现
        if has_doc_link(doc_link) and not is_implemented(impl_status):
            doc_path_rel = extract_doc_path(doc_link)
            results.append({
                "requestCommand": request_cmd,
                "commandCode": cmd_code,
                "responseCommand": response_cmd,
                "responseCode": response_code,
                "description": description,
                "docPath": doc_path_rel,
                "category": current_category,
                "subcategory": current_subcategory,
                "lineNumber": i + 1
            })

            # 如果达到限制数量，停止
            if limit > 0 and len(results) >= limit:
                break

    if not results:
        return {
            "success": True,
            "found": False,
            "count": 0,
            "message": "所有有文档的指令都已实现"
        }

    return {
        "success": True,
        "found": True,
        "count": len(results),
        "instructions": results
    }


def mark_implemented(doc_path: str, instruction_name: str, impl_file: str) -> dict:
    """标记指令为已实现"""
    try:
        content = Path(doc_path).read_text(encoding='utf-8')
    except FileNotFoundError:
        return {"success": False, "error": f"文档不存在: {doc_path}"}

    lines = content.split('\n')
    found = False
    updated_line = None
    line_number = None

    for i, line in enumerate(lines):
        cols = parse_table_row(line)
        if not cols or len(cols) < 9:
            continue

        if cols[COL_REQUEST_CMD] == instruction_name:
            found = True
            line_number = i + 1

            # 检查是否已实现
            if is_implemented(cols[COL_IMPL_STATUS]):
                return {
                    "success": False,
                    "error": f"指令 {instruction_name} 已被标记为实现",
                    "currentStatus": cols[COL_IMPL_STATUS],
                    "lineNumber": line_number
                }

            # 更新实现状态列
            new_impl = f"已实现<br>{impl_file}"
            cols[COL_IMPL_STATUS] = new_impl

            # 重建行
            updated_line = '| ' + ' | '.join(cols) + ' |'
            lines[i] = updated_line
            break

    if not found:
        return {
            "success": False,
            "error": f"未找到指令: {instruction_name}"
        }

    # 写回文件
    Path(doc_path).write_text('\n'.join(lines), encoding='utf-8')

    return {
        "success": True,
        "instruction": instruction_name,
        "implFile": impl_file,
        "lineNumber": line_number,
        "message": f"已标记 {instruction_name} 为已实现"
    }


def add_api_link(doc_path: str, instruction_name: str, api_doc_path: str) -> dict:
    """添加 API 文档链接"""
    try:
        content = Path(doc_path).read_text(encoding='utf-8')
    except FileNotFoundError:
        return {"success": False, "error": f"文档不存在: {doc_path}"}

    lines = content.split('\n')
    found = False
    line_number = None

    for i, line in enumerate(lines):
        cols = parse_table_row(line)
        if not cols or len(cols) < 9:
            continue

        if cols[COL_REQUEST_CMD] == instruction_name:
            found = True
            line_number = i + 1

            # 检查是否已有 API 链接
            if has_api_link(cols[COL_IMPL_STATUS]):
                return {
                    "success": False,
                    "error": f"指令 {instruction_name} 已有 API 文档链接",
                    "currentStatus": cols[COL_IMPL_STATUS],
                    "lineNumber": line_number
                }

            # 检查是否已实现
            if not is_implemented(cols[COL_IMPL_STATUS]):
                return {
                    "success": False,
                    "error": f"指令 {instruction_name} 尚未标记为已实现，请先标记实现",
                    "lineNumber": line_number
                }

            # 解析当前实现状态
            current_impl = cols[COL_IMPL_STATUS]

            # 添加 ✅ 前缀（如果没有的话）
            if not current_impl.startswith('✅'):
                current_impl = '✅ ' + current_impl

            # 添加 API 链接
            api_link = f"[🔍 查看接口详情]({api_doc_path})"
            new_impl = f"{current_impl}<br>{api_link}"
            cols[COL_IMPL_STATUS] = new_impl

            # 重建行
            lines[i] = '| ' + ' | '.join(cols) + ' |'
            break

    if not found:
        return {
            "success": False,
            "error": f"未找到指令: {instruction_name}"
        }

    # 写回文件
    Path(doc_path).write_text('\n'.join(lines), encoding='utf-8')

    return {
        "success": True,
        "instruction": instruction_name,
        "apiDocPath": api_doc_path,
        "lineNumber": line_number,
        "message": f"已为 {instruction_name} 添加 API 文档链接"
    }


def get_instruction_info(doc_path: str, instruction_name: str) -> dict:
    """获取指令详细信息"""
    try:
        content = Path(doc_path).read_text(encoding='utf-8')
    except FileNotFoundError:
        return {"success": False, "error": f"文档不存在: {doc_path}"}

    lines = content.split('\n')
    current_category = ""
    current_subcategory = ""

    for i, line in enumerate(lines):
        # 解析分类标题
        if line.startswith('## ') and not line.startswith('## 📊'):
            current_category = line[3:].strip()
            continue
        if line.startswith('### '):
            current_subcategory = line[4:].strip()
            continue

        cols = parse_table_row(line)
        if not cols or len(cols) < 9:
            continue

        if cols[COL_REQUEST_CMD] == instruction_name:
            doc_path_rel = extract_doc_path(cols[COL_DOC_LINK])
            return {
                "success": True,
                "found": True,
                "instruction": {
                    "requestCommand": cols[COL_REQUEST_CMD],
                    "commandCode": cols[COL_CMD_CODE],
                    "responseCommand": cols[COL_RESPONSE_CMD],
                    "responseCode": cols[COL_RESPONSE_CODE],
                    "description": cols[COL_DESCRIPTION],
                    "docPath": doc_path_rel,
                    "implStatus": cols[COL_IMPL_STATUS],
                    "models": cols[COL_MODELS],
                    "unitTest": cols[COL_UNIT_TEST],
                    "category": current_category,
                    "subcategory": current_subcategory,
                    "lineNumber": i + 1,
                    "isImplemented": is_implemented(cols[COL_IMPL_STATUS]),
                    "hasApiLink": has_api_link(cols[COL_IMPL_STATUS]),
                    "hasDocLink": has_doc_link(cols[COL_DOC_LINK])
                }
            }

    return {
        "success": True,
        "found": False,
        "message": f"未找到指令: {instruction_name}"
    }


def main():
    parser = argparse.ArgumentParser(
        description='TCB 指令分类文档管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--doc-path',
        default=DEFAULT_DOC_PATH,
        help='TCB 指令分类文档路径'
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # find-unimplemented
    find_parser = subparsers.add_parser(
        'find-unimplemented',
        help='查找未实现的指令'
    )
    find_parser.add_argument(
        '--limit', '-n',
        type=int,
        default=10,
        help='返回数量限制，0 表示返回所有 (默认: 10)'
    )

    # mark-implemented
    mark_parser = subparsers.add_parser(
        'mark-implemented',
        help='标记指令为已实现'
    )
    mark_parser.add_argument('instruction', help='指令名称 (如 REQ_ADMIN_LOGIN)')
    mark_parser.add_argument('impl_file', help='实现文件名 (如 AdminLoginProtocol.kt)')

    # add-api-link
    link_parser = subparsers.add_parser(
        'add-api-link',
        help='添加 API 文档链接'
    )
    link_parser.add_argument('instruction', help='指令名称')
    link_parser.add_argument('api_path', help='API 文档相对路径 (如 ./api/AdminLoginProtocol.md)')

    # get-info
    info_parser = subparsers.add_parser(
        'get-info',
        help='获取指令详细信息'
    )
    info_parser.add_argument('instruction', help='指令名称')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    result = {}

    if args.command == 'find-unimplemented':
        result = find_unimplemented(args.doc_path, args.limit)
    elif args.command == 'mark-implemented':
        result = mark_implemented(args.doc_path, args.instruction, args.impl_file)
    elif args.command == 'add-api-link':
        result = add_api_link(args.doc_path, args.instruction, args.api_path)
    elif args.command == 'get-info':
        result = get_instruction_info(args.doc_path, args.instruction)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result.get('success', False):
        sys.exit(1)


if __name__ == '__main__':
    main()
