import sqlite3

# 连接数据库
conn = sqlite3.connect('database/asset.db')
cursor = conn.cursor()

# 检查数据库中的所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('数据库中的表:')
for table in tables:
    print(f'- {table[0]}')

if tables:
    # 如果有表，检查第一个表的内容
    table_name = tables[0][0]
    print(f'\n检查表 {table_name}:')
    
    # 检查表结构
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    print('表结构:')
    for col in columns:
        print(f'  列名: {col[1]}, 类型: {col[2]}')
    
    # 检查记录数
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f'\n记录总数: {count}')
    
    # 查看前5条数据
    if count > 0:
        cursor.execute(f'SELECT * FROM {table_name} LIMIT 5')
        rows = cursor.fetchall()
        print('\n前5条数据:')
        for i, row in enumerate(rows, 1):
            print(f'  记录{i}: {row}')
else:
    print('数据库中没有表')

conn.close()
print('\n数据库检查完成')