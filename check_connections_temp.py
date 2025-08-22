from models import Connection
from main import get_db

# 获取数据库连接
db = next(get_db())

# 查询所有连接
connections = db.query(Connection).all()
print(f'数据库中共有 {len(connections)} 个连接')

# 显示前5个连接的详细信息
for i, conn in enumerate(connections[:5]):
    print(f'{i+1}. 源设备ID: {conn.source_device_id}, 目标设备ID: {conn.target_device_id}')
    print(f'   源端口: {conn.source_port}, 目标端口: {conn.target_port}')
    print(f'   连接类型: {conn.connection_type}, 创建时间: {conn.created_at}')
    print('---')

# 关闭数据库连接
db.close()
print('检查完成')