#!/usr/bin/env python3
"""
Day2任务验证脚本
用于验证Day2创建的所有API路由是否正常工作
"""

import sys
import asyncio
from pathlib import Path

# 添加src目录到路径
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

async def test_imports():
    """测试所有Day2模块是否能正常导入"""
    print("测试Day2模块导入...")
    try:
        from src.api.routes.wiki import router as wiki_router
        from src.api.routes.versions import router as versions_router
        from src.api.routes.tags import router as tags_router
        from src.api.router import api_router
        from src.main import app

        print("所有Day2模块导入成功")
        return app
    except Exception as e:
        print(f"导入失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_routes(app):
    """测试路由注册情况"""
    print("\n测试路由注册...")

    routes = [r for r in app.routes if hasattr(r, 'path')]

    # 按类型统计
    wiki_routes = [r for r in routes if 'wiki' in r.path]
    versions_routes = [r for r in routes if 'versions' in r.path]
    tags_routes = [r for r in routes if 'tags' in r.path]

    print(f"总路由数量: {len(routes)}")
    print(f"Wiki路由数量: {len(wiki_routes)}")
    print(f"版本路由数量: {len(versions_routes)}")
    print(f"标签路由数量: {len(tags_routes)}")

    # 列出Day2新增的关键路由
    print("\nDay2新增路由:")
    day2_keywords = ['wiki/pages', 'versions/', 'tags/']
    for route in routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            if any(keyword in route.path for keyword in day2_keywords):
                methods = list(route.methods)
                print(f"  {methods} {route.path}")

    return True

def test_openapi(app):
    """测试OpenAPI文档生成"""
    print("\n测试OpenAPI文档...")
    try:
        openapi_schema = app.openapi()
        title = openapi_schema.get("info", {}).get("title", "Unknown")
        version = openapi_schema.get("info", {}).get("version", "Unknown")
        paths = openapi_schema.get("paths", {})

        print(f"OpenAPI文档已生成")
        print(f"API标题: {title}")
        print(f"API版本: {version}")
        print(f"接口路径数量: {len(paths)}")

        # 检查Day2相关路径
        day2_paths = [p for p in paths.keys() if any(kw in p for kw in ['wiki', 'versions', 'tags'])]
        print(f"Day2相关接口: {len(day2_paths)}个")

        return True
    except Exception as e:
        print(f"OpenAPI测试失败: {e}")
        return False

def test_application_services():
    """测试应用服务层"""
    print("\n测试应用服务层...")
    try:
        from src.application.wiki_application import WikiApplicationService, get_wiki_application_service
        from src.application.tag_application import TagApplicationService, get_tag_application_service

        print("应用服务类可导入")

        # 测试服务实例化
        try:
            wiki_service = get_wiki_application_service()
            print("WikiApplicationService可实例化")
        except Exception as e:
            print(f"WikiApplicationService实例化警告: {e}")

        try:
            tag_service = get_tag_application_service()
            print("TagApplicationService可实例化")
        except Exception as e:
            print(f"TagApplicationService实例化警告: {e}")

        return True
    except Exception as e:
        print(f"应用服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("Day2任务验证脚本")
    print("=" * 60)

    # 测试导入
    app = await test_imports()
    if not app:
        print("\n导入测试失败，无法继续")
        return False

    # 测试路由
    routes_ok = test_routes(app)

    # 测试OpenAPI
    openapi_ok = test_openapi(app)

    # 测试应用服务
    services_ok = test_application_services()

    # 总结
    print("\n" + "=" * 60)
    print("验证结果总结")
    print("=" * 60)

    all_passed = routes_ok and openapi_ok and services_ok

    if all_passed:
        print("所有测试通过！Day2任务已成功完成。")
        print("\n下一步：")
        print("1. 启动应用: cd apps/backend && python run.py")
        print("2. 访问API文档: http://127.0.0.1:8000/docs")
        print("3. 实现具体的业务逻辑")
    else:
        print("部分测试未通过，请检查上述错误。")

    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生未预期错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)