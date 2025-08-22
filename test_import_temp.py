import pandas as pd
from models import Device, Connection
from main import get_db

# 测试Excel导入过程
excel_file = '设备表.xlsx'

print("=== 开始测试Excel导入过程 ===")

# 获取数据库连接
db = next(get_db())

try:
    # 1. 检查设备数据
    devices = db.query(Device).all()
    print(f"\n数据库中共有 {len(devices)} 个设备")
    
    if len(devices) > 0:
        print("前5个设备:")
        for i, device in enumerate(devices[:5]):
            print(f"  {i+1}. ID={device.id}, 名称='{device.name}'")
    
    # 2. 读取Excel连接数据
    print(f"\n正在读取Excel文件: {excel_file}")
    df_connections = pd.read_excel(excel_file, sheet_name='连接')
    print(f"Excel中共有 {len(df_connections)} 行连接数据")
    
    # 3. 检查前几行连接数据
    print("\n前3行连接数据的设备名称:")
    for i in range(min(3, len(df_connections))):
        row = df_connections.iloc[i]
        source_name = str(row.get('A端设备名称', '')).strip()
        target_name = str(row.get('B端设备名称', '')).strip()
        print(f"  第{i+1}行: A端='{source_name}', B端='{target_name}'")
        
        # 检查设备是否存在
        source_device = db.query(Device).filter(Device.name == source_name).first()
        target_device = db.query(Device).filter(Device.name == target_name).first()
        
        print(f"    A端设备存在: {source_device is not None}")
        print(f"    B端设备存在: {target_device is not None}")
        
        if source_device:
            print(f"    A端设备ID: {source_device.id}")
        if target_device:
            print(f"    B端设备ID: {target_device.id}")
    
    # 4. 检查现有连接
    connections = db.query(Connection).all()
    print(f"\n数据库中现有连接数: {len(connections)}")
    
except Exception as e:
    print(f"测试过程中出错: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    db.close()
    
print("\n=== 测试完成 ===")