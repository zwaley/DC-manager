#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化数据库并检查数据库状态
"""

import os
import sqlite3
from models import create_db_and_tables, engine
from config import DATABASE_URL

def init_and_check_database():
    """初始化并检查数据库"""
    print("=== 数据库初始化和检查 ===")
    print(f"配置的数据库URL: {DATABASE_URL}")
    
    # 获取实际的数据库文件路径
    db_file = DATABASE_URL.replace("sqlite:///", "")
    if db_file.startswith("./"):
        db_file = db_file[2:]  # 移除 ./
    
    print(f"数据库文件路径: {db_file}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查数据库文件是否存在
    if os.path.exists(db_file):
        print(f"数据库文件存在，大小: {os.path.getsize(db_file)} 字节")
    else:
        print("数据库文件不存在")
    
    # 初始化数据库
    print("\n正在初始化数据库...")
    try:
        create_db_and_tables()
        print("数据库初始化成功")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return
    
    # 检查初始化后的数据库
    if os.path.exists(db_file):
        print(f"\n初始化后数据库文件大小: {os.path.getsize(db_file)} 字节")
        
        # 连接数据库检查表
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n数据库中的表:")
        for table in tables:
            table_name = table[0]
            print(f"  {table_name}")
            
            # 检查表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"    列数: {len(columns)}")
            
            # 检查记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"    记录数: {count}")
        
        conn.close()
    else:
        print("\n数据库文件仍然不存在")
    
    # 检查其他可能的数据库文件
    print("\n检查当前目录下的所有.db文件:")
    for file in os.listdir("."):
        if file.endswith(".db"):
            size = os.path.getsize(file)
            print(f"  {file}: {size} 字节")
            
            if size > 0:
                # 检查这个数据库的表
                try:
                    conn = sqlite3.connect(file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    table_names = [t[0] for t in tables]
                    print(f"    表: {table_names}")
                    
                    # 如果有connections表，检查记录数
                    if 'connections' in table_names:
                        cursor.execute("SELECT COUNT(*) FROM connections;")
                        count = cursor.fetchone()[0]
                        print(f"    connections表记录数: {count}")
                    
                    conn.close()
                except Exception as e:
                    print(f"    检查失败: {e}")

if __name__ == '__main__':
    init_and_check_database()