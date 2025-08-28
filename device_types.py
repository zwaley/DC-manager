# -*- coding: utf-8 -*-
"""
设备类型定义模块
定义系统中使用的标准设备类型和相关分类函数
"""

# 标准设备类型列表（用户在Excel表格中必须使用这些标准格式填报）
STANDARD_DEVICE_TYPES = [
    "发电机组",
    "直流系统设备", 
    "交、直流配电设备",
    "交流UPS主机",
    "高压配电设备",
    "中央空调主机",
    "机房专用精密空调（列间空调）",
    "普通空调",
    "太阳能光伏组件",
    "油机启动电池",
    "-48V直流系统2V阀控铅酸蓄电池",
    "UPS系统阀控式铅酸蓄电池",
    "操作电源2V、6V、12V阀控式铅酸蓄电池"
]

# 设备类型分类（用于拓扑图层级算法的辅助判断，但不决定层级）
# 注意：拓扑图层级主要基于连接关系确定，这些分类仅用于辅助处理双向连接等特殊情况

def is_power_source_type(device_type: str) -> bool:
    """
    判断是否为电源类设备
    注意：此函数仅用于处理双向连接等特殊情况的辅助判断，
    拓扑图层级主要基于连接关系的hierarchy_relation字段确定
    """
    power_source_keywords = [
        "发电机组", "交流UPS主机", "高压配电设备", "交、直流配电设备",
        "直流系统设备", "太阳能光伏组件"
    ]
    return any(keyword in device_type for keyword in power_source_keywords)

def is_storage_type(device_type: str) -> bool:
    """
    判断是否为储能类设备
    注意：此函数仅用于处理双向连接等特殊情况的辅助判断，
    拓扑图层级主要基于连接关系的hierarchy_relation字段确定
    """
    storage_keywords = [
        "油机启动电池", "-48V直流系统2V阀控铅酸蓄电池", 
        "UPS系统阀控式铅酸蓄电池", "操作电源2V、6V、12V阀控式铅酸蓄电池"
    ]
    return any(keyword in device_type for keyword in storage_keywords)

def is_hvac_type(device_type: str) -> bool:
    """
    判断是否为空调类设备
    """
    hvac_keywords = [
        "中央空调主机", "机房专用精密空调（列间空调）", "普通空调"
    ]
    return any(keyword in device_type for keyword in hvac_keywords)

def get_device_type_category(device_type: str) -> str:
    """
    获取设备类型的分类
    返回值：'power_source', 'storage', 'hvac', 'other'
    """
    if is_power_source_type(device_type):
        return 'power_source'
    elif is_storage_type(device_type):
        return 'storage'
    elif is_hvac_type(device_type):
        return 'hvac'
    else:
        return 'other'

# 连接类型定义
STANDARD_CONNECTION_TYPES = ["交流", "直流"]

# 设备类型验证函数
def validate_device_type(device_type: str) -> bool:
    """
    验证设备类型是否在标准列表中
    """
    return device_type in STANDARD_DEVICE_TYPES

def get_device_type_suggestions(partial_type: str) -> list:
    """
    根据部分输入获取设备类型建议
    """
    if not partial_type:
        return STANDARD_DEVICE_TYPES
    
    suggestions = []
    partial_lower = partial_type.lower()
    
    for device_type in STANDARD_DEVICE_TYPES:
        if partial_lower in device_type.lower():
            suggestions.append(device_type)
    
    return suggestions