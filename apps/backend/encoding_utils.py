#!/usr/bin/env python3
"""
编码处理工具
解决Windows环境下控制台编码问题
"""
import os
import sys
import locale


def setup_console_encoding():
    """
    设置控制台编码以支持Unicode字符

    在Windows上，默认控制台编码可能是GBK等本地编码，
    这会导致打印Unicode字符时出现编码错误。
    此函数尝试设置合适的编码环境。
    """
    # 获取当前系统的默认编码
    system_encoding = locale.getpreferredencoding()

    # Windows常见问题编码
    problem_encodings = {'cp936', 'gbk', 'gb2312', 'gb18030'}

    if sys.platform == 'win32':
        # Windows系统，尝试设置UTF-8
        try:
            # 设置环境变量
            os.environ['PYTHONIOENCODING'] = 'utf-8'

            # 尝试设置控制台编码（如果可能）
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')

            print(f"[ENCODING] Windows系统检测到，已设置UTF-8编码", file=sys.stderr)
            return 'utf-8'

        except Exception as e:
            # 如果设置失败，回退到系统编码
            print(f"[ENCODING] 无法设置UTF-8编码，使用系统编码: {system_encoding} ({e})", file=sys.stderr)
            return system_encoding
    else:
        # 非Windows系统，通常支持UTF-8
        print(f"[ENCODING] 非Windows系统，编码: {system_encoding}", file=sys.stderr)
        return system_encoding


def safe_print(text, *args, **kwargs):
    """
    安全的打印函数，自动处理编码问题

    参数:
        text: 要打印的文本
        *args, **kwargs: 传递给print函数的其他参数
    """
    try:
        # 尝试正常打印
        print(text, *args, **kwargs)
    except UnicodeEncodeError as e:
        # 如果遇到编码错误，尝试替换问题字符
        if isinstance(text, str):
            # 替换常见的Unicode符号
            safe_text = text.replace('✅', '[OK]')
            safe_text = safe_text.replace('❌', '[ERROR]')
            safe_text = safe_text.replace('⚠️', '[WARN]')
            safe_text = safe_text.replace('🔧', '[TOOL]')
            safe_text = safe_text.replace('📁', '[DIR]')
            safe_text = safe_text.replace('📋', '[LIST]')
            safe_text = safe_text.replace('🚀', '[LAUNCH]')
            safe_text = safe_text.replace('🧪', '[TEST]')
            safe_text = safe_text.replace('📊', '[STATS]')
            safe_text = safe_text.replace('🎯', '[TARGET]')

            # 尝试再次打印
            try:
                print(safe_text, *args, **kwargs)
            except UnicodeEncodeError:
                # 如果还有问题，使用ASCII-only文本
                ascii_text = text.encode('ascii', 'ignore').decode('ascii')
                print(ascii_text, *args, **kwargs)
        else:
            # 如果不是字符串，直接打印
            print(text, *args, **kwargs)


def get_safe_status_symbols():
    """
    获取安全的状态符号（避免编码问题）

    返回:
        dict: 包含安全符号的字典
    """
    # 尝试使用Unicode符号
    try:
        # 测试Unicode字符是否可以打印
        '✅'.encode(sys.stdout.encoding or 'utf-8')
        return {
            'ok': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'tool': '🔧',
            'dir': '📁',
            'list': '📋',
            'launch': '🚀',
            'test': '🧪',
            'stats': '📊',
            'target': '🎯',
        }
    except (UnicodeEncodeError, AttributeError):
        # 如果不能打印Unicode，使用ASCII替代
        return {
            'ok': '[OK]',
            'error': '[ERROR]',
            'warning': '[WARN]',
            'info': '[INFO]',
            'tool': '[TOOL]',
            'dir': '[DIR]',
            'list': '[LIST]',
            'launch': '[LAUNCH]',
            'test': '[TEST]',
            'stats': '[STATS]',
            'target': '[TARGET]',
        }


def create_safe_script_template(script_path, description="Python脚本"):
    """
    创建安全的脚本模板，包含编码处理

    参数:
        script_path: 脚本文件路径
        description: 脚本描述
    """
    template = f'''#!/usr/bin/env python3
"""
{description}
包含编码问题处理
"""
import os
import sys

# 添加编码处理工具（如果可用）
try:
    from encoding_utils import setup_console_encoding, safe_print, get_safe_status_symbols
    # 设置编码
    encoding = setup_console_encoding()
    symbols = get_safe_status_symbols()
    OK = symbols['ok']
    ERROR = symbols['error']
    WARN = symbols['warning']
    # 使用safe_print替代print
    print = safe_print
except ImportError:
    # 如果没有编码工具，使用简单替代
    OK = "[OK]"
    ERROR = "[ERROR]"
    WARN = "[WARN]"
    # 设置环境变量
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')


def main():
    """主函数"""
    print(f"{{OK}} 脚本启动: {{sys.argv[0]}}")
    print(f"Python版本: {{sys.version}}")
    print(f"系统编码: {{sys.stdout.encoding}}")

    # 您的代码在这里...
    print(f"{{OK}} 脚本执行完成")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\\n{{WARN}} 脚本被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\\n{{ERROR}} 脚本执行出错: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
'''

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"[OK] 已创建安全脚本模板: {script_path}")


def fix_existing_script(script_path):
    """
    修复现有脚本的编码问题

    参数:
        script_path: 要修复的脚本路径
    """
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换常见的Unicode符号
        replacements = {
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARN]',
            '🔧': '[TOOL]',
            '📁': '[DIR]',
            '📋': '[LIST]',
            '🚀': '[LAUNCH]',
            '🧪': '[TEST]',
            '📊': '[STATS]',
            '🎯': '[TARGET]',
        }

        for unicode_char, ascii_replacement in replacements.items():
            content = content.replace(unicode_char, ascii_replacement)

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] 已修复脚本: {script_path}")
        return True

    except Exception as e:
        print(f"[ERROR] 修复脚本失败 {script_path}: {e}")
        return False


if __name__ == "__main__":
    # 测试编码设置
    encoding = setup_console_encoding()
    print(f"当前编码设置: {encoding}")

    # 显示可用的符号
    symbols = get_safe_status_symbols()
    print(f"可用符号: {symbols}")

    # 测试安全打印
    safe_print(f"{symbols['ok']} 安全打印测试")
    safe_print(f"{symbols['error']} 错误测试")
    safe_print(f"{symbols['warning']} 警告测试")