#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试应用路由 - 直接检查FastAPI应用对象
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 导入main模块
    import main
    print(f"✅ 成功导入main模块")
    print(f"App对象: {main.app}")
    print(f"App类型: {type(main.app)}")
    
    # 检查路由
    print("\n=== 检查路由 ===")
    routes = main.app.routes
    print(f"路由总数: {len(routes)}")
    
    for i, route in enumerate(routes, 1):
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', 'N/A')
            print(f"{i:2d}. {route.path:<30} {methods}")
    
    # 特别检查我们添加的路由
    print("\n=== 检查特定路由 ===")
    target_routes = ['/debug-routes', '/debug-lifecycle', '/test-route']
    
    for target in target_routes:
        found = False
        for route in routes:
            if hasattr(route, 'path') and route.path == target:
                print(f"✅ 找到路由: {target}")
                print(f"   方法: {getattr(route, 'methods', 'N/A')}")
                print(f"   端点: {getattr(route, 'endpoint', 'N/A')}")
                found = True
                break
        if not found:
            print(f"❌ 未找到路由: {target}")
    
    # 尝试直接调用路由函数
    print("\n=== 尝试直接调用路由函数 ===")
    try:
        # 检查是否有debug_routes函数
        if hasattr(main, 'debug_routes'):
            print("✅ 找到debug_routes函数")
            result = main.debug_routes()
            print(f"函数返回: {result}")
        else:
            print("❌ 未找到debug_routes函数")
    except Exception as e:
        print(f"❌ 调用函数失败: {e}")
        
except Exception as e:
    print(f"❌ 导入main模块失败: {e}")
    import traceback
    traceback.print_exc()