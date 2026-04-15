#!/usr/bin/env python3
"""
批量修复脚本编码问题
"""
import os
import sys
from pathlib import Path


def fix_unicode_symbols(content):
    """修复内容中的Unicode符号"""
    # Unicode符号到ASCII替换的映射
    replacements = {
        # 状态符号
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARN]',
        'ℹ️': '[INFO]',

        # 工具/动作符号
        '🔧': '[TOOL]',
        '📁': '[DIR]',
        '📋': '[LIST]',
        '🚀': '[LAUNCH]',
        '🧪': '[TEST]',
        '📊': '[STATS]',
        '🎯': '[TARGET]',
        '📝': '[NOTE]',
        '🔍': '[SEARCH]',

        # 其他常见符号
        '👉': '[=>]',
        '👈': '[<=]',
        '⭐': '[STAR]',
        '🔥': '[HOT]',
        '💡': '[IDEA]',
        '🔄': '[REFRESH]',
        '📈': '[UP]',
        '📉': '[DOWN]',
    }

    for unicode_char, ascii_replacement in replacements.items():
        content = content.replace(unicode_char, ascii_replacement)

    return content


def add_encoding_header(content, file_path):
    """添加编码头部注释（如果需要）"""
    lines = content.split('\n')

    # 检查是否已有编码声明
    has_encoding = False
    for line in lines[:5]:  # 检查前5行
        if 'coding:' in line.lower() or 'encoding:' in line.lower():
            has_encoding = True
            break

    if not has_encoding:
        # 在shebang之后添加编码声明
        if lines and lines[0].startswith('#!'):
            lines.insert(1, '# -*- coding: utf-8 -*-')
        else:
            lines.insert(0, '# -*- coding: utf-8 -*-')

        # 添加编码问题说明注释
        comment = f'# 编码修复: {os.path.basename(file_path)} - 已替换Unicode符号避免Windows编码问题'
        if lines[0].startswith('#!'):
            lines.insert(2, comment)
        else:
            lines.insert(1, comment)

    return '\n'.join(lines)


def fix_script_file(file_path):
    """修复单个脚本文件"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"[ERROR] 文件不存在: {file_path}")
            return False

        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 修复Unicode符号
        content = fix_unicode_symbols(content)

        # 添加编码头部
        content = add_encoding_header(content, file_path)

        # 如果内容有变化，保存文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # 统计替换的符号
            changes = {}
            for line_num, (orig_line, new_line) in enumerate(zip(
                original_content.split('\n'), content.split('\n')
            ), 1):
                if orig_line != new_line:
                    # 查找被替换的符号
                    for symbol in ['✅', '❌', '⚠️', '🔧', '📁', '📋', '🚀', '🧪', '📊', '🎯']:
                        if symbol in orig_line and symbol not in new_line:
                            changes.setdefault(symbol, 0)
                            changes[symbol] += 1

            print(f"[OK] 已修复: {file_path}")
            if changes:
                changes_str = ', '.join([f"{k}×{v}" for k, v in changes.items()])
                print(f"      替换符号: {changes_str}")
            return True
        else:
            print(f"[INFO] 无需修复: {file_path} (无Unicode符号)")
            return True

    except Exception as e:
        print(f"[ERROR] 修复失败 {file_path}: {e}")
        return False


def find_python_scripts(directory):
    """查找目录中的所有Python脚本"""
    scripts = []
    directory = Path(directory)

    for pattern in ['*.py', '**/*.py']:
        for file_path in directory.glob(pattern):
            # 排除一些特殊文件
            if file_path.name in ['encoding_utils.py', 'fix_all_scripts.py']:
                continue
            scripts.append(str(file_path))

    return sorted(scripts)


def main():
    """主函数"""
    print("批量修复脚本编码问题")
    print("=" * 60)

    # 要修复的脚本列表（手动指定）
    manual_scripts = [
        "scripts/test_db_init.py",
        "scripts/init_db.py",
        "test_day1_modifications.py",
        "check_current_status.py",
        "run_test.py",
        "test_imports.py",
        "test_fix.py",
        "test_fastapi.py",
        "test_with_encoding.py",
    ]

    # 查找其他脚本
    current_dir = Path(__file__).parent
    all_scripts = find_python_scripts(current_dir)

    # 合并列表，去重
    scripts_to_fix = list(set(manual_scripts + all_scripts))

    print(f"找到 {len(scripts_to_fix)} 个脚本文件")
    print()

    # 修复脚本
    successful = 0
    failed = 0

    for script in scripts_to_fix:
        script_path = Path(script)
        if not script_path.is_absolute():
            script_path = current_dir / script_path

        if script_path.exists():
            if fix_script_file(script_path):
                successful += 1
            else:
                failed += 1
        else:
            print(f"[WARN] 跳过不存在文件: {script}")

    print()
    print("=" * 60)
    print("修复完成!")
    print(f"成功: {successful}, 失败: {failed}, 总计: {successful + failed}")

    if failed == 0:
        print("[OK] 所有脚本修复成功!")
    else:
        print("[WARN] 部分脚本修复失败，请检查错误信息")

    print()
    print("下一步:")
    print("1. 运行修复后的脚本测试:")
    print("   python scripts/test_db_init.py")
    print("   python scripts/init_db.py")
    print("2. 创建新脚本时使用安全模板:")
    print("   from encoding_utils import create_safe_script_template")
    print()
    print("更多信息请参考 ENCODING_SOLUTION.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断修复过程")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] 修复过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)