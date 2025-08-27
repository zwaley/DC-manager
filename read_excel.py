import pandas as pd

# 读取Excel文件
df = pd.read_excel('设备表.xlsx')

print('Excel文件结构分析:')
print('=' * 50)

# 获取所有工作表名称
excel_file = pd.ExcelFile('设备表.xlsx')
print(f'工作表数量: {len(excel_file.sheet_names)}')
print(f'工作表名称: {excel_file.sheet_names}')

print('\n第一个工作表的列结构:')
print('-' * 30)
for i, col in enumerate(df.columns, 1):
    print(f'{i:2d}. {col}')

print(f'\n数据统计:')
print(f'总列数: {len(df.columns)}')
print(f'总行数: {len(df)}')

print('\n前3行数据预览:')
print('-' * 30)
for i in range(min(3, len(df))):
    print(f'\n第{i+1}行:')
    for col in df.columns:
        value = df.iloc[i][col]
        if pd.isna(value):
            value = 'NaN'
        print(f'  {col}: {value}')

# 检查是否有第二个工作表
if len(excel_file.sheet_names) > 1:
    print(f'\n\n第二个工作表 "{excel_file.sheet_names[1]}" 的结构:')
    print('=' * 50)
    df2 = pd.read_excel('设备表.xlsx', sheet_name=excel_file.sheet_names[1])
    
    print('列结构:')
    for i, col in enumerate(df2.columns, 1):
        print(f'{i:2d}. {col}')
    
    print(f'\n数据统计:')
    print(f'总列数: {len(df2.columns)}')
    print(f'总行数: {len(df2)}')
    
    print('\n前3行数据预览:')
    print('-' * 30)
    for i in range(min(3, len(df2))):
        print(f'\n第{i+1}行:')
        for col in df2.columns:
            value = df2.iloc[i][col]
            if pd.isna(value):
                value = 'NaN'
            print(f'  {col}: {value}')