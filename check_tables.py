#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库表结构
"""

import sqlite3

def check_database_tables():
    """检查数据库中的表"""
    conn = sqlite3.connect('dc_asset_manager.db')
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("数据库中的表:")
    for table in tables:
        print(f"  {table[0]}")
    
    # 如果有表，查看第一个表的结构
    if tables:
        table_name = tables[0][0]
        print(f"\n表 '{table_name}' 的结构:")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 查看前几条记录
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        records = cursor.fetchall()
        print(f"\n表 '{table_name}' 的前5条记录:")
        for i, record in enumerate(records):
            print(f"  记录{i+1}: {record}")
    
    conn.close()

if __name__ == '__main__':
    check_database_tables()