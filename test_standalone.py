#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试服务器 - 在不同端口启动服务器进行测试
"""

import sys
import os
import uvicorn
import asyncio
import threading
import time
import requests

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_test_server():
    """在独立线程中启动测试服务器"""
    try:
        import main
        print("✅ 成功导入main模块")
        print(f"启动测试服务器在端口 8001...")
        uvicorn.run(main.app, host="127.0.0.1", port=8001, log_level="info")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        import traceback
        traceback.print_exc()

def test_routes():
    """测试路由"""
    base_url = "http://127.0.0.1:8001"
    test_routes = [
        "/debug-routes", 
        "/debug-lifecycle", 
        "/test-route"
    ]
    
    print("\n=== 等待服务器启动 ===")
    time.sleep(3)  # 等待服务器启动
    
    print("=== 开始测试路由 ===")
    
    for route in test_routes:
        url = f"{base_url}{route}"
        try:
            print(f"\n测试路由: {route}")
            response = requests.get(url, timeout=5)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text[:500]  # 显示前500个字符
                print(f"响应内容: {content}")
            else:
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    print("=== 独立服务器测试 ===")
    
    # 在独立线程中启动服务器
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    
    # 测试路由
    test_routes()