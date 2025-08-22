import pandas as pd
import os

# 检查Excel文件内容
excel_file = '设备表.xlsx'

if os.path.exists(excel_file):
    print(f"正在检查Excel文件: {excel_file}")
    
    # 读取所有sheet
    try:
        xl_file = pd.ExcelFile(excel_file)
        print(f"Excel文件包含的sheet: {xl_file.sheet_names}")
        
        # 检查Sheet1
        if 'Sheet1' in xl_file.sheet_names:
            df1 = pd.read_excel(excel_file, sheet_name='Sheet1')
            print(f"\nSheet1 - 设备数据:")
            print(f"行数: {len(df1)}")
            print(f"列名: {list(df1.columns)}")
            if len(df1) > 0:
                print(f"前3行数据:")
                print(df1.head(3))
        
        # 检查连接sheet
        connection_sheet = None
        if '连接' in xl_file.sheet_names:
            connection_sheet = '连接'
        elif 'Sheet2' in xl_file.sheet_names:
            connection_sheet = 'Sheet2'
            
        if connection_sheet:
            df2 = pd.read_excel(excel_file, sheet_name=connection_sheet)
            print(f"\n{connection_sheet} - 连接数据:")
            print(f"行数: {len(df2)}")
            print(f"列名: {list(df2.columns)}")
            if len(df2) > 0:
                print(f"前5行数据:")
                print(df2.head(5))
        else:
            print("\n警告: 没有找到连接数据sheet!")
            
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
else:
    print(f"Excel文件不存在: {excel_file}")

print("\n检查完成")