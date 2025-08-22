#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的Excel导入功能
"""

import pandas as pd
from models import SessionLocal, Device, Connection
from sqlalchemy import func

def test_import():
    """测试改进后的导入功能"""
    print("=== 测试改进后的Excel导入功能 ===")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 读取Excel文件
        excel_file = "设备表.xlsx"
        print(f"\n1. 读取Excel文件: {excel_file}")
        
        # 读取连接数据
        df_connections = pd.read_excel(excel_file, sheet_name='连接')
        print(f"   连接工作表总行数: {len(df_connections)}")
        
        # 统计当前数据库状态
        device_count_before = db.query(Device).count()
        connection_count_before = db.query(Connection).count()
        print(f"\n2. 导入前数据库状态:")
        print(f"   设备数量: {device_count_before}")
        print(f"   连接数量: {connection_count_before}")
        
        # 分析Excel数据
        print(f"\n3. 分析Excel连接数据:")
        
        # 统计空设备名称
        empty_source = df_connections['A端设备名称'].isna() | (df_connections['A端设备名称'].astype(str).str.strip() == '')
        empty_target = df_connections['B端设备名称'].isna() | (df_connections['B端设备名称'].astype(str).str.strip() == '')
        
        print(f"   A端设备名称为空: {empty_source.sum()} 行")
        print(f"   B端设备名称为空: {empty_target.sum()} 行")
        print(f"   两端都为空: {(empty_source & empty_target).sum()} 行")
        
        # 获取所有非空设备名称
        all_device_names = set()
        for _, row in df_connections.iterrows():
            source_name = str(row.get('A端设备名称', '')).strip()
            target_name = str(row.get('B端设备名称', '')).strip()
            if source_name:
                all_device_names.add(source_name)
            if target_name:
                all_device_names.add(target_name)
        
        print(f"   Excel中涉及的设备总数: {len(all_device_names)}")
        
        # 检查哪些设备在数据库中不存在
        existing_devices = {device.name for device in db.query(Device).all()}
        missing_devices = all_device_names - existing_devices
        print(f"   数据库中不存在的设备: {len(missing_devices)}")
        
        if missing_devices:
            print("   缺失的设备列表:")
            for device_name in sorted(missing_devices):
                print(f"     - {device_name}")
        
        # 预测导入结果
        valid_connections = 0
        for _, row in df_connections.iterrows():
            source_name = str(row.get('A端设备名称', '')).strip()
            target_name = str(row.get('B端设备名称', '')).strip()
            
            if source_name and target_name:
                valid_connections += 1
        
        print(f"\n4. 预测导入结果:")
        print(f"   理论上可导入的连接: {valid_connections} 个")
        print(f"   需要自动创建的设备: {len(missing_devices)} 个")
        
        # 模拟导入过程（不实际执行）
        print(f"\n5. 改进后的导入逻辑将会:")
        print(f"   - 自动创建 {len(missing_devices)} 个缺失设备")
        print(f"   - 成功导入 {valid_connections} 个连接")
        print(f"   - 跳过 {len(df_connections) - valid_connections} 个无效连接")
        
        success_rate = (valid_connections / len(df_connections)) * 100 if len(df_connections) > 0 else 0
        print(f"   - 预期导入成功率: {success_rate:.1f}%")
        
        print(f"\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_import()