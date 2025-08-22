#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复connection_type字段默认值问题

问题描述：
- models.py中connection_type字段设置了default='cable'
- 导致空连接类型被自动填充为'cable'
- 需要移除默认值约束，并修正现有错误数据

修复方案：
1. 移除connection_type字段的默认值约束
2. 将错误的'cable'数据修正为NULL（仅针对应该为空闲的端口）
"""

import sqlite3
import os
from datetime import datetime

def backup_database(db_path):
    """备份数据库"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"database_backups/asset_backup_{timestamp}.db"
    
    # 确保备份目录存在
    os.makedirs("database_backups", exist_ok=True)
    
    # 复制数据库文件
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✅ 数据库已备份到: {backup_path}")
    return backup_path

def fix_connection_type_default():
    """修复connection_type字段默认值问题"""
    db_path = "database/asset.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    # 备份数据库
    backup_path = backup_database(db_path)
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 检查当前connection_type字段状态...")
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(connections)")
        columns = cursor.fetchall()
        
        connection_type_info = None
        for col in columns:
            if col[1] == 'connection_type':
                connection_type_info = col
                break
        
        if connection_type_info:
            print(f"当前connection_type字段信息: {connection_type_info}")
        else:
            print("❌ 未找到connection_type字段")
            return False
        
        # 统计当前数据
        cursor.execute("SELECT COUNT(*) FROM connections")
        total_connections = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM connections WHERE connection_type = 'cable'")
        cable_connections = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM connections WHERE connection_type IS NULL OR connection_type = ''")
        null_connections = cursor.fetchone()[0]
        
        print(f"📊 当前数据统计:")
        print(f"   总连接数: {total_connections}")
        print(f"   'cable'类型: {cable_connections}")
        print(f"   空值类型: {null_connections}")
        
        # 重建表结构，移除默认值
        print("\n🔧 开始修复表结构...")
        
        # 创建新表（无默认值）
        cursor.execute("""
        CREATE TABLE connections_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_device_id INTEGER,
            source_port VARCHAR,
            target_device_id INTEGER,
            target_port VARCHAR,
            cable_type VARCHAR,
            source_fuse_number VARCHAR(50),
            source_fuse_spec VARCHAR(100),
            source_breaker_number VARCHAR(50),
            source_breaker_spec VARCHAR(100),
            target_fuse_number VARCHAR(50),
            target_fuse_spec VARCHAR(100),
            target_breaker_number VARCHAR(50),
            target_breaker_spec VARCHAR(100),
            target_device_location VARCHAR(200),
            hierarchy_relation VARCHAR(20),
            upstream_downstream VARCHAR(20),
            connection_type VARCHAR(20),  -- 移除默认值
            cable_model VARCHAR(100),
            cable_specification VARCHAR(100),
            parallel_count INTEGER DEFAULT 1,
            rated_current REAL,
            cable_length REAL,
            source_device_photo VARCHAR(500),
            target_device_photo VARCHAR(500),
            remark TEXT,
            installation_date DATE,
            created_at DATETIME,
            updated_at DATETIME
        )
        """)
        
        # 复制数据到新表
        cursor.execute("""
        INSERT INTO connections_new 
        SELECT * FROM connections
        """)
        
        # 删除旧表
        cursor.execute("DROP TABLE connections")
        
        # 重命名新表
        cursor.execute("ALTER TABLE connections_new RENAME TO connections")
        
        print("✅ 表结构修复完成")
        
        # 现在处理数据修正
        print("\n🔧 开始修正错误数据...")
        
        # 这里需要根据业务逻辑判断哪些'cable'应该改为NULL
        # 暂时不自动修改，因为需要更多业务逻辑判断
        print("⚠️  数据修正需要根据具体业务逻辑进行，请手动检查和修正")
        
        # 提交更改
        conn.commit()
        
        # 验证修复结果
        cursor.execute("PRAGMA table_info(connections)")
        columns = cursor.fetchall()
        
        connection_type_info = None
        for col in columns:
            if col[1] == 'connection_type':
                connection_type_info = col
                break
        
        print(f"\n✅ 修复后connection_type字段信息: {connection_type_info}")
        
        # 统计修复后数据
        cursor.execute("SELECT COUNT(*) FROM connections WHERE connection_type = 'cable'")
        cable_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM connections WHERE connection_type IS NULL")
        null_after = cursor.fetchone()[0]
        
        print(f"\n📊 修复后数据统计:")
        print(f"   'cable'类型: {cable_after}")
        print(f"   NULL类型: {null_after}")
        
        conn.close()
        
        print("\n🎉 connection_type字段默认值修复完成！")
        print("💡 建议：")
        print("   1. 重启应用程序以应用新的模型定义")
        print("   2. 检查现有'cable'数据是否需要修正为NULL")
        print("   3. 测试Excel导入功能，确认空连接类型不再被填充为'cable'")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        print(f"💾 可以从备份恢复: {backup_path}")
        return False

if __name__ == "__main__":
    print("🚀 开始修复connection_type字段默认值问题...")
    print("=" * 60)
    
    success = fix_connection_type_default()
    
    print("=" * 60)
    if success:
        print("✅ 修复完成！")
    else:
        print("❌ 修复失败！")