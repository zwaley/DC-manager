#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Excel文件中的工作表
"""

import pandas as pd

def check_excel_sheets():
    """检查Excel文件中的工作表"""
    excel_file = "设备表.xlsx"
    
    try:
        # 读取Excel文件的所有工作表名称
        excel_file_obj = pd.ExcelFile(excel_file)
        sheet_names = excel_file_obj.sheet_names
        
        print(f"Excel文件: {excel_file}")
        print(f"工作表数量: {len(sheet_names)}")
        print("工作表列表:")
        for i, sheet_name in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet_name}")
        
        # 检查每个工作表的内容
        for sheet_name in sheet_names:
            print(f"\n=== 工作表: {sheet_name} ===")
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            print(f"行数: {len(df)}")
            print(f"列数: {len(df.columns)}")
            print("列名:")
            for col in df.columns:
                print(f"  - {col}")
            
            # 显示前几行数据
            if len(df) > 0:
                print("\n前3行数据:")
                print(df.head(3).to_string())
            
    except Exception as e:
        print(f"检查Excel文件时出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_excel_sheets()