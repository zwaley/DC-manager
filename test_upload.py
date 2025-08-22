#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Excel上传功能
用于诊断Excel上传是否能正常触发upload_excel函数
"""

import requests
import os

def test_upload_excel():
    """测试Excel文件上传"""
    print("=== 测试Excel上传功能 ===")
    
    # 服务器地址
    server_url = "http://localhost:8000"
    upload_url = f"{server_url}/upload"
    
    # 检查Excel文件是否存在
    excel_file_path = "设备表.xlsx"
    if not os.path.exists(excel_file_path):
        print(f"错误：Excel文件 '{excel_file_path}' 不存在")
        print("请确保Excel文件在当前目录下")
        return False
    
    print(f"找到Excel文件: {excel_file_path}")
    print(f"文件大小: {os.path.getsize(excel_file_path)} 字节")
    
    # 准备上传数据
    try:
        with open(excel_file_path, 'rb') as f:
            files = {'file': (excel_file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {'password': 'admin123'}  # 使用默认密码
            
            print(f"正在上传到: {upload_url}")
            print("上传参数:")
            print(f"  - 文件名: {excel_file_path}")
            print(f"  - 密码: admin123")
            
            # 发送POST请求
            response = requests.post(upload_url, files=files, data=data, timeout=60)
            
            print(f"\n响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ 上传成功！")
                print("响应内容:")
                print(response.text[:1000])  # 只显示前1000个字符
                return True
            else:
                print(f"❌ 上传失败，状态码: {response.status_code}")
                print("错误响应:")
                print(response.text[:1000])
                return False
                
    except FileNotFoundError:
        print(f"错误：无法打开文件 '{excel_file_path}'")
        return False
    except requests.exceptions.ConnectionError:
        print(f"错误：无法连接到服务器 {server_url}")
        print("请确保服务器正在运行")
        return False
    except requests.exceptions.Timeout:
        print("错误：请求超时")
        return False
    except Exception as e:
        print(f"错误：{e}")
        return False

def check_server_status():
    """检查服务器状态"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"❌ 服务器响应异常，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False

if __name__ == "__main__":
    print("开始诊断Excel上传问题...\n")
    
    # 1. 检查服务器状态
    print("1. 检查服务器状态")
    if not check_server_status():
        print("请先启动服务器")
        exit(1)
    
    print("\n2. 测试Excel上传")
    success = test_upload_excel()
    
    if success:
        print("\n✅ Excel上传测试成功！")
        print("请检查服务器日志以确认数据是否正确处理")
    else:
        print("\n❌ Excel上传测试失败！")
        print("请检查：")
        print("  1. Excel文件是否存在且格式正确")
        print("  2. 服务器是否正常运行")
        print("  3. 管理员密码是否正确")
        print("  4. 网络连接是否正常")