import pandas as pd
import os

# 检查Excel文件的sheet结构
excel_file = '设备表.xlsx'

if os.path.exists(excel_file):
    print(f"正在检查Excel文件: {excel_file}")
    
    try:
        # 读取Excel文件的所有sheet
        xl_file = pd.ExcelFile(excel_file)
        print(f"\nExcel文件包含的所有sheet: {xl_file.sheet_names}")
        
        # 检查每个sheet的内容
        for i, sheet_name in enumerate(xl_file.sheet_names):
            print(f"\n=== Sheet {i+1}: '{sheet_name}' ===")
            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                print(f"行数: {len(df)}")
                print(f"列数: {len(df.columns)}")
                print(f"列名: {list(df.columns)}")
                
                # 如果是连接相关的sheet，显示更多信息
                if '连接' in sheet_name or 'Sheet2' in sheet_name or i == 1:
                    print(f"\n前3行数据样本:")
                    for row_idx in range(min(3, len(df))):
                        print(f"第{row_idx+1}行:")
                        for col in df.columns[:5]:  # 只显示前5列
                            value = df.iloc[row_idx][col]
                            print(f"  {col}: {value}")
                        print()
                        
            except Exception as e:
                print(f"读取sheet '{sheet_name}' 时出错: {e}")
                
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
else:
    print(f"Excel文件不存在: {excel_file}")
    
print("\n检查完成")