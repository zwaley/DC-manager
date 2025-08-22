#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：扩展Connection表结构

本脚本用于安全地扩展现有Connection表，添加Excel中的18个字段支持。
执行前会自动备份数据库，确保数据安全。

使用方法：
    python migrate_connection_table.py

作者：设备连接关系模块开发团队
日期：2024-12
"""

import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# 数据库配置
DATABASE_PATH = "./database/asset.db"
BACKUP_DIR = "database_backups"

def create_backup():
    """创建数据库备份"""
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ 数据库文件不存在: {DATABASE_PATH}")
        return False
    
    # 创建备份目录
    Path(BACKUP_DIR).mkdir(exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"devices_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        shutil.copy2(DATABASE_PATH, backup_path)
        print(f"✅ 数据库备份成功: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ 数据库备份失败: {e}")
        return False

def check_table_exists(cursor, table_name):
    """检查表是否存在"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def get_table_columns(cursor, table_name):
    """获取表的列信息"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return {col[1]: col[2] for col in columns}  # {column_name: data_type}

def add_column_if_not_exists(cursor, table_name, column_name, column_type, default_value=None):
    """如果列不存在则添加列"""
    columns = get_table_columns(cursor, table_name)
    
    if column_name not in columns:
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if default_value is not None:
            sql += f" DEFAULT {default_value}"
        
        try:
            cursor.execute(sql)
            print(f"  ✅ 添加列: {column_name} ({column_type})")
            return True
        except Exception as e:
            print(f"  ❌ 添加列失败 {column_name}: {e}")
            return False
    else:
        print(f"  ⏭️  列已存在: {column_name}")
        return True

def migrate_connection_table():
    """迁移Connection表结构"""
    print("\n🚀 开始Connection表结构迁移...")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 检查connections表是否存在
        if not check_table_exists(cursor, 'connections'):
            print("❌ connections表不存在，请先运行主程序创建基础表结构")
            return False
        
        print("📋 当前connections表结构:")
        current_columns = get_table_columns(cursor, 'connections')
        for col_name, col_type in current_columns.items():
            print(f"  - {col_name}: {col_type}")
        
        print("\n📝 开始添加新字段...")
        
        # A端（源端）信息字段
        add_column_if_not_exists(cursor, 'connections', 'source_fuse_number', 'VARCHAR(50)')
        add_column_if_not_exists(cursor, 'connections', 'source_fuse_spec', 'VARCHAR(100)')
        add_column_if_not_exists(cursor, 'connections', 'source_breaker_number', 'VARCHAR(50)')
        add_column_if_not_exists(cursor, 'connections', 'source_breaker_spec', 'VARCHAR(100)')
        
        # B端（目标端）信息字段
        add_column_if_not_exists(cursor, 'connections', 'target_fuse_number', 'VARCHAR(50)')
        add_column_if_not_exists(cursor, 'connections', 'target_fuse_spec', 'VARCHAR(100)')
        add_column_if_not_exists(cursor, 'connections', 'target_breaker_number', 'VARCHAR(50)')
        add_column_if_not_exists(cursor, 'connections', 'target_breaker_spec', 'VARCHAR(100)')
        add_column_if_not_exists(cursor, 'connections', 'target_device_location', 'VARCHAR(200)')
        
        # 连接信息字段
        add_column_if_not_exists(cursor, 'connections', 'hierarchy_relation', 'VARCHAR(20)')
        add_column_if_not_exists(cursor, 'connections', 'upstream_downstream', 'VARCHAR(20)')
        add_column_if_not_exists(cursor, 'connections', 'connection_type', 'VARCHAR(20)')
        add_column_if_not_exists(cursor, 'connections', 'cable_model', 'VARCHAR(100)')
        
        # 技术参数字段
        add_column_if_not_exists(cursor, 'connections', 'cable_specification', 'VARCHAR(100)')
        add_column_if_not_exists(cursor, 'connections', 'parallel_count', 'INTEGER', '1')
        add_column_if_not_exists(cursor, 'connections', 'rated_current', 'REAL')
        add_column_if_not_exists(cursor, 'connections', 'cable_length', 'REAL')
        
        # 附加信息字段
        add_column_if_not_exists(cursor, 'connections', 'source_device_photo', 'VARCHAR(500)')
        add_column_if_not_exists(cursor, 'connections', 'target_device_photo', 'VARCHAR(500)')
        add_column_if_not_exists(cursor, 'connections', 'remark', 'TEXT')
        
        # 系统字段
        add_column_if_not_exists(cursor, 'connections', 'installation_date', 'DATE')
        add_column_if_not_exists(cursor, 'connections', 'created_at', 'DATETIME')
        add_column_if_not_exists(cursor, 'connections', 'updated_at', 'DATETIME')
        
        # 提交更改
        conn.commit()
        print("\n✅ Connection表结构迁移完成！")
        
        # 显示迁移后的表结构
        print("\n📋 迁移后的connections表结构:")
        updated_columns = get_table_columns(cursor, 'connections')
        for col_name, col_type in updated_columns.items():
            print(f"  - {col_name}: {col_type}")
        
        print(f"\n📊 字段统计: {len(updated_columns)} 个字段")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def verify_migration():
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 检查表结构
        columns = get_table_columns(cursor, 'connections')
        
        # 必需字段列表（基于设计文档）
        required_fields = [
            'id', 'source_device_id', 'target_device_id',
            'source_port', 'target_port', 'cable_type',  # 原有字段
            'source_fuse_number', 'source_fuse_spec', 'source_breaker_number', 'source_breaker_spec',
            'target_fuse_number', 'target_fuse_spec', 'target_breaker_number', 'target_breaker_spec',
            'target_device_location', 'hierarchy_relation', 'upstream_downstream', 'connection_type',
            'cable_model', 'cable_specification', 'parallel_count', 'rated_current', 'cable_length',
            'source_device_photo', 'target_device_photo', 'remark',
            'installation_date', 'created_at', 'updated_at'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in columns:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ 缺少字段: {missing_fields}")
            return False
        else:
            print("✅ 所有必需字段都已存在")
            
        # 检查数据完整性
        cursor.execute("SELECT COUNT(*) FROM connections")
        connection_count = cursor.fetchone()[0]
        print(f"📊 现有连接记录数: {connection_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 设备连接关系模块 - 数据库迁移脚本")
    print("=" * 60)
    
    # 检查数据库文件是否存在
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ 数据库文件不存在: {DATABASE_PATH}")
        print("请先运行主程序创建数据库")
        return
    
    # 创建备份
    print("\n📦 第1步: 创建数据库备份")
    backup_path = create_backup()
    if not backup_path:
        print("❌ 备份失败，迁移终止")
        return
    
    # 执行迁移
    print("\n🔄 第2步: 执行表结构迁移")
    if not migrate_connection_table():
        print("❌ 迁移失败")
        print(f"💡 可以从备份恢复: {backup_path}")
        return
    
    # 验证迁移
    print("\n✅ 第3步: 验证迁移结果")
    if not verify_migration():
        print("❌ 验证失败")
        return
    
    print("\n" + "=" * 60)
    print("🎉 数据库迁移成功完成！")
    print("=" * 60)
    print(f"📦 备份文件: {backup_path}")
    print("💡 现在可以使用扩展后的Connection模型功能")
    print("🚀 下一步: 实现连接管理的RESTful API接口")

if __name__ == "__main__":
    main()