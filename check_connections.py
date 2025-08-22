#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 创建数据库连接
engine = create_engine('sqlite:///asset_management.db')
Session = sessionmaker(bind=engine)
db = Session()

try:
    # 检查连接数量
    connection_count = db.query(Connection).count()
    print(f'数据库中连接数量: {connection_count}')
    
    if connection_count > 0:
        # 显示前3个连接
        connections = db.query(Connection).limit(3).all()
        print('\n前3个连接:')
        for c in connections:
            connection_type = getattr(c, 'connection_type', '未知')
            cable_model = getattr(c, 'cable_model', '未知')
            print(f'ID: {c.id}, 源设备ID: {c.source_device_id}, 目标设备ID: {c.target_device_id}, 连接类型: {connection_type}, 电缆型号: {cable_model}')
    else:
        print('数据库中没有连接数据')
        
    # 检查设备数量
    device_count = db.query(Device).count()
    print(f'\n数据库中设备数量: {device_count}')
    
finally:
    db.close()