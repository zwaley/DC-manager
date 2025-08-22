import pandas as pd

# 读取Excel文件的所有sheet
print('=== 读取Excel文件的所有sheet ===')
xls = pd.ExcelFile('设备表.xlsx')
print(f'Excel文件包含的sheet: {xls.sheet_names}')

# 读取第一个sheet（设备表）
print('\n=== Sheet 1: 设备表 ===')
df1 = pd.read_excel('设备表.xlsx', sheet_name=0)
print('设备表列名:')
for i, col in enumerate(df1.columns.tolist()):
    print(f'{i+1}. {col}')
print(f'总共有 {len(df1.columns)} 列，{len(df1)} 行数据')

# 读取第二个sheet（连接表）
if len(xls.sheet_names) > 1:
    print('\n=== Sheet 2: 连接表 ===')
    df2 = pd.read_excel('设备表.xlsx', sheet_name=1)
    print('连接表列名:')
    for i, col in enumerate(df2.columns.tolist()):
        print(f'{i+1}. {col}')
    print(f'总共有 {len(df2.columns)} 列，{len(df2)} 行数据')
    
    # 显示连接表的前几行数据样本
    print('\n连接表前3行数据样本:')
    for i in range(min(3, len(df2))):
        print(f'\n第{i+1}行:')
        for col in df2.columns:
            print(f'  {col}: {df2.iloc[i][col]}')
else:
    print('\n没有找到第二个sheet（连接表）')