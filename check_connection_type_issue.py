#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查连接类型判断问题的脚本
专门检查有A端设备但B端设备为空/NULL的连接记录的连接类型设置情况
"""

import sqlite3

def check_connection_type_issues():
    """检查连接类型设置的问题"""
    conn = sqlite3.connect('database/asset.db')
    cursor = conn.cursor()
    
    print("=== 连接类型判断问题检查 ===")
    
    # 1. 检查所有连接记录的基本情况
    cursor.execute('SELECT COUNT(*) FROM connections')
    total_count = cursor.fetchone()[0]
    print(f"总连接记录数: {total_count}")
    
    # 2. 检查B端设备为NULL或空的记录
    cursor.execute("""
        SELECT COUNT(*) FROM connections 
        WHERE target_device_id IS NULL OR target_device_id = '' OR target_device_id = 'nan'
    """)
    null_target_count = cursor.fetchone()[0]
    print(f"B端设备为空的记录数: {null_target_count}")
    
    # 3. 检查A端设备为NULL或空的记录
    cursor.execute("""
        SELECT COUNT(*) FROM connections 
        WHERE source_device_id IS NULL OR source_device_id = '' OR source_device_id = 'nan'
    """)
    null_source_count = cursor.fetchone()[0]
    print(f"A端设备为空的记录数: {null_source_count}")
    
    # 4. 检查完全空白的记录（A端和B端都为空）
    cursor.execute("""
        SELECT COUNT(*) FROM connections 
        WHERE (source_device_id IS NULL OR source_device_id = '' OR source_device_id = 'nan')
        AND (target_device_id IS NULL OR target_device_id = '' OR target_device_id = 'nan')
    """)
    both_null_count = cursor.fetchone()[0]
    print(f"A端和B端都为空的记录数: {both_null_count}")
    
    print("\n=== 问题记录详细分析 ===")
    
    # 5. 检查有A端设备但B端设备为空，且连接类型不为NULL的记录（这是问题记录）
    cursor.execute("""
        SELECT id, source_device_id, target_device_id, connection_type, source_port
        FROM connections 
        WHERE (source_device_id IS NOT NULL AND source_device_id != '' AND source_device_id != 'nan')
        AND (target_device_id IS NULL OR target_device_id = '' OR target_device_id = 'nan')
        AND connection_type IS NOT NULL
        ORDER BY id
    """)
    problem_records = cursor.fetchall()
    
    print(f"\n问题记录（有A端设备但B端为空，连接类型却不为NULL）: {len(problem_records)}条")
    if problem_records:
        print("详细信息:")
        for record in problem_records[:20]:  # 只显示前20条
            print(f"  ID:{record[0]}, A端设备:{record[1]}, B端设备:{record[2]}, 连接类型:{record[3]}, A端端口:{record[4]}")
        if len(problem_records) > 20:
            print(f"  ... 还有{len(problem_records) - 20}条记录")
    
    # 6. 检查有A端设备但B端设备为空，且连接类型为NULL的记录（这是正确的）
    cursor.execute("""
        SELECT COUNT(*) FROM connections 
        WHERE (source_device_id IS NOT NULL AND source_device_id != '' AND source_device_id != 'nan')
        AND (target_device_id IS NULL OR target_device_id = '' OR target_device_id = 'nan')
        AND connection_type IS NULL
    """)
    correct_records_count = cursor.fetchone()[0]
    print(f"\n正确记录（有A端设备但B端为空，连接类型为NULL）: {correct_records_count}条")
    
    # 7. 检查B端设备为占位符设备87的情况
    cursor.execute("""
        SELECT id, source_device_id, target_device_id, connection_type, source_port
        FROM connections 
        WHERE target_device_id = '87'
        ORDER BY id
    """)
    placeholder_records = cursor.fetchall()
    
    print(f"\nB端设备为占位符设备87的记录: {len(placeholder_records)}条")
    if placeholder_records:
        print("详细信息:")
        for record in placeholder_records:
            print(f"  ID:{record[0]}, A端设备:{record[1]}, B端设备:{record[2]}, 连接类型:{record[3]}, A端端口:{record[4]}")
    
    # 8. 按连接类型统计
    cursor.execute("""
        SELECT connection_type, COUNT(*) 
        FROM connections 
        GROUP BY connection_type
        ORDER BY COUNT(*) DESC
    """)
    type_stats = cursor.fetchall()
    
    print("\n=== 连接类型统计 ===")
    for type_name, count in type_stats:
        type_display = type_name if type_name is not None else 'NULL'
        print(f"{type_display}: {count}条")
    
    conn.close()
    
    return len(problem_records)

if __name__ == '__main__':
    problem_count = check_connection_type_issues()
    print(f"\n=== 总结 ===")
    print(f"发现{problem_count}条问题记录需要修复")
    if problem_count > 0:
        print("这些记录有A端设备但B端设备为空，连接类型却被错误设置为非NULL值")
        print("建议将这些记录的连接类型设置为NULL")