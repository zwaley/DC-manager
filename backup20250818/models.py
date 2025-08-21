# 导入 SQLAlchemy 所需的模块
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# --- 数据库设置 ---

# 定义数据库连接URL
# 我们将使用 SQLite 数据库。数据库文件将保存在 /app/database/asset.db
# 这个路径对应于 docker-compose.yml 中定义的命名卷，以实现数据持久化。
DATABASE_URL = "sqlite:///./database/asset.db"

# 创建数据库引擎
# connect_args={"check_same_thread": False} 是 SQLite 特有的配置，
# 因为 FastAPI 是多线程的，需要这个选项来允许在不同线程中共享连接。
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建一个数据库会话的工厂
# autocommit=False 和 autoflush=False 确保事务控制是手动的，这在Web应用中是最佳实践。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建一个基础类，我们的 ORM 模型将继承这个类。
Base = declarative_base()


# --- ORM 模型定义 ---

class Device(Base):
    """
    设备模型 (Device Model)
    对应数据库中的 'devices' 表。
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    # 将 model_type 修改为 model
    model = Column(String)
    # 新增 location 字段
    location = Column(String)
    # 新增 power_rating 字段
    power_rating = Column(String) # 使用 String 类型以增加灵活性，例如可以存储 "200W"
    # 保留 vendor, commission_date, remark 作为额外信息
    vendor = Column(String)
    commission_date = Column(String)
    remark = Column(String)

    # 定义与 Connection 模型的关系
    # 'source_connections' 属性将是一个列表，包含所有以此设备为源设备的连接。
    # 'back_populates' 参数指定了在关联的 Connection 模型中，哪个属性反向引用回这个 Device。
    source_connections = relationship(
        "Connection", 
        foreign_keys="[Connection.source_device_id]", 
        back_populates="source_device"
    )
    # 'target_connections' 属性将是一个列表，包含所有以此设备为目标设备的连接。
    target_connections = relationship(
        "Connection", 
        foreign_keys="[Connection.target_device_id]", 
        back_populates="target_device"
    )

class Connection(Base):
    """
    连接模型 (Connection Model)
    对应数据库中的 'connections' 表。
    """
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    source_device_id = Column(Integer, ForeignKey("devices.id"))
    source_port = Column(String)
    target_device_id = Column(Integer, ForeignKey("devices.id"))
    target_port = Column(String)
    cable_type = Column(String)

    # 定义与 Device 模型的关系
    # 'source_device' 属性将引用源设备对象。
    source_device = relationship(
        "Device", 
        foreign_keys=[source_device_id], 
        back_populates="source_connections"
    )
    # 'target_device' 属性将引用目标设备对象。
    target_device = relationship(
        "Device", 
        foreign_keys=[target_device_id], 
        back_populates="target_connections"
    )

# --- 数据库初始化函数 ---

def create_db_and_tables():
    """
    创建数据库文件以及在上面定义的所有表。
    这个函数应该在应用程序启动时被调用一次。
    """
    # Base.metadata.create_all 会检查表是否存在，如果不存在，则创建它们。
    Base.metadata.create_all(bind=engine)