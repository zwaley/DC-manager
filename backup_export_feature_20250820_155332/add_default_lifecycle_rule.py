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

print("=== 添加默认生命周期规则 ===")

# 检查是否已经有"未知类型"或"默认"规则
cursor.execute("SELECT * FROM lifecycle_rules WHERE device_type IN ('未知类型', '默认', 'None', '') OR device_type IS NULL;")
existing_default = cursor.fetchone()

if existing_default:
    print(f"已存在默认规则: {existing_default}")
else:
    # 添加默认规则
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 为None/空值设备类型添加默认规则
    cursor.execute("""
        INSERT INTO lifecycle_rules (device_type, lifecycle_years, warning_months, description, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('未知类型', 10, 6, '未知类型设备的默认生命周期规则', 'true', current_time, current_time))
    
    print("✅ 已添加默认生命周期规则:")
    print("   设备类型: 未知类型")
    print("   生命周期: 10年")
    print("   预警期: 6个月")
    print("   描述: 未知类型设备的默认生命周期规则")

# 提交更改
conn.commit()

# 验证添加结果
cursor.execute("SELECT * FROM lifecycle_rules ORDER BY id;")
all_rules = cursor.fetchall()

print(f"\n当前所有生命周期规则 (共{len(all_rules)}个):")
for rule in all_rules:
    rule_id, device_type, lifecycle_years, warning_months, description, is_active, created_at, updated_at = rule
    print(f"  ID{rule_id}: '{device_type}' - {lifecycle_years}年 (预警{warning_months}个月) - {is_active}")

conn.close()
print("\n=== 完成 ===")
print("\n现在需要重启服务器以使更改生效。")