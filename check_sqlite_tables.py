import sqlite3
import os

# 检查数据库文件是否存在
db_path = './database/asset.db'
print(f"数据库文件路径: {db_path}")
print(f"数据库文件是否存在: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"\n数据库中的表: {[table[0] for table in tables]}")
    
    # 检查每个表的结构和数据
    for table in tables:
        table_name = table[0]
        print(f"\n=== 表 '{table_name}' ====")
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print(f"列信息: {[col[1] for col in columns]}")
        
        # 获取表中的记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"记录数: {count}")
        
        # 如果是devices表，显示前几条记录
        if table_name == 'devices' and count > 0:
            cursor.execute(f"SELECT name FROM {table_name} LIMIT 5;")
            device_names = cursor.fetchall()
            print(f"前5个设备名称: {[name[0] for name in device_names]}")
    
    conn.close()
else:
    print("数据库文件不存在！")