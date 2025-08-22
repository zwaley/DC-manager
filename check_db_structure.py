#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

# 连接数据库
conn = sqlite3.connect('database/asset.db')
cursor = conn.cursor()

try:
    # 检查所有表
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    print('数据库中的表:', [t[0] for t in tables])
    
    # 检查connections表结构
    if 'connections' in [t[0] for t in tables]:
        cursor.execute('PRAGMA table_info(connections)')
        columns = cursor.fetchall()
        print('\nconnections表结构:')
        for col in columns:
            print(f'{col[1]} {col[2]}')
            
        # 检查connections表数据量
        cursor.execute('SELECT COUNT(*) FROM connections')
        count = cursor.fetchone()[0]
        print(f'\nconnections表数据量: {count}')
        
        if count > 0:
            cursor.execute('SELECT * FROM connections LIMIT 3')
            rows = cursor.fetchall()
            print('\n前3条连接数据:')
            for i, row in enumerate(rows):
                print(f'第{i+1}条: {row}')
    else:
        print('\nconnections表不存在')
        
    # 检查devices表
    if 'devices' in [t[0] for t in tables]:
        cursor.execute('SELECT COUNT(*) FROM devices')
        device_count = cursor.fetchone()[0]
        print(f'\ndevices表数据量: {device_count}')
    else:
        print('\ndevices表不存在')
        
finally:
    conn.close()