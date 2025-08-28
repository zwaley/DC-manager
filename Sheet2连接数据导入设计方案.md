# Sheet2连接数据导入设计方案

## 1. 设计目标

- **不影响现有设备管理功能**：Sheet2处理作为独立模块，不修改现有设备导入逻辑
- **字段名称一致性**：确保Excel字段、数据库字段、API字段、前端字段完全一致
- **端口逻辑处理**：正确处理熔丝和空开作为设备端口的业务逻辑
- **数据完整性**：确保连接关系数据的完整导入和验证

## 2. Sheet2字段映射表

### Excel字段 → Connection模型字段映射

| Excel字段名 | Connection字段名 | 数据类型 | 说明 | 端口逻辑 |
|------------|-----------------|---------|------|----------|
| A端设备名称 | source_device_name | String | 用于查找source_device_id | - |
| A端熔丝编号 | source_fuse_number | String(50) | A端熔丝编号 | 端口选项1 |
| A端熔丝规格 | source_fuse_spec | String(100) | A端熔丝规格 | 端口选项1 |
| A端空开编号 | source_breaker_number | String(50) | A端空开编号 | 端口选项2 |
| A端空开规格 | source_breaker_spec | String(100) | A端空开规格 | 端口选项2 |
| 上下级 | hierarchy_relation | String(20) | 上下级关系 | - |
| 上下游 | upstream_downstream | String(20) | 上下游关系 | - |
| 连接类型（交流/直流） | connection_type | String(20) | 连接类型 | AC/DC |
| 电缆型号 | cable_model | String(100) | 电缆型号 | - |
| B端设备名称 | target_device_name | String | 用于查找target_device_id | - |
| B端熔丝编号 | target_fuse_number | String(50) | B端熔丝编号 | 端口选项1 |
| B端熔丝规格 | target_fuse_spec | String(100) | B端熔丝规格 | 端口选项1 |
| B端空开编号 | target_breaker_number | String(50) | B端空开编号 | 端口选项2 |
| 空开规格 | target_breaker_spec | String(100) | B端空开规格 | 端口选项2 |
| B端设备位置（非动力设备） | target_device_location | String(200) | B端设备位置 | - |
| A端设备照片 | source_device_photo | String(500) | A端设备照片路径 | - |
| B端设备照片 | target_device_photo | String(500) | B端设备照片路径 | - |
| 备注 | remark | Text | 备注信息 | - |

## 3. 端口逻辑处理规则

### 3.1 端口选择逻辑

对于每个设备端（A端/B端），端口信息遵循以下规则：

```
端口类型选择：
- 如果熔丝编号不为空 → 使用熔丝作为端口
  - source_port = source_fuse_number + " (" + source_fuse_spec + ")"
  - target_port = target_fuse_number + " (" + target_fuse_spec + ")"
  
- 如果熔丝编号为空且空开编号不为空 → 使用空开作为端口
  - source_port = source_breaker_number + " (" + source_breaker_spec + ")"
  - target_port = target_breaker_number + " (" + target_breaker_spec + ")"
  
- 如果都为空 → source_port/target_port = null
```

### 3.2 端口验证规则

```python
def validate_port_logic(row):
    """
    验证端口逻辑：同一连接中，每端只能选择熔丝或空开其中之一
    """
    # A端验证
    a_has_fuse = bool(row.get('A端熔丝编号'))
    a_has_breaker = bool(row.get('A端空开编号'))
    
    # B端验证
    b_has_fuse = bool(row.get('B端熔丝编号'))
    b_has_breaker = bool(row.get('B端空开编号'))
    
    # 验证规则：每端最多只能有一种端口类型
    if a_has_fuse and a_has_breaker:
        return False, "A端不能同时有熔丝和空开"
    if b_has_fuse and b_has_breaker:
        return False, "B端不能同时有熔丝和空开"
        
    return True, "端口逻辑验证通过"
```

## 4. 连接类型映射

### 4.1 Excel值 → 数据库值映射

```python
CONNECTION_TYPE_MAPPING = {
    '电缆': 'cable',
    '交流': 'AC',
'直流': 'DC',
    # 兼容性映射
    'cable': 'cable',
    'busbar': 'busbar',
    'busway': 'busway'
}
```

## 5. 设备名称匹配策略

### 5.1 设备查找逻辑

```python
def find_device_by_name(device_name, db_session):
    """
    通过设备名称查找设备ID
    优先级：完全匹配 > 模糊匹配
    """
    # 1. 完全匹配
    device = db_session.query(Device).filter(Device.name == device_name).first()
    if device:
        return device
    
    # 2. 模糊匹配（去除空格后匹配）
    clean_name = device_name.strip()
    device = db_session.query(Device).filter(Device.name == clean_name).first()
    if device:
        return device
        
    # 3. 包含匹配（设备名称包含查找名称）
    device = db_session.query(Device).filter(Device.name.contains(clean_name)).first()
    return device
```

## 6. 数据验证规则

### 6.1 必填字段验证

```python
REQUIRED_FIELDS = [
    'A端设备名称',
    'B端设备名称', 
    '连接类型（交流 / 直流）'
]
```

### 6.2 数据完整性验证

- A端设备和B端设备必须在数据库中存在
- 连接类型必须是有效值
- 端口逻辑必须符合业务规则
- 不能创建重复的连接关系

## 7. 实现步骤

### 7.1 第一步：扩展upload_excel函数

```python
# 在现有upload_excel函数中添加Sheet2处理
def process_sheet2_connections(excel_file, devices_map, db_session):
    """
    处理Sheet2连接数据
    """
    # 读取Sheet2数据
    df_connections = pd.read_excel(excel_file, sheet_name='连接')
    
    # 处理每一行连接数据
    for index, row in df_connections.iterrows():
        # 验证和处理逻辑
        pass
```

### 7.2 第二步：创建连接处理函数

```python
def create_connection_from_excel_row(row, devices_map, db_session):
    """
    从Excel行数据创建Connection对象
    """
    # 字段映射和验证
    # 设备查找
    # 端口处理
    # 连接创建
    pass
```

### 7.3 第三步：集成到现有流程

在upload_excel函数的步骤5之后添加：

```python
# 步骤 6: 处理Sheet2连接数据
print("\n步骤 6: 处理Sheet2连接数据...")
sheet2_connections_count = process_sheet2_connections(file, devices_map, db)
print(f"从Sheet2创建了 {sheet2_connections_count} 个连接")
```

## 8. 错误处理和日志

### 8.1 错误分类

- **设备不存在错误**：Excel中的设备名称在数据库中找不到
- **端口逻辑错误**：违反熔丝/空开选择规则
- **数据格式错误**：字段值不符合预期格式
- **重复连接错误**：尝试创建已存在的连接

### 8.2 日志记录

```python
# 详细的处理日志
print(f"  - 第 {index+2} 行：处理连接 '{source_device_name}' -> '{target_device_name}'")
print(f"    源端口: {source_port}, 目标端口: {target_port}")
print(f"    连接类型: {connection_type}, 电缆型号: {cable_model}")
```

## 9. 向后兼容性

### 9.1 保持现有功能不变

- Sheet1设备导入逻辑完全不变
- 现有API接口保持兼容
- 前端连接管理页面无需修改

### 9.2 字段名称统一

确保以下组件中的字段名称完全一致：
- models.py中的Connection模型
- main.py中的API接口
- templates/connections.html中的前端代码
- Excel导入处理代码

## 10. 测试计划

### 10.1 单元测试

- 端口逻辑验证函数测试
- 设备名称匹配函数测试
- 连接类型映射测试

### 10.2 集成测试

- 完整Excel文件导入测试
- 错误处理测试
- 数据完整性验证测试

### 10.3 用户验收测试

- 导入真实Excel文件
- 验证连接关系正确性
- 确认设备管理功能未受影响

---

**注意事项：**
1. 所有字段名称必须在各个组件间保持严格一致
2. 端口逻辑处理必须符合业务规则
3. 错误处理要详细，便于用户理解和修正
4. 保持向后兼容，不影响现有功能