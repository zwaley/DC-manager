#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备分类分析脚本
分析现有设备型号，设计设备类型分类体系
"""

import sqlite3
import re
from collections import defaultdict

def analyze_device_models():
    """分析设备型号，提取设备类型模式"""
    conn = sqlite3.connect('database/asset.db')
    cursor = conn.cursor()
    
    # 获取所有设备型号
    cursor.execute('SELECT DISTINCT model FROM devices ORDER BY model')
    models = [row[0] for row in cursor.fetchall()]
    
    print(f"总共发现 {len(models)} 种不同的设备型号:")
    print("=" * 50)
    
    # 按型号模式分类
    patterns = defaultdict(list)
    
    for model in models:
        # 跳过None值
        if model is None:
            print(f"- [空值] (跳过)")
            continue
            
        print(f"- {model}")
        
        # 分析型号模式
        model_upper = model.upper()
        if 'DPS' in model_upper:
            patterns['整流器'].append(model)
        elif 'UPS' in model_upper:
            patterns['UPS'].append(model)
        elif 'DPFG' in model_upper:
            patterns['整流器'].append(model)
        elif '蓄电池' in model or 'BATTERY' in model_upper:
            patterns['蓄电池'].append(model)
        elif 'DC' in model_upper:
            patterns['直流设备'].append(model)
        elif 'AC' in model_upper:
            patterns['交流设备'].append(model)
        else:
            patterns['其他'].append(model)
    
    print("\n" + "=" * 50)
    print("设备类型分类建议:")
    print("=" * 50)
    
    for device_type, type_models in patterns.items():
        print(f"\n{device_type} ({len(type_models)}个型号):")
        for model in type_models:
            print(f"  - {model}")
    
    conn.close()
    return patterns

def create_device_type_mapping(patterns):
    """创建设备型号到类型的映射关系"""
    mapping = {}
    
    for device_type, type_models in patterns.items():
        for model in type_models:
            mapping[model] = device_type
    
    return mapping

def suggest_lifecycle_rules():
    """建议生命周期规则"""
    print("\n" + "=" * 50)
    print("建议的生命周期规则:")
    print("=" * 50)
    
    suggested_rules = {
        '整流器': {'lifecycle_years': 10, 'warning_months': 12},
        'UPS': {'lifecycle_years': 8, 'warning_months': 12},
        '蓄电池': {'lifecycle_years': 5, 'warning_months': 6},
        '直流设备': {'lifecycle_years': 10, 'warning_months': 12},
        '交流设备': {'lifecycle_years': 10, 'warning_months': 12},
        '其他': {'lifecycle_years': 8, 'warning_months': 12}
    }
    
    for device_type, rule in suggested_rules.items():
        print(f"{device_type}: 生命周期 {rule['lifecycle_years']} 年，预警提前 {rule['warning_months']} 个月")
    
    return suggested_rules

if __name__ == '__main__':
    print("设备分类分析报告")
    print("=" * 50)
    
    # 分析设备型号
    patterns = analyze_device_models()
    
    # 创建映射关系
    mapping = create_device_type_mapping(patterns)
    
    # 建议生命周期规则
    rules = suggest_lifecycle_rules()
    
    print("\n" + "=" * 50)
    print("分析完成！")
    print(f"共分析了 {sum(len(models) for models in patterns.values())} 个设备型号")
    print(f"建议设置 {len(patterns)} 种设备类型的生命周期规则")