import sqlite3
import os
from datetime import datetime

# 连接数据库
db_path = 'database/asset.db'
if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 检查设备投产日期数据 ===")

# 查看所有设备的投产日期情况
cursor.execute("""
    SELECT 
        id, 
        asset_id, 
        name, 
        device_type, 
        commission_date,
        CASE 
            WHEN commission_date IS NULL THEN '空值'
            WHEN commission_date = '' THEN '空字符串'
            WHEN commission_date = 'None' THEN 'None字符串'
            ELSE '有值'
        END as date_status
    FROM devices 
    ORDER BY date_status, id
""")

devices = cursor.fetchall()

print(f"\n总设备数: {len(devices)}")

# 统计投产日期状态
date_status_count = {}
for device in devices:
    status = device[5]  # date_status
    date_status_count[status] = date_status_count.get(status, 0) + 1

print("\n投产日期状态统计:")
for status, count in date_status_count.items():
    print(f"  {status}: {count}个设备")

# 显示有投产日期的设备
print("\n有投产日期的设备:")
has_date_count = 0
for device in devices:
    device_id, asset_id, name, device_type, commission_date, date_status = device
    if date_status == '有值':
        has_date_count += 1
        print(f"  ID{device_id}: {name} - 类型:{device_type} - 投产日期:{commission_date}")
        if has_date_count >= 10:  # 只显示前10个
            break

if has_date_count > 10:
    print(f"  ... 还有{has_date_count - 10}个设备有投产日期")

# 显示没有投产日期的设备（前10个）
print("\n没有投产日期的设备（前10个）:")
no_date_count = 0
for device in devices:
    device_id, asset_id, name, device_type, commission_date, date_status = device
    if date_status != '有值':
        no_date_count += 1
        print(f"  ID{device_id}: {name} - 类型:{device_type} - 投产日期:{commission_date} ({date_status})")
        if no_date_count >= 10:
            break

total_no_date = sum([count for status, count in date_status_count.items() if status != '有值'])
if total_no_date > 10:
    print(f"  ... 还有{total_no_date - 10}个设备没有投产日期")

conn.close()
print("\n=== 检查完成 ===")
print("\n建议: 如果大部分设备没有投产日期，需要补充这些数据才能正确计算生命周期状态。")