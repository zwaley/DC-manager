#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行时测试脚本 - 动态添加路由进行测试
"""

import sys
sys.path.append('.')

import requests
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse

def runtime_test():
    """运行时动态测试"""
    print("=== 运行时动态测试开始 ===")
    
    # 1. 导入并获取应用实例
    try:
        import main
        app = main.app
        print(f"✓ 获取应用实例成功: {app.title}")
    except Exception as e:
        print(f"❌ 获取应用实例失败: {e}")
        return
    
    # 2. 动态添加一个测试路由
    print("\n2. 动态添加测试路由")
    
    @app.get("/runtime-test")
    async def runtime_test_route():
        return JSONResponse(content={"message": "Runtime test route works!", "timestamp": time.time()})
    
    print("✓ 已添加 /runtime-test 路由")
    
    # 3. 等待一下让路由生效
    print("\n3. 等待路由生效...")
    time.sleep(2)
    
    # 4. 测试新添加的路由
    print("\n4. 测试新添加的路由")
    try:
        response = requests.get("http://localhost:8009/runtime-test", timeout=5)
        if response.status_code == 200:
            print(f"✓ 动态路由测试成功: {response.json()}")
        else:
            print(f"❌ 动态路由测试失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 动态路由测试异常: {e}")
    
    # 5. 再次测试 /graph 路由
    print("\n5. 再次测试 /graph 路由")
    try:
        response = requests.get("http://localhost:8009/graph", timeout=5)
        if response.status_code == 200:
            print(f"✓ /graph 路由现在可以访问了！")
            print(f"  内容类型: {response.headers.get('content-type')}")
            print(f"  内容大小: {len(response.content)} 字节")
        else:
            print(f"❌ /graph 路由仍然无法访问: HTTP {response.status_code}")
            print(f"  响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"❌ /graph 路由测试异常: {e}")
    
    # 6. 检查所有路由
    print("\n6. 检查当前所有路由")
    from fastapi.routing import APIRoute
    
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                'path': route.path,
                'methods': list(route.methods),
                'name': route.name
            })
    
    # 查找相关路由
    graph_routes = [r for r in routes if '/graph' in r['path'] or 'test' in r['path']]
    
    print(f"找到 {len(graph_routes)} 个相关路由:")
    for route in graph_routes:
        print(f"  - {route['methods']} {route['path']} ({route['name']})")
    
    print("\n=== 运行时动态测试完成 ===")

if __name__ == "__main__":
    try:
        runtime_test()
    except Exception as e:
        print(f"❌ 运行时测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()