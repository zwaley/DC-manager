#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_connections():
    # 直接使用SQLite查询避免ORM问题
    conn = sqlite3.connect('database/asset.db')
    cursor = conn.cursor()
    
    try:
        # 查询连接表的基本信息
        cursor.execute("SELECT COUNT(*) FROM connections")
        total_count = cursor.fetchone()[0]
        print(f'总连接数: {total_count}')
        
        # 查询前20条记录
        cursor.execute("""
            SELECT id, source_device_id, target_device_id, connection_type, 
                   source_fuse_number, source_breaker_number
            FROM connections 
            LIMIT 20
        """)
        
        print('\n前20条连接记录的详细信息:')
        for i, row in enumerate(cursor.fetchall()):
            conn_id, source_id, target_id, conn_type, fuse_num, breaker_num = row
            port = fuse_num or breaker_num
            print(f'{i+1}. ID:{conn_id}, A端设备:{source_id}, B端设备:{target_id}, 连接类型:{conn_type}, A端端口:{port}')
        
        # 查找所有连接类型为'cable'的记录
        cursor.execute("""
            SELECT id, source_device_id, target_device_id, connection_type
            FROM connections 
            WHERE connection_type = 'cable'
        """)
        
        cable_connections = cursor.fetchall()
        print(f'\n连接类型为cable的记录数: {len(cable_connections)}')
        
        # 查看设备表中的设备数量
        cursor.execute("SELECT COUNT(*) FROM devices")
        device_count = cursor.fetchone()[0]
        print(f'设备总数: {device_count}')
        
        # 查看设备ID的范围
        cursor.execute("SELECT MIN(id), MAX(id) FROM devices")
        min_id, max_id = cursor.fetchone()
        print(f'设备ID范围: {min_id} - {max_id}')
        
    finally:
        conn.close()

if __name__ == '__main__':
    check_connections()