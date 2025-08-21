#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import LifecycleRule, Device

# 创建数据库连接
DATABASE_URL = "sqlite:///./database/asset.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_database():
    db = SessionLocal()
    try:
        # 检查生命周期规则
        rules = db.query(LifecycleRule).all()
        print(f"生命周期规则数量: {len(rules)}")
        for rule in rules:
            print(f"规则: device_type={rule.device_type}, lifecycle_years={rule.lifecycle_years}, warning_months={rule.warning_months}, is_active={rule.is_active}")
        
        # 检查设备数据
        devices = db.query(Device).limit(10).all()
        print(f"\n前10个设备的device_type:")
        for device in devices:
            print(f"设备{device.id}: device_type='{device.device_type}', commission_date='{device.commission_date}'")
            
        # 统计设备类型分布
        device_types = db.query(Device.device_type).distinct().all()
        print(f"\n设备类型分布:")
        for device_type in device_types:
            if device_type[0]:
                count = db.query(Device).filter(Device.device_type == device_type[0]).count()
                print(f"  {device_type[0]}: {count}个设备")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_database()