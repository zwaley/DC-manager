#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试生命周期规则匹配问题
"""

from models import *
from sqlalchemy.orm import sessionmaker

def debug_lifecycle_matching():
    """调试生命周期规则匹配问题"""
    
    # 创建数据库会话
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 获取所有设备和规则
        devices = db.query(Device).all()
        rules = {rule.device_type: rule for rule in db.query(LifecycleRule).filter(LifecycleRule.is_active == "true").all()}
        
        print("=== 生命周期规则匹配调试 ===")
        print(f"\n总设备数: {len(devices)}")
        print(f"活跃规则数: {len(rules)}")
        
        print("\n现有规则:")
        for device_type, rule in rules.items():
            print(f"- 设备类型: '{device_type}' (长度: {len(device_type)}, repr: {repr(device_type)})")
            print(f"  生命周期: {rule.lifecycle_years}年, 状态: {rule.is_active}")
        
        # 检查有device_type的设备匹配情况
        devices_with_type = [d for d in devices if d.device_type]
        print(f"\n有device_type的设备数: {len(devices_with_type)}")
        
        matched_count = 0
        unmatched_count = 0
        
        print("\n详细匹配情况:")
        for device in devices_with_type:
            device_type = device.device_type
            if device_type in rules:
                matched_count += 1
                rule = rules[device_type]
                print(f"✓ 匹配: ID={device.id}, name='{device.name}', device_type='{device_type}' -> {rule.lifecycle_years}年")
            else:
                unmatched_count += 1
                print(f"✗ 未匹配: ID={device.id}, name='{device.name}', device_type='{device_type}' (长度: {len(device_type)}, repr: {repr(device_type)})")
                
                # 检查是否有相似的规则
                print(f"  可用规则类型: {list(rules.keys())}")
                for rule_type in rules.keys():
                    if device_type.strip() == rule_type.strip():
                        print(f"  ⚠️ 去除空格后匹配: '{device_type.strip()}' == '{rule_type.strip()}'")
                    elif device_type.lower() == rule_type.lower():
                        print(f"  ⚠️ 忽略大小写后匹配: '{device_type.lower()}' == '{rule_type.lower()}'")
        
        print(f"\n=== 匹配统计 ===")
        print(f"有device_type的设备: {len(devices_with_type)}")
        print(f"匹配到规则的设备: {matched_count}")
        print(f"未匹配到规则的设备: {unmatched_count}")
        
        # 测试生命周期状态计算逻辑
        print(f"\n=== 测试生命周期状态计算 ===")
        from datetime import datetime, timedelta
        import re
        
        current_date = datetime.now()
        
        for device in devices_with_type[:5]:  # 只测试前5个设备
            rule = rules.get(device.device_type)
            print(f"\n设备: {device.name} (ID: {device.id})")
            print(f"设备类型: '{device.device_type}' (repr: {repr(device.device_type)})")
            print(f"投运日期: {device.commission_date}")
            
            if rule:
                print(f"匹配规则: {rule.lifecycle_years}年, 预警: {rule.warning_months}个月")
                
                if device.commission_date:
                    try:
                        # 解析投产日期 - 使用与main.py相同的逻辑
                        commission_date = None
                        date_str = device.commission_date.strip()
                        
                        # 处理特殊格式：YYYYMM (如 202312)
                        import re
                        if re.match(r'^\d{6}$', date_str):
                            try:
                                year = int(date_str[:4])
                                month = int(date_str[4:6])
                                commission_date = datetime(year, month, 1)
                            except ValueError:
                                pass
                        
                        # 如果特殊格式解析失败，尝试标准格式
                        if not commission_date:
                            date_formats = [
                                "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
                                "%Y-%m", "%Y/%m", "%Y.%m",
                                "%Y年%m月%d日", "%Y年%m月"
                            ]
                            
                            for fmt in date_formats:
                                try:
                                    commission_date = datetime.strptime(date_str, fmt)
                                    break
                                except ValueError:
                                    continue
                        
                        if commission_date:
                            days_in_service = (current_date - commission_date).days
                            lifecycle_days = rule.lifecycle_years * 365
                            warning_days = lifecycle_days - (rule.warning_months * 30)
                            
                            print(f"运行天数: {days_in_service}")
                            print(f"生命周期天数: {lifecycle_days}")
                            print(f"预警天数: {warning_days}")
                            
                            if days_in_service >= lifecycle_days:
                                status = "expired"
                                status_text = "已超期"
                            elif days_in_service >= warning_days:
                                status = "warning"
                                status_text = "临近超限"
                            else:
                                status = "normal"
                                status_text = "正常"
                            
                            print(f"计算状态: {status} - {status_text}")
                        else:
                            print(f"日期解析失败: 无法识别日期格式 '{date_str}'")
                    except Exception as e:
                        print(f"日期解析错误: {e}")
                else:
                    print("无投运日期")
            else:
                print("未找到匹配规则")
        
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_lifecycle_matching()