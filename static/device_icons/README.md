# 设备图标自定义指南

## 概述

本系统支持用户自定义设备图标，通过简单的文件替换和配置修改，可以轻松更换设备在拓扑图中的显示图标。

## 目录结构

```
static/
├── device_icons/           # 用户自定义图标目录
│   ├── icon_config.json   # 图标配置文件
│   └── README.md          # 本说明文件
└── default_icons/         # 系统默认图标目录
    ├── ups.svg
    ├── transformer.svg
    ├── high_voltage_cabinet.svg
    ├── low_voltage_cabinet.svg
    ├── ats_cabinet.svg
    ├── dc_distribution_cabinet.svg
    ├── dc_control_panel.svg
    └── default_device.svg
```

## 自定义图标步骤

### 1. 准备图标文件

- **推荐格式**: SVG（矢量格式，可无损缩放）
- **支持格式**: SVG, PNG, JPG, JPEG
- **推荐尺寸**: 48x48 像素
- **文件命名**: 使用英文名称，避免特殊字符

### 2. 放置图标文件

将准备好的图标文件复制到 `device_icons/` 目录下。

例如：
```
device_icons/
├── my_ups.svg
├── custom_transformer.png
└── special_cabinet.svg
```

### 3. 修改配置文件

编辑 `device_icons/icon_config.json` 文件，修改 `icon_mapping` 部分：

```json
{
  "icon_mapping": {
    "UPS": "my_ups.svg",
    "变压器": "custom_transformer.png",
    "高压配电柜": "special_cabinet.svg",
    "低压配电柜": "low_voltage_cabinet.svg",
    "ATS柜": "ats_cabinet.svg",
    "直流分配柜": "dc_distribution_cabinet.svg",
    "直流操作屏": "dc_control_panel.svg"
  }
}
```

### 4. 重启应用

修改配置后，重启应用程序以使更改生效。

## 配置文件说明

### icon_mapping
设备类型与图标文件的映射关系。键为设备类型名称，值为图标文件名。

### default_icon
当设备类型未在映射中找到时使用的默认图标。

### icon_size
图标的显示尺寸设置。

### search_paths
图标文件的搜索路径，按优先级排序：
1. `./device_icons/` - 用户自定义图标（优先级最高）
2. `./default_icons/` - 系统默认图标

### supported_formats
支持的图标文件格式列表。

### fallback_color
当图标文件无法加载时使用的备用颜色。

## 图标设计建议

### SVG 图标设计要点

1. **尺寸**: 使用 48x48 的 viewBox
2. **颜色**: 使用对比鲜明的颜色，便于识别
3. **细节**: 保持图标简洁，避免过多细节
4. **一致性**: 保持相同的设计风格

### 设备类型图标建议

- **UPS**: 使用蓝色调，突出电源特征
- **变压器**: 使用棕色调，体现变压器的工业特征
- **高压配电柜**: 使用红色调，警示高压危险
- **低压配电柜**: 使用蓝色调，区别于高压设备
- **ATS柜**: 使用紫色调，体现切换功能
- **直流分配柜**: 使用橙色调，突出直流特征
- **直流操作屏**: 使用灰色调，体现控制功能

## 示例：创建自定义UPS图标

1. 创建 `my_ups.svg` 文件：

```svg
<svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <!-- 自定义UPS设计 -->
  <rect x="4" y="12" width="40" height="24" rx="2" fill="#1976D2"/>
  <!-- 添加更多设计元素 -->
</svg>
```

2. 修改 `icon_config.json`：

```json
{
  "icon_mapping": {
    "UPS": "my_ups.svg"
  }
}
```

3. 重启应用程序

## 故障排除

### 图标不显示

1. 检查文件路径是否正确
2. 确认文件格式是否支持
3. 检查配置文件语法是否正确
4. 查看应用程序日志获取错误信息

### 图标显示异常

1. 检查图标文件是否损坏
2. 确认图标尺寸是否合适
3. 对于SVG文件，检查语法是否正确

## 技术支持

如果在使用过程中遇到问题，请：

1. 检查本文档的故障排除部分
2. 查看应用程序日志文件
3. 联系技术支持团队

---

**注意**: 修改图标配置后需要重启应用程序才能生效。建议在修改前备份原始配置文件。