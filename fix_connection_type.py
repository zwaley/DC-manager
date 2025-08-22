#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复连接类型问题的脚本
将有A端设备但B端设备为占位符87的连接记录的连接类型设置为NULL
改进版：确保数据库连接始终正确关闭，避免数据库锁定问题
"""

import sqlite3
from datetime import datetime
import sys

def fix_connection_type_issues():
    """修复连接类型设置问题"""
    conn = None
    try:
        conn = sqlite3.connect('database/asset.db')
        cursor = conn.cursor()
        
        print("=== 连接类型修复开始 ===")
        
        # 查找需要修复的记录：有A端设备但B端设备为占位符87，且连接类型不为NULL
        cursor.execute("""
            SELECT id, source_device_id, target_device_id, connection_type, source_port
            FROM connections 
            WHERE source_device_id != 87  -- A端不是占位符
            AND target_device_id = 87     -- B端是占位符
            AND connection_type IS NOT NULL  -- 连接类型不为空
            ORDER BY id
        """)
        problem_records = cursor.fetchall()
        
        print(f"找到{len(problem_records)}条需要修复的记录:")
        for record in problem_records:
            print(f"  ID:{record[0]}, A端设备:{record[1]}, B端设备:{record[2]}, 当前连接类型:{record[3]}, A端端口:{record[4]}")
        
        if len(problem_records) == 0:
            print("没有需要修复的记录")
            return
        
        # 自动执行修复，不需要用户确认（避免脚本被中断）
        print(f"\n开始修复这{len(problem_records)}条记录的连接类型...")
        
        # 开始事务
        cursor.execute('BEGIN TRANSACTION')
        
        # 执行修复
        cursor.execute("""
            UPDATE connections 
            SET connection_type = NULL,
                updated_at = ?
            WHERE source_device_id != 87  -- A端不是占位符
            AND target_device_id = 87     -- B端是占位符
            AND connection_type IS NOT NULL  -- 连接类型不为空
        """, (datetime.now().isoformat(),))
        
        affected_rows = cursor.rowcount
        print(f"\n成功修复{affected_rows}条记录")
        
        # 提交事务
        conn.commit()
        print("修复完成并已提交")
        
        # 验证修复结果
        print("\n=== 修复后验证 ===")
        
        # 检查修复后的记录
        cursor.execute("""
            SELECT id, source_device_id, target_device_id, connection_type, source_port
            FROM connections 
            WHERE source_device_id != 87  -- A端不是占位符
            AND target_device_id = 87     -- B端是占位符
            ORDER BY id
        """)
        fixed_records = cursor.fetchall()
        
        print(f"修复后有A端设备但B端为占位符87的记录: {len(fixed_records)}条")
        for record in fixed_records:
            print(f"  ID:{record[0]}, A端设备:{record[1]}, B端设备:{record[2]}, 连接类型:{record[3]}, A端端口:{record[4]}")
        
        # 统计连接类型
        cursor.execute("""
            SELECT connection_type, COUNT(*) 
            FROM connections 
            GROUP BY connection_type
            ORDER BY COUNT(*) DESC
        """)
        type_stats = cursor.fetchall()
        
        print("\n修复后连接类型统计:")
        for type_name, count in type_stats:
            type_display = type_name if type_name is not None else 'NULL'
            print(f"  {type_display}: {count}条")
        
    except Exception as e:
        print(f"\n修复失败: {e}")
        if conn:
            try:
                conn.rollback()
                print("已回滚事务")
            except:
                pass
        sys.exit(1)
    
    finally:
        # 确保数据库连接始终被关闭
        if conn:
            try:
                conn.close()
                print("\n数据库连接已关闭")
            except:
                pass
    
    print("\n=== 连接类型修复完成 ===")

if __name__ == '__main__':
    fix_connection_type_issues()