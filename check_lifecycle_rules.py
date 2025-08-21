import sqlite3
import os

# 连接数据库
db_path = 'database/asset.db'
if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 检查生命周期规则表 ===")

# 检查表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lifecycle_rules';")
table_exists = cursor.fetchone()

if table_exists:
    print("✅ lifecycle_rules 表存在")
    
    # 查看表结构
    cursor.execute("PRAGMA table_info(lifecycle_rules);")
    columns = cursor.fetchall()
    print("\n表结构:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 查看所有规则
    cursor.execute("SELECT * FROM lifecycle_rules;")
    rules = cursor.fetchall()
    print(f"\n规则总数: {len(rules)}")
    
    if rules:
        print("\n所有规则:")
        for i, rule in enumerate(rules, 1):
            print(f"  规则{i}: {rule}")
    else:
        print("❌ 表中没有任何规则数据！")
        print("\n这就是为什么所有设备状态都是'unknown'的原因。")
        print("需要添加生命周期规则数据。")
        
        # 建议添加一些默认规则
        print("\n建议添加以下默认规则:")
        default_rules = [
            ("直流头柜", 15, 6, "直流头柜设备生命周期规则", "true"),
            ("开关电源", 10, 6, "开关电源设备生命周期规则", "true"),
            ("UPS主机", 12, 6, "UPS主机设备生命周期规则", "true"),
            ("交直流配电设备", 20, 12, "交直流配电设备生命周期规则", "true"),
            ("未知类型", 10, 6, "未知类型设备默认生命周期规则", "true")
        ]
        
        for rule in default_rules:
            print(f"  设备类型: {rule[0]}, 生命周期: {rule[1]}年, 预警期: {rule[2]}个月")
            
else:
    print("❌ lifecycle_rules 表不存在！")

conn.close()
print("\n=== 检查完成 ===")