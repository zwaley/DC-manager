#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生命周期规则匹配情况分析脚本
"""

from models import *
from sqlalchemy.orm import sessionmaker

def analyze_lifecycle_matching():
    """分析设备与生命周期规则的匹配情况"""
    
    # 创建数据库会话
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 获取所有设备和规则
        devices = db.query(Device).all()
        rules = {rule.device_model: rule for rule in db.query(LifecycleRule).filter(LifecycleRule.is_active == 'true').all()}
        
        print("=== 生命周期规则匹配情况分析 ===")
        print(f"\n数据库中共有 {len(devices)} 个设备")
        print(f"生命周期规则共有 {len(rules)} 条")
        
        print("\n当前生命周期规则:")
        for rule_model, rule in rules.items():
            print(f"  - '{rule_model}' -> {rule.lifecycle_years}年")
        
        # 分析匹配情况
        matched_devices = []
        unmatched_devices = []
        
        print("\n匹配情况分析:")
        for device in devices:
            if device.model and device.model in rules:
                matched_devices.append(device)
                print(f"  ✓ 匹配: ID={device.id}, 型号='{device.model}', 规则={rules[device.model].lifecycle_years}年")
            else:
                unmatched_devices.append(device)
        
        print(f"\n=== 统计结果 ===")
        print(f"总设备数: {len(devices)}")
        print(f"匹配到规则的设备: {len(matched_devices)}")
        print(f"未匹配到规则的设备: {len(unmatched_devices)}")
        print(f"匹配率: {len(matched_devices)/len(devices)*100:.1f}%")
        
        if unmatched_devices:
            print("\n未匹配的设备型号统计:")
            unmatched_models = {}
            for device in unmatched_devices:
                model = device.model or "(空)"
                if model not in unmatched_models:
                    unmatched_models[model] = 0
                unmatched_models[model] += 1
            
            for model, count in sorted(unmatched_models.items()):
                print(f"  - '{model}': {count} 个设备")
        
        print("\n=== 问题分析 ===")
        
        # 检查制表符问题
        tab_rules = [rule for rule in rules.keys() if '\t' in rule]
        if tab_rules:
            print(f"发现包含制表符的规则: {tab_rules}")
        
        # 检查大小写问题
        print("\n建议的修复方案:")
        print("1. 清理规则中的制表符")
        print("2. 统一大小写格式")
        print("3. 考虑使用设备分类而非具体型号")
        
    finally:
        db.close()

if __name__ == "__main__":
    analyze_lifecycle_matching()