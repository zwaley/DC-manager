#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度调试脚本 - 检查 FastAPI 应用的详细状态
"""

import sys
import os
sys.path.append('.')

def deep_debug():
    """深度调试 FastAPI 应用"""
    print("=== 深度调试开始 ===")
    
    # 1. 检查模块导入
    print("\n1. 检查模块导入状态")
    try:
        import main
        print(f"✓ main 模块导入成功")
        print(f"  模块文件路径: {main.__file__}")
        print(f"  模块修改时间: {os.path.getmtime(main.__file__)}")
    except Exception as e:
        print(f"❌ main 模块导入失败: {e}")
        return
    
    # 2. 检查 FastAPI 应用实例
    print("\n2. 检查 FastAPI 应用实例")
    try:
        app = main.app
        print(f"✓ FastAPI 应用实例获取成功")
        print(f"  应用类型: {type(app)}")
        print(f"  应用标题: {app.title}")
        print(f"  应用版本: {app.version}")
    except Exception as e:
        print(f"❌ FastAPI 应用实例获取失败: {e}")
        return
    
    # 3. 详细检查路由
    print("\n3. 详细检查路由注册")
    from fastapi.routing import APIRoute, Mount
    
    all_routes = []
    graph_routes = []
    
    def collect_routes(routes, prefix=""):
        for route in routes:
            if isinstance(route, APIRoute):
                full_path = prefix + route.path
                route_info = {
                    'path': full_path,
                    'methods': list(route.methods),
                    'name': route.name,
                    'endpoint': route.endpoint,
                    'endpoint_name': getattr(route.endpoint, '__name__', str(route.endpoint))
                }
                all_routes.append(route_info)
                
                if '/graph' in full_path:
                    graph_routes.append(route_info)
                    
            elif isinstance(route, Mount):
                # 递归处理挂载的路由
                collect_routes(route.routes, prefix + route.path)
    
    collect_routes(app.routes)
    
    print(f"总路由数: {len(all_routes)}")
    
    # 4. 专门检查 /graph 路由
    print("\n4. /graph 路由详细信息")
    if graph_routes:
        for route in graph_routes:
            print(f"✓ 找到路由: {route['methods']} {route['path']}")
            print(f"  端点函数: {route['endpoint_name']}")
            print(f"  端点对象: {route['endpoint']}")
            
            # 检查端点函数是否可调用
            if callable(route['endpoint']):
                print(f"  ✓ 端点函数可调用")
                
                # 尝试获取函数签名
                try:
                    import inspect
                    sig = inspect.signature(route['endpoint'])
                    print(f"  函数签名: {sig}")
                except Exception as e:
                    print(f"  ⚠️ 无法获取函数签名: {e}")
            else:
                print(f"  ❌ 端点函数不可调用")
    else:
        print("❌ 没有找到任何 /graph 相关路由")
    
    # 5. 检查路由表的完整性
    print("\n5. 路由表完整性检查")
    expected_routes = ['/graph', '/graph/{device_id}', '/graph_data/{device_id}']
    
    for expected in expected_routes:
        found = False
        for route in all_routes:
            if route['path'] == expected:
                found = True
                break
        
        if found:
            print(f"✓ {expected} - 已找到")
        else:
            print(f"❌ {expected} - 未找到")
    
    # 6. 检查是否存在路径模式冲突
    print("\n6. 路径模式冲突检查")
    path_patterns = {}
    for route in all_routes:
        path = route['path']
        methods = tuple(sorted(route['methods']))
        key = (path, methods)
        
        if key in path_patterns:
            print(f"⚠️ 发现重复路由: {path} {methods}")
            print(f"   第一个: {path_patterns[key]['endpoint_name']}")
            print(f"   第二个: {route['endpoint_name']}")
        else:
            path_patterns[key] = route
    
    # 7. 尝试直接调用路由函数
    print("\n7. 尝试直接调用 /graph 路由函数")
    graph_route = None
    for route in graph_routes:
        if route['path'] == '/graph' and 'GET' in route['methods']:
            graph_route = route
            break
    
    if graph_route:
        try:
            print(f"找到 /graph 路由函数: {graph_route['endpoint_name']}")
            
            # 尝试创建模拟请求来测试函数
            from fastapi import Request
            from unittest.mock import Mock
            
            # 创建模拟的 Request 对象
            mock_request = Mock(spec=Request)
            
            print("尝试调用路由函数...")
            # 注意：这里不能直接调用，因为需要依赖注入
            print("⚠️ 路由函数需要依赖注入，无法直接测试")
            
        except Exception as e:
            print(f"❌ 调用路由函数时出错: {e}")
    else:
        print("❌ 未找到 /graph GET 路由")
    
    print("\n=== 深度调试完成 ===")
    return all_routes, graph_routes

if __name__ == "__main__":
    try:
        all_routes, graph_routes = deep_debug()
    except Exception as e:
        print(f"❌ 深度调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()