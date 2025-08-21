#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务器脚本 - 直接测试路由功能
"""

import sys
import os
import requests
import time

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_routes():
    """测试路由是否可访问"""
    base_url = "http://localhost:8000"
    test_routes = [
        "/",
        "/debug-routes", 
        "/debug-lifecycle", 
        "/test-route",
        "/api/lifecycle-rules"
    ]
    
    print("=== 路由测试开始 ===")
    
    for route in test_routes:
        url = f"{base_url}{route}"
        try:
            print(f"\n测试路由: {route}")
            response = requests.get(url, timeout=5)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text[:200]  # 只显示前200个字符
                print(f"响应内容: {content}...")
            else:
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
    
    print("\n=== 路由测试完成 ===")

if __name__ == "__main__":
    test_routes()