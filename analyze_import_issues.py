import pandas as pd
import sqlite3
import os

def analyze_excel_import_issues():
    """
    分析Excel连接数据导入问题
    检查每一行数据的导入情况，找出跳过的原因
    """
    print("=== Excel连接数据导入问题分析 ===")
    
    # 检查Excel文件
    excel_file = '设备表.xlsx'
    if not os.path.exists(excel_file):
        print(f"错误：Excel文件 {excel_file} 不存在")
        return
    
    # 连接数据库
    db_path = './database/asset.db'
    if not os.path.exists(db_path):
        print(f"错误：数据库文件 {db_path} 不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 获取数据库中的设备名称
        cursor.execute("SELECT name FROM devices")
        device_names = {row[0] for row in cursor.fetchall()}
        print(f"数据库中设备总数: {len(device_names)}")
        print(f"前10个设备名称: {list(device_names)[:10]}")
        
        # 读取Excel文件的连接数据
        try:
            df = pd.read_excel(excel_file, sheet_name='连接')
            print(f"\nExcel中连接数据总行数: {len(df)}")
        except Exception as e:
            print(f"读取Excel文件失败: {e}")
            return
        
        # 分析每一行数据
        valid_connections = 0
        skipped_connections = 0
        skip_reasons = {}
        
        print("\n=== 逐行分析连接数据 ===")
        
        for index, row in df.iterrows():
            row_num = index + 2  # Excel行号从2开始（第1行是标题）
            
            # 提取A端和B端设备名称
            a_device_name = str(row.get('A端设备名称', '')).strip() if pd.notna(row.get('A端设备名称')) else ''
            b_device_name = str(row.get('B端设备名称', '')).strip() if pd.notna(row.get('B端设备名称')) else ''
            
            # 检查跳过原因
            skip_reason = None
            
            if not a_device_name:
                skip_reason = "A端设备名称为空"
            elif not b_device_name:
                skip_reason = "B端设备名称为空"
            elif a_device_name not in device_names:
                skip_reason = f"A端设备'{a_device_name}'在数据库中不存在"
            elif b_device_name not in device_names:
                skip_reason = f"B端设备'{b_device_name}'在数据库中不存在"
            
            if skip_reason:
                skipped_connections += 1
                if skip_reason not in skip_reasons:
                    skip_reasons[skip_reason] = []
                skip_reasons[skip_reason].append(row_num)
                
                # 显示前10个跳过的行的详细信息
                if skipped_connections <= 10:
                    print(f"第{row_num}行被跳过: {skip_reason}")
                    print(f"  A端设备: '{a_device_name}'")
                    print(f"  B端设备: '{b_device_name}'")
            else:
                valid_connections += 1
        
        # 统计结果
        print(f"\n=== 分析结果统计 ===")
        print(f"有效连接数: {valid_connections}")
        print(f"跳过连接数: {skipped_connections}")
        print(f"总连接数: {valid_connections + skipped_connections}")
        
        # 跳过原因统计
        print(f"\n=== 跳过原因统计 ===")
        for reason, rows in skip_reasons.items():
            print(f"{reason}: {len(rows)}行")
            if len(rows) <= 5:
                print(f"  涉及行号: {rows}")
            else:
                print(f"  涉及行号: {rows[:5]}... (共{len(rows)}行)")
        
        # 检查数据库中实际的连接数
        cursor.execute("SELECT COUNT(*) FROM connections")
        db_connections = cursor.fetchone()[0]
        print(f"\n数据库中实际连接数: {db_connections}")
        
        if db_connections != valid_connections:
            print(f"警告：预期有效连接数({valid_connections})与数据库实际连接数({db_connections})不匹配！")
        
    except Exception as e:
        print(f"分析过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_excel_import_issues()