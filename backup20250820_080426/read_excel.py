import pandas as pd

# 读取Excel文件
df = pd.read_excel('设备表.xlsx')

# 打印列名
print('Excel文件列名:')
for i, col in enumerate(df.columns.tolist()):
    print(f'{i+1}. {col}')

print(f'\n总共有 {len(df.columns)} 列')
print(f'总共有 {len(df)} 行数据')

# 显示前几行数据的样本
print('\n前3行数据样本:')
for i in range(min(3, len(df))):
    print(f'\n第{i+1}行:')
    for col in df.columns:
        print(f'  {col}: {df.iloc[i][col]}')