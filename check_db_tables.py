import sqlite3

# 连接数据库
conn = sqlite3.connect('dc_asset_manager.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('数据库中的表:', [table[0] for table in tables])

# 如果有设备相关的表，查看其结构
for table in tables:
    table_name = table[0]
    if 'device' in table_name.lower() or 'equipment' in table_name.lower():
        print(f"\n表 '{table_name}' 的结构:")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 查看前几条记录
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        rows = cursor.fetchall()
        print(f"\n前3条记录:")
        for i, row in enumerate(rows, 1):
            print(f"  第{i}条: {row}")

conn.close()