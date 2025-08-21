#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试路由注册情况的脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 导入main模块
    import main
    
    print("=== FastAPI应用路由检查 ===")
    print(f"应用对象: {main.app}")
    print(f"应用标题: {main.app.title}")
    print(f"应用版本: {main.app.version}")
    
    print("\n=== 所有注册的路由 ===")
    for i, route in enumerate(main.app.routes, 1):
        print(f"{i:2d}. {route.path:<30} {getattr(route, 'methods', 'N/A')}")
    
    print("\n=== 查找特定路由 ===")
    target_routes = ['/debug-routes', '/debug-lifecycle', '/test-route', '/lifecycle-management']
    
    for target in target_routes:
        found = False
        for route in main.app.routes:
            if route.path == target:
                print(f"✅ 找到路由: {target} - 方法: {getattr(route, 'methods', 'N/A')}")
                found = True
                break
        if not found:
            print(f"❌ 未找到路由: {target}")
    
    print("\n=== 路由总数 ===")
    print(f"总共注册了 {len(main.app.routes)} 个路由")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()