#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_tables():
    conn = sqlite3.connect('./database/asset.db')
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print('数据库中的表:')
    for table in tables:
        print(f'  {table[0]}')
    
    # 检查每个表的结构
    for table in tables:
        table_name = table[0]
        print(f'\n表 {table_name} 的结构:')
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for column in columns:
            print(f'  {column[1]} ({column[2]})')
    
    conn.close()

if __name__ == "__main__":
    check_tables()