from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Connection

# 创建数据库连接
engine = create_engine('sqlite:///dc_asset_manager.db')
Session = sessionmaker(bind=engine)
db = Session()

# 查询前10条连接记录
connections = db.query(Connection).limit(10).all()

print('前10条连接记录的connection_type字段:')
for c in connections:
    print(f'ID: {c.id}, connection_type: "{c.connection_type}", source_device_id: {c.source_device_id}, target_device_id: {c.target_device_id}')

# 统计connection_type字段的情况
total_connections = db.query(Connection).count()
connections_with_type = db.query(Connection).filter(Connection.connection_type.isnot(None), Connection.connection_type != '').count()
connections_without_type = total_connections - connections_with_type

print(f'\n统计结果:')
print(f'总连接记录数: {total_connections}')
print(f'有connection_type的记录数: {connections_with_type}')
print(f'无connection_type的记录数: {connections_without_type}')

db.close()