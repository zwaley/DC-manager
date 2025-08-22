# 导入 SQLAlchemy 所需的模块
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Date, Float, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
import os

# 导入配置
from config import DATABASE_URL

# --- 数据库设置 ---

# 确保数据库目录存在
os.makedirs(os.path.dirname(DATABASE_URL.replace('sqlite:///', '')), exist_ok=True)

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
    # 新增资产编号字段，作为唯一标识符，要求唯一、有索引且不能为空
    asset_id = Column(String, unique=True, index=True, nullable=False)
    # 设备名称不再要求唯一，因为资产编号是唯一标识
    name = Column(String, index=True, nullable=False)
    # 新增局站字段，用于标识设备所属的局站
    station = Column(String, index=True, nullable=False)
    # 将 model_type 修改为 model
    model = Column(String)
    # 新增设备类型字段，用于生命周期管理，支持用户自定义设备类型
    device_type = Column(String, index=True, nullable=True)  # 允许为空，便于数据迁移
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

class LifecycleRule(Base):
    """
    设备生命周期规则模型 (Lifecycle Rule Model)
    对应数据库中的 'lifecycle_rules' 表。
    用于存储不同设备类型的生命周期年限规则。
    """
    __tablename__ = "lifecycle_rules"

    id = Column(Integer, primary_key=True, index=True)
    # 设备类型，作为规则的标识（如：整流器、UPS、蓄电池、开关电源等）
    device_type = Column(String, unique=True, index=True, nullable=False)
    # 生命周期年限（单位：年）
    lifecycle_years = Column(Integer, nullable=False)
    # 临近超限提醒时间（提前多少个月提醒，默认6个月）
    warning_months = Column(Integer, default=6)
    # 规则描述
    description = Column(String)
    # 是否启用该规则
    is_active = Column(String, default="true")  # 使用字符串存储布尔值以保持一致性
    # 创建时间
    created_at = Column(String)
    # 更新时间
    updated_at = Column(String)

class Connection(Base):
    """
    连接模型 (Connection Model)
    对应数据库中的 'connections' 表。
    扩展支持Excel中的18个字段，完整记录设备连接关系信息。
    """
    __tablename__ = "connections"
    
    # 基础字段
    id = Column(Integer, primary_key=True, index=True)
    source_device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    target_device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    
    # A端（源端）信息 - 对应Excel字段2-5
    source_port = Column(String(100))  # A端端口（保留原有字段）
    source_fuse_number = Column(String(50))  # A端熔丝编号
    source_fuse_spec = Column(String(100))  # A端熔丝规格
    source_breaker_number = Column(String(50))  # A端空开编号
    source_breaker_spec = Column(String(100))  # A端空开规格
    
    # B端（目标端）信息 - 对应Excel字段11-15
    target_port = Column(String(100))  # B端端口（保留原有字段）
    target_fuse_number = Column(String(50))  # B端熔丝编号
    target_fuse_spec = Column(String(100))  # B端熔丝规格
    target_breaker_number = Column(String(50))  # B端空开编号
    target_breaker_spec = Column(String(100))  # B端空开规格（对应Excel字段14）
    target_device_location = Column(String(200))  # B端设备位置（非动力设备）
    
    # 连接信息 - 对应Excel字段6-9
    hierarchy_relation = Column(String(20))  # 上下级关系（如：A上B下）
    upstream_downstream = Column(String(20))  # 上下游关系（如：上游、下游）
    connection_type = Column(String(20), nullable=True, default=None)  # 连接类型：cable/busbar/busway，空值表示空闲端口
    cable_model = Column(String(100))  # 电缆型号
    cable_type = Column(String(100))  # 保留原有字段，向后兼容
    
    # 技术参数（从电缆型号和规格推导）
    cable_specification = Column(String(100))  # 电缆规格（如：RVVZ-240mm²）
    parallel_count = Column(Integer, default=1)  # 并联数量（从备注解析）
    rated_current = Column(Float)  # 额定电流(A)（从熔丝/空开规格推导）
    cable_length = Column(Float)  # 电缆长度(m)
    
    # 附加信息 - 对应Excel字段16-18
    source_device_photo = Column(String(500))  # A端设备照片路径
    target_device_photo = Column(String(500))  # B端设备照片路径
    remark = Column(Text)  # 备注
    
    # 系统字段
    installation_date = Column(Date)  # 安装日期
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    增加了详细的日志记录来跟踪数据库初始化过程。
    """
    import os
    import traceback
    
    print("\n=== 数据库初始化开始 ===")
    
    try:
        # 检查数据库目录
        db_dir = os.path.dirname(DATABASE_URL.replace("sqlite:///", ""))
        if db_dir and not os.path.exists(db_dir):
            print(f"创建数据库目录: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
        
        # 检查数据库文件是否存在
        db_file = DATABASE_URL.replace("sqlite:///", "")
        db_exists = os.path.exists(db_file)
        print(f"数据库文件路径: {db_file}")
        print(f"数据库文件是否存在: {db_exists}")
        
        # 创建表
        print("正在创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("数据库表创建完成")
        
        # 验证表是否创建成功
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"数据库中的表: {tables}")
        
        # 检查每个表的结构
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            print(f"表 '{table_name}' 的列: {column_names}")
        
        print("=== 数据库初始化完成 ===")
        
    except Exception as e:
        print(f"\n!!! 数据库初始化失败 !!!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        print("\n完整错误堆栈:")
        traceback.print_exc()
        print("=" * 50)
        raise  # 重新抛出异常，因为数据库初始化失败是严重问题