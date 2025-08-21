#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查设备的device_type字段情况
"""

from models import *
from sqlalchemy.orm import sessionmaker

def check_device_types():
    """检查设备的device_type字段情况"""
    
    # 创建数据库会话
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 获取所有设备
        devices = db.query(Device).all()
        print(f"总设备数: {len(devices)}")
        
        # 统计device_type字段情况
        devices_with_type = []
        devices_without_type = []
        
        print("\n设备device_type字段情况:")
        for device in devices:
            if device.device_type:
                devices_with_type.append(device)
                print(f"✓ ID={device.id}, name={device.name}, device_type='{device.device_type}', model='{device.model}'")
            else:
                devices_without_type.append(device)
                print(f"✗ ID={device.id}, name={device.name}, device_type=None, model='{device.model}'")
        
        print(f"\n=== 统计结果 ===")
        print(f"有device_type的设备: {len(devices_with_type)}")
        print(f"没有device_type的设备: {len(devices_without_type)}")
        
        # 检查生命周期规则
        rules = db.query(LifecycleRule).all()
        print(f"\n生命周期规则数量: {len(rules)}")
        print("\n现有规则:")
        for rule in rules:
            print(f"- 设备类型: '{rule.device_type}', 生命周期: {rule.lifecycle_years}年, 状态: {rule.is_active}")
        
    except Exception as e:
        print(f"检查失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_device_types()