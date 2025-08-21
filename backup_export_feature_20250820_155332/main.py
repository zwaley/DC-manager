import os
from fastapi import FastAPI, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import pandas as pd
from typing import List, Optional
from urllib.parse import quote
import io
import traceback # 导入 traceback 用于打印详细的错误堆栈
from datetime import datetime, timedelta
import re

# 修正了导入，使用正确的函数名和模型
from models import SessionLocal, Device, Connection, LifecycleRule, create_db_and_tables

# --- 权限控制配置 ---
ADMIN_PASSWORD = "admin123"  # 管理员密码，实际部署时应该使用更安全的密码

def verify_admin_password(password: str) -> bool:
    """
    验证管理员密码
    Args:
        password: 用户输入的密码
    Returns:
        bool: 密码是否正确
    """
    return password == ADMIN_PASSWORD

# --- FastAPI 应用设置 ---

app = FastAPI(
    title="安吉电信动力设备管理系统",
    description="一个用于管理和可视化数据中心动力设备资产的Web应用。",
    version="1.1.0" # 版本升级
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
# 设置模板目录
templates = Jinja2Templates(directory="templates")

# --- 数据库会话管理 ---

def get_db():
    """
    数据库会话管理函数
    增加了详细的日志记录来跟踪数据库连接的创建和关闭过程
    """
    print("\n--- 创建数据库会话 ---")
    db = None
    try:
        db = SessionLocal()
        print(f"数据库会话创建成功: {id(db)}")
        yield db
    except Exception as e:
        print(f"数据库会话创建失败: {e}")
        if db:
            print("正在回滚数据库事务...")
            db.rollback()
        raise
    finally:
        if db:
            print(f"正在关闭数据库会话: {id(db)}")
            db.close()
            print("数据库会话已关闭")
        print("--- 数据库会话管理结束 ---\n")

# --- 应用启动事件 ---

@app.on_event("startup")
def on_startup():
    """
    应用启动事件处理函数
    增加了详细的日志记录来跟踪应用启动过程
    """
    print("\n" + "=" * 60)
    print("🚀 动力资源资产管理系统启动中...")
    print("=" * 60)
    
    try:
        # 检查并创建数据库目录
        db_dir = './database'
        if not os.path.exists(db_dir):
            print(f"📁 创建数据库目录: {db_dir}")
            os.makedirs(db_dir)
        else:
            print(f"📁 数据库目录已存在: {db_dir}")
        
        # 初始化数据库
        print("🗄️ 正在初始化数据库...")
        create_db_and_tables()
        
        print("✅ 应用启动完成！")
        print("🌐 服务器地址: http://localhost:8000")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 应用启动失败!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        print("\n完整错误堆栈:")
        traceback.print_exc()
        print("=" * 60)
        raise  # 重新抛出异常，停止应用启动

# --- 路由和视图函数 ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    """
    首页路由 - 显示所有设备列表
    增加了详细的日志记录来跟踪数据获取过程
    """
    print("\n=== 首页数据获取开始 ===")
    
    try:
        # 获取设备数据
        print("正在从数据库查询设备数据...")
        devices = db.query(Device).order_by(Device.id).all()
        device_count = len(devices)
        print(f"查询到 {device_count} 个设备")
        
        # 获取生命周期规则
        lifecycle_rules = db.query(LifecycleRule).filter(LifecycleRule.is_active == 'true').all()
        rules_dict = {rule.device_type: rule for rule in lifecycle_rules}
        print(f"加载了 {len(rules_dict)} 个生命周期规则")
        
        # 为每个设备计算生命周期状态
        for device in devices:
            lifecycle_status = "unknown"
            lifecycle_status_text = "未配置规则"
            
            if device.device_type and device.device_type in rules_dict:
                rule = rules_dict[device.device_type]
                if device.commission_date:
                    try:
                        # 解析投产日期
                        commission_date = None
                        date_str = str(device.commission_date).strip()
                        
                        # 处理特殊格式：YYYYMM (如 202312)
                        if re.match(r'^\d{6}$', date_str):
                            try:
                                year = int(date_str[:4])
                                month = int(date_str[4:6])
                                commission_date = datetime(year, month, 1)
                            except ValueError:
                                pass
                        
                        # 如果特殊格式解析失败，尝试标准格式
                        if not commission_date:
                            date_formats = [
                                "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
                                "%Y-%m", "%Y/%m", "%Y.%m",
                                "%Y年%m月%d日", "%Y年%m月"
                            ]
                            
                            for fmt in date_formats:
                                try:
                                    commission_date = datetime.strptime(date_str, fmt)
                                    break
                                except ValueError:
                                    continue
                        
                        if commission_date:
                            # 计算服役时间
                            today = datetime.now()
                            service_years = (today - commission_date).days / 365.25
                            
                            # 判断状态
                            if service_years >= rule.lifecycle_years:
                                lifecycle_status = "expired"
                                lifecycle_status_text = "已超期"
                            elif service_years >= (rule.lifecycle_years - rule.warning_months / 12):
                                lifecycle_status = "warning"
                                lifecycle_status_text = "临近超限"
                            else:
                                lifecycle_status = "normal"
                                lifecycle_status_text = "正常"
                        else:
                            lifecycle_status = "unknown"
                            lifecycle_status_text = "投产日期格式无法识别"
                    except Exception as e:
                        lifecycle_status = "unknown"
                        lifecycle_status_text = "投产日期格式无法识别"
                else:
                    lifecycle_status = "unknown"
                    lifecycle_status_text = "投产日期未填写"
            
            # 将状态信息添加到设备对象
            device.lifecycle_status = lifecycle_status
            device.lifecycle_status_text = lifecycle_status_text
        
        # 显示前几个设备的信息用于调试
        if device_count > 0:
            print("\n前3个设备信息:")
            for i, device in enumerate(devices[:3]):
                print(f"  设备{i+1}: ID={device.id}, 资产编号={device.asset_id}, 名称={device.name}, 生命周期状态={device.lifecycle_status}")
        else:
            print("警告: 数据库中没有设备数据！")
        
        # 获取连接数据用于统计
        connections = db.query(Connection).all()
        connection_count = len(connections)
        print(f"数据库中共有 {connection_count} 个连接")
        
        # 获取所有不重复的局站列表，用于筛选下拉框
        print("正在获取局站列表...")
        stations = db.query(Device.station).filter(Device.station.isnot(None)).filter(Device.station != '').distinct().all()
        station_list = [station[0] for station in stations if station[0]]  # 提取局站名称并过滤空值
        station_list.sort()  # 按字母顺序排序
        print(f"找到 {len(station_list)} 个不同的局站: {station_list}")
        
        # 获取所有不重复的设备类型列表，用于筛选下拉框
        print("正在获取设备类型列表...")
        device_types = db.query(Device.device_type).filter(Device.device_type.isnot(None)).filter(Device.device_type != '').distinct().all()
        device_type_list = [device_type[0] for device_type in device_types if device_type[0]]  # 提取设备类型并过滤空值
        device_type_list.sort()  # 按字母顺序排序
        print(f"找到 {len(device_type_list)} 个不同的设备类型: {device_type_list}")
        
        # 获取所有不重复的厂家列表，用于筛选下拉框
        print("正在获取厂家列表...")
        vendors = db.query(Device.vendor).filter(Device.vendor.isnot(None)).filter(Device.vendor != '').distinct().all()
        vendor_list = [vendor[0] for vendor in vendors if vendor[0]]  # 提取厂家名称并过滤空值
        vendor_list.sort()  # 按字母顺序排序
        print(f"找到 {len(vendor_list)} 个不同的厂家: {vendor_list}")
        
        # 检查是否有上传错误信息
        upload_error = request.query_params.get("error")
        if upload_error:
            print(f"检测到上传错误信息: {upload_error}")
        else:
            print("没有上传错误信息")
        
        # 检查是否有成功信息
        success_message = request.query_params.get("success")
        if success_message:
            print(f"检测到成功信息: {success_message}")
        else:
            print("没有成功信息")
        
        print("=== 首页数据获取完成 ===")
        
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "devices": devices, 
            "stations": station_list,
            "device_types": device_type_list,
            "vendors": vendor_list,
            "upload_error": upload_error,
            "success_message": success_message
        })
        
    except Exception as e:
        print(f"\n!!! 首页数据获取失败 !!!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        print("\n完整错误堆栈:")
        traceback.print_exc()
        print("=" * 50)
        
        # 返回错误页面或空设备列表
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "devices": [], 
            "stations": [],
            "device_types": [],
            "vendors": [],
            "upload_error": f"获取设备数据时出错: {e}"
        })

@app.post("/upload")
async def upload_excel(file: UploadFile = File(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    处理 Excel 文件上传。
    如果失败，则重定向回主页并附带详细错误信息。
    增加了详细的日志记录来跟踪处理过程。
    """
    print("\n=== 开始处理上传的Excel文件 ===")
    print(f"上传文件名: {file.filename}")
    print(f"文件类型: {file.content_type}")
    
    # 验证管理员密码
    if not verify_admin_password(password):
        error_message = "密码错误，无权限执行此操作。"
        print(f"权限验证失败: {error_message}")
        return RedirectResponse(url=f"/?error={quote(error_message)}", status_code=303)
    
    print("管理员密码验证通过")
    
    try:
        # 步骤 1: 增量更新模式 - 保留手工添加的设备，只更新Excel中的设备
        print("\n步骤 1: 采用增量更新模式，保留现有手工添加的设备...")
        
        # 记录当前数据量
        current_connections_count = db.query(Connection).count()
        current_devices_count = db.query(Device).count()
        print(f"当前数据库状态: {current_connections_count} 个连接, {current_devices_count} 个设备")
        print("步骤 1: 完成。将采用增量更新模式处理Excel数据。")

        contents = await file.read()
        print(f"文件大小: {len(contents)} 字节")
        buffer = io.BytesIO(contents)
        
        # 步骤 2: 读取Excel文件
        print("\n步骤 2: 使用 pandas 读取Excel文件...")
        # 通过 dtype 参数指定列以字符串形式读取，避免自动转换格式
        # 重要：假设"上级设备"列现在包含的是父设备的资产编号
        df = pd.read_excel(buffer, dtype={
            '资产编号': str,
            '设备投产时间': str,
            '上级设备': str 
        })
        df = df.where(pd.notna(df), None) # 将 NaN 替换为 None
        print(f"步骤 2: 完成。读取到 {len(df)} 行数据。")
        print(f"Excel 文件列名: {df.columns.tolist()}")
        
        # 验证必要的列是否存在
        required_columns = ['资产编号', '设备名称']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Excel文件缺少必要的列: {missing_columns}"
            print(f"错误: {error_msg}")
            return RedirectResponse(url=f"/?error={quote(error_msg)}", status_code=303)
        
        # 显示前几行数据样本用于调试
        print("\n前3行数据样本:")
        for i in range(min(3, len(df))):
            print(f"第{i+1}行: 资产编号={df.iloc[i].get('资产编号')}, 设备名称={df.iloc[i].get('设备名称')}")

        devices_map = {} # 这个映射将以 资产编号 为键
        devices_created_count = 0
        devices_updated_count = 0
        skipped_rows = []

        # 步骤 3: 增量更新设备（创建或更新）
        print("\n步骤 3: 开始第一遍处理 - 增量更新设备（创建新设备或更新现有设备）...")
        for index, row in df.iterrows():
            # 新增：获取并校验资产编号
            asset_id = row.get("资产编号")
            if isinstance(asset_id, str):
                asset_id = asset_id.strip()

            if not asset_id or asset_id == 'nan' or asset_id.lower() == 'none':
                skip_reason = f"资产编号为空或无效: '{asset_id}'"
                print(f"  - 第 {index+2} 行：跳过，{skip_reason}")
                skipped_rows.append((index+2, skip_reason))
                continue
            
            device_name = row.get("设备名称")
            if isinstance(device_name, str):
                device_name = device_name.strip()

            if not device_name or device_name == 'nan' or device_name.lower() == 'none':
                skip_reason = f"设备名称为空或无效: '{device_name}'"
                print(f"  - 第 {index+2} 行：跳过，{skip_reason}")
                skipped_rows.append((index+2, skip_reason))
                continue
            
            # 检查资产编号是否已在本次上传中重复
            if asset_id in devices_map:
                skip_reason = f"资产编号 '{asset_id}' 在Excel文件中重复"
                print(f"  - 第 {index+2} 行：跳过，{skip_reason}")
                skipped_rows.append((index+2, skip_reason))
                continue

            try:
                # 检查数据库中是否已存在该资产编号的设备
                existing_device = db.query(Device).filter(Device.asset_id == asset_id).first()
                
                # 获取局站信息
                station = row.get("局站")
                if isinstance(station, str):
                    station = station.strip()
                if not station or station == 'nan' or station.lower() == 'none':
                    skip_reason = f"局站信息为空或无效: '{station}'"
                    print(f"  - 第 {index+2} 行：跳过，{skip_reason}")
                    skipped_rows.append((index+2, skip_reason))
                    continue
                
                if existing_device:
                    # 更新现有设备
                    existing_device.name = device_name
                    existing_device.station = station
                    existing_device.model = row.get("设备型号")
                    existing_device.device_type = row.get("设备类型")
                    existing_device.location = row.get("机房内空间位置")
                    existing_device.power_rating = row.get("设备额定容量")
                    existing_device.vendor = row.get("设备生产厂家")
                    existing_device.commission_date = row.get("设备投产时间")
                    existing_device.remark = row.get("备注")
                    
                    devices_map[asset_id] = existing_device
                    devices_updated_count += 1
                    print(f"  - 第 {index+2} 行：准备更新现有设备 '{device_name}' (资产编号: {asset_id}, 局站: {station})")
                else:
                    # 创建新设备
                    device = Device(
                        asset_id=asset_id,
                        name=device_name,
                        station=station,
                        model=row.get("设备型号"),
                        device_type=row.get("设备类型"),
                        location=row.get("机房内空间位置"),
                        power_rating=row.get("设备额定容量"),
                        vendor=row.get("设备生产厂家"),
                        commission_date=row.get("设备投产时间"),
                        remark=row.get("备注")
                    )
                    db.add(device)
                    devices_map[asset_id] = device
                    devices_created_count += 1
                    print(f"  - 第 {index+2} 行：准备创建新设备 '{device_name}' (资产编号: {asset_id}, 局站: {station})")
                    
            except Exception as device_error:
                skip_reason = f"处理设备失败: {device_error}"
                print(f"  - 第 {index+2} 行：跳过，{skip_reason}")
                skipped_rows.append((index+2, skip_reason))
                continue
        
        print(f"\n准备提交设备更改到数据库（新建: {devices_created_count}, 更新: {devices_updated_count}）...")
        try:
            db.commit() # 提交事务以生成设备ID
            print("设备提交成功！")
        except Exception as commit_error:
            print(f"设备提交失败: {commit_error}")
            db.rollback()
            raise commit_error
            
        # 验证设备数量
        actual_device_count = db.query(Device).count()
        print(f"步骤 3: 完成。新建 {devices_created_count} 个设备，更新 {devices_updated_count} 个设备，数据库中总共有 {actual_device_count} 个设备。")
        
        if skipped_rows:
            print(f"\n跳过的行数统计: {len(skipped_rows)} 行")
            for row_num, reason in skipped_rows[:5]:  # 只显示前5个
                print(f"  第{row_num}行: {reason}")
            if len(skipped_rows) > 5:
                print(f"  ... 还有 {len(skipped_rows) - 5} 行被跳过")

        # 刷新映射，确保对象包含数据库生成的ID
        print("\n刷新设备对象以获取数据库生成的ID...")
        for asset_id_key in list(devices_map.keys()):
            try:
                db.refresh(devices_map[asset_id_key])
                print(f"  设备 {asset_id_key} ID: {devices_map[asset_id_key].id}")
            except Exception as refresh_error:
                print(f"  刷新设备 {asset_id_key} 失败: {refresh_error}")

        # 步骤 4: 清理涉及Excel设备的旧连接
        print("\n步骤 4: 清理涉及Excel中设备的旧连接...")
        excel_device_ids = [device.id for device in devices_map.values()]
        if excel_device_ids:
            # 删除涉及这些设备的所有连接（作为源设备或目标设备）
            old_connections_deleted = db.query(Connection).filter(
                (Connection.source_device_id.in_(excel_device_ids)) |
                (Connection.target_device_id.in_(excel_device_ids))
            ).delete(synchronize_session=False)
            db.commit()
            print(f"删除了 {old_connections_deleted} 个涉及Excel设备的旧连接")
        else:
            print("没有Excel设备，跳过连接清理")
            
        connections_created_count = 0
        connection_skipped_rows = []
        
        # 步骤 5: 创建新连接
        print("\n步骤 5: 开始第二遍处理 - 创建新连接...")
        for index, row in df.iterrows():
            # 使用资产编号来查找设备
            source_asset_id = row.get("上级设备")
            target_asset_id = row.get("资产编号")

            if isinstance(source_asset_id, str):
                source_asset_id = source_asset_id.strip()
            if isinstance(target_asset_id, str):
                target_asset_id = target_asset_id.strip()
            
            # 检查是否有上级设备信息
            if not source_asset_id or source_asset_id == 'nan' or source_asset_id.lower() == 'none':
                print(f"  - 第 {index+2} 行：跳过连接创建，无上级设备信息")
                continue
                
            # 确保源和目标设备都存在于映射中
            if target_asset_id and source_asset_id:
                if source_asset_id not in devices_map:
                    skip_reason = f"上级设备 '{source_asset_id}' 不存在"
                    print(f"  - 第 {index+2} 行：跳过连接，{skip_reason}")
                    connection_skipped_rows.append((index+2, skip_reason))
                    continue
                    
                if target_asset_id not in devices_map:
                    skip_reason = f"目标设备 '{target_asset_id}' 不存在"
                    print(f"  - 第 {index+2} 行：跳过连接，{skip_reason}")
                    connection_skipped_rows.append((index+2, skip_reason))
                    continue
                
                source_device = devices_map[source_asset_id]
                target_device = devices_map[target_asset_id]
                
                try:
                    connection = Connection(
                        source_device_id=source_device.id,
                        source_port=row.get("上级端口"),
                        target_device_id=target_device.id,
                        target_port=row.get("本端端口"),
                        cable_type=row.get("线缆类型")
                    )
                    db.add(connection)
                    connections_created_count += 1
                    print(f"  - 第 {index+2} 行：准备创建从 '{source_device.name}' 到 '{target_device.name}' 的连接")
                except Exception as conn_error:
                    skip_reason = f"创建连接对象失败: {conn_error}"
                    print(f"  - 第 {index+2} 行：跳过连接，{skip_reason}")
                    connection_skipped_rows.append((index+2, skip_reason))
                    continue
        
        print(f"\n准备提交 {connections_created_count} 个连接到数据库...")
        try:
            db.commit()
            print("连接提交成功！")
        except Exception as commit_error:
            print(f"连接提交失败: {commit_error}")
            db.rollback()
            raise commit_error
            
        # 验证连接是否真的被创建
        actual_connection_count = db.query(Connection).count()
        print(f"步骤 5: 完成。预期创建 {connections_created_count} 个连接，实际数据库中有 {actual_connection_count} 个连接。")
        
        if connection_skipped_rows:
            print(f"\n连接跳过的行数统计: {len(connection_skipped_rows)} 行")
            for row_num, reason in connection_skipped_rows[:5]:  # 只显示前5个
                print(f"  第{row_num}行: {reason}")
            if len(connection_skipped_rows) > 5:
                print(f"  ... 还有 {len(connection_skipped_rows) - 5} 行连接被跳过")
                
        print("\n=== Excel文件增量更新处理成功 ===")
        print(f"处理结果: 新建 {devices_created_count} 个设备, 更新 {devices_updated_count} 个设备, 创建 {connections_created_count} 个连接")
        print(f"数据库最终状态: {actual_device_count} 个设备, {actual_connection_count} 个连接")

    except Exception as e:
        print(f"\n!!! 发生异常，开始回滚事务 !!!")
        try:
            db.rollback()
            print("事务回滚成功")
        except Exception as rollback_error:
            print(f"事务回滚失败: {rollback_error}")
            
        error_message = f"处理Excel文件时出错: {e}"
        print(f"\n=== Excel文件处理失败 ===")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {error_message}")
        print("\n完整错误堆栈:")
        traceback.print_exc()
        print("=" * 50)
        
        # 检查数据库状态
        try:
            final_device_count = db.query(Device).count()
            final_connection_count = db.query(Connection).count()
            print(f"\n错误后数据库状态: {final_device_count} 个设备, {final_connection_count} 个连接")
        except Exception as db_check_error:
            print(f"无法检查数据库状态: {db_check_error}")
            
        return RedirectResponse(url=f"/?error={quote(error_message)}", status_code=303)

    print(f"\n上传处理完成，重定向到首页...")
    return RedirectResponse(url="/", status_code=303)

# 更新设备信息
@app.post("/devices/{device_id}")
async def update_device(
    device_id: int,
    asset_id: str = Form(...),
    name: str = Form(...),
    station: str = Form(...),
    model: str = Form(None),
    device_type: str = Form(None),
    location: str = Form(None),
    power_rating: str = Form(None),
    vendor: str = Form(None),
    commission_date: str = Form(None),
    remark: str = Form(None),
    db: Session = Depends(get_db)
):
    """更新设备信息（编辑功能不需要密码验证，因为在进入编辑页面时已验证）"""
    try:
        # 获取要更新的设备
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            error_message = "设备不存在。"
            return RedirectResponse(url=f"/?error={quote(error_message)}", status_code=303)
        
        # 检查资产编号唯一性（排除当前设备）
        existing_device = db.query(Device).filter(
            Device.asset_id == asset_id,
            Device.id != device_id
        ).first()
        if existing_device:
            error_message = f"资产编号 {asset_id} 已存在，请使用其他编号。"
            return RedirectResponse(url=f"/?error={quote(error_message)}", status_code=303)
        
        # 更新设备信息
        device.asset_id = asset_id
        device.name = name
        device.station = station
        device.model = model if model else None
        device.device_type = device_type if device_type else None
        device.location = location if location else None
        device.power_rating = power_rating if power_rating else None
        device.vendor = vendor if vendor else None
        device.commission_date = commission_date if commission_date else None
        device.remark = remark if remark else None
        
        db.commit()
        
        success_message = f"设备 {name} 更新成功。"
        return RedirectResponse(url=f"/?success={quote(success_message)}", status_code=303)
        
    except Exception as e:
        db.rollback()
        error_message = f"更新设备失败：{str(e)}"
        return RedirectResponse(url=f"/?error={quote(error_message)}", status_code=303)

# 编辑设备页面
@app.get("/edit/{device_id}")
async def edit_device_page(device_id: int, password: str, request: Request, db: Session = Depends(get_db)):
    """显示编辑设备页面"""
    # 验证管理员密码
    if not verify_admin_password(password):
        error_message = "密码错误，无权限执行此操作。"
        return RedirectResponse(url=f"/?error={quote(error_message)}", status_code=303)
    
    # 获取设备信息
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        error_message = "设备不存在。"
        return RedirectResponse(url=f"/?error={quote(error_message)}", status_code=303)
    
    return templates.TemplateResponse("edit_device.html", {
        "request": request,
        "device": device
    })

# 删除设备
@app.delete("/devices/{device_id}")
async def delete_device(device_id: int, request: Request, db: Session = Depends(get_db)):
    """删除设备"""
    try:
        # 获取请求体中的密码
        body = await request.json()
        password = body.get("password")
        
        # 验证管理员密码
        if not verify_admin_password(password):
            raise HTTPException(status_code=403, detail="密码错误，无权限执行此操作。")
        
        # 获取要删除的设备
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="设备不存在。")
        
        device_name = device.name
        
        # 删除相关的连接记录
        db.query(Connection).filter(
            (Connection.source_device_id == device_id) | 
            (Connection.target_device_id == device_id)
        ).delete()
        
        # 删除设备
        db.delete(device)
        db.commit()
        
        return {"message": f"设备 {device_name} 删除成功。"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除设备失败：{str(e)}")

@app.post("/devices")
async def create_device(
    asset_id: str = Form(...),
    name: str = Form(...),
    station: str = Form(...),
    model: str = Form(None),
    device_type: str = Form(None),
    location: str = Form(None),
    power_rating: str = Form(None),
    vendor: str = Form(None),
    commission_date: str = Form(None),
    remark: str = Form(None),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 验证管理员密码
    if not verify_admin_password(password):
        error_message = "密码错误，无权限执行此操作。"
        return RedirectResponse(url=f"/?error={quote(error_message)}", status_code=303)
    
    # 增加资产编号唯一性校验
    existing_device = db.query(Device).filter(Device.asset_id == asset_id).first()
    if existing_device:
        # 如果存在，则重定向回主页并显示错误信息
        error_message = f"创建失败：资产编号 '{asset_id}' 已存在。"
        return RedirectResponse(url=f"/?error={quote(error_message)}", status_code=303)

    new_device = Device(
        asset_id=asset_id,
        name=name,
        station=station,
        model=model,
        device_type=device_type,
        location=location,
        power_rating=power_rating,
        vendor=vendor,
        commission_date=commission_date,
        remark=remark
    )
    db.add(new_device)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/graph_data/{device_id}")
async def get_graph_data(device_id: int, db: Session = Depends(get_db)):
    nodes = []
    edges = []
    processed_ids = set()

    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    queue = [device]
    visited_ids = {device.id}

    while queue:
        current_device = queue.pop(0)

        if current_device.id not in processed_ids:
            # 在悬浮提示中也加入资产编号
            nodes.append({
                "id": current_device.id,
                "label": current_device.name,
                "title": f"""<b>资产编号:</b> {current_device.asset_id}<br>
                             <b>名称:</b> {current_device.name}<br>
                             <b>型号:</b> {current_device.model or 'N/A'}<br>
                             <b>位置:</b> {current_device.location or 'N/A'}<br>
                             <b>功率:</b> {current_device.power_rating or 'N/A'}""",
                "level": 0 
            })
            processed_ids.add(current_device.id)

        # 向上游查找
        for conn in current_device.target_connections:
            source_device = conn.source_device
            if source_device and source_device.id not in visited_ids:
                edges.append({"from": source_device.id, "to": current_device.id, "arrows": "to", "label": conn.cable_type or ""})
                visited_ids.add(source_device.id)
                queue.append(source_device)

        # 向下游查找
        for conn in current_device.source_connections:
            target_device = conn.target_device
            if target_device and target_device.id not in visited_ids:
                edges.append({"from": current_device.id, "to": target_device.id, "arrows": "to", "label": conn.cable_type or ""})
                visited_ids.add(target_device.id)
                queue.append(target_device)
                
    return JSONResponse(content={"nodes": nodes, "edges": edges})


@app.get("/graph/{device_id}", response_class=HTMLResponse)
async def get_power_chain_graph(request: Request, device_id: int):
    return templates.TemplateResponse("graph.html", {"request": request, "device_id": device_id})


# --- 设备生命周期规则管理 API ---

@app.get("/api/lifecycle-rules")
async def get_lifecycle_rules(db: Session = Depends(get_db)):
    """
    获取所有生命周期规则
    """
    try:
        rules = db.query(LifecycleRule).all()
        return JSONResponse(content={
            "success": True,
            "data": [{
                "id": rule.id,
                "device_type": rule.device_type,
                "lifecycle_years": rule.lifecycle_years,
                "warning_months": rule.warning_months,
                "description": rule.description,
                "is_active": rule.is_active,
                "created_at": rule.created_at,
                "updated_at": rule.updated_at
            } for rule in rules]
        })
    except Exception as e:
        print(f"获取生命周期规则失败: {e}")
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)


@app.post("/api/lifecycle-rules")
async def create_lifecycle_rule(
    device_type: str = Form(...),
    lifecycle_years: int = Form(...),
    warning_months: int = Form(6),
    description: str = Form(""),
    password: str = Form(...),  # 添加密码参数
    db: Session = Depends(get_db)
):
    """
    创建生命周期规则
    """
    try:
        # 验证管理员密码
        if not verify_admin_password(password):
            return JSONResponse(content={"success": False, "message": "密码错误"}, status_code=401)
        
        from datetime import datetime
        
        # 检查设备类型是否已存在规则
        existing_rule = db.query(LifecycleRule).filter(LifecycleRule.device_type == device_type).first()
        if existing_rule:
            return JSONResponse(content={
                "success": False, 
                "message": f"设备类型 '{device_type}' 的生命周期规则已存在"
            }, status_code=400)
        
        # 创建新规则
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_rule = LifecycleRule(
            device_type=device_type,
            lifecycle_years=lifecycle_years,
            warning_months=warning_months,
            description=description,
            is_active="true",
            created_at=current_time,
            updated_at=current_time
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        return JSONResponse(content={
            "success": True,
            "message": "生命周期规则创建成功",
            "data": {
                "id": new_rule.id,
                "device_type": new_rule.device_type,
                "lifecycle_years": new_rule.lifecycle_years,
                "warning_months": new_rule.warning_months
            }
        })
        
    except Exception as e:
        db.rollback()
        print(f"创建生命周期规则失败: {e}")
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)


@app.put("/api/lifecycle-rules/{rule_id}")
async def update_lifecycle_rule(
    rule_id: int,
    device_type: str = Form(...),
    lifecycle_years: int = Form(...),
    warning_months: int = Form(6),
    description: str = Form(""),
    is_active: str = Form("true"),
    password: str = Form(...),  # 添加密码参数
    db: Session = Depends(get_db)
):
    """
    更新生命周期规则
    """
    try:
        # 验证管理员密码
        if not verify_admin_password(password):
            return JSONResponse(content={"success": False, "message": "密码错误"}, status_code=401)
        
        from datetime import datetime
        
        rule = db.query(LifecycleRule).filter(LifecycleRule.id == rule_id).first()
        if not rule:
            return JSONResponse(content={"success": False, "message": "规则不存在"}, status_code=404)
        
        # 检查设备类型是否与其他规则冲突
        existing_rule = db.query(LifecycleRule).filter(
            LifecycleRule.device_type == device_type,
            LifecycleRule.id != rule_id
        ).first()
        if existing_rule:
            return JSONResponse(content={
                "success": False, 
                "message": f"设备类型 '{device_type}' 的生命周期规则已存在"
            }, status_code=400)
        
        # 更新规则
        rule.device_type = device_type
        rule.lifecycle_years = lifecycle_years
        rule.warning_months = warning_months
        rule.description = description
        rule.is_active = is_active
        rule.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        db.commit()
        
        return JSONResponse(content={
            "success": True,
            "message": "生命周期规则更新成功"
        })
        
    except Exception as e:
        db.rollback()
        print(f"更新生命周期规则失败: {e}")
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)


@app.delete("/api/lifecycle-rules/{rule_id}")
async def delete_lifecycle_rule(rule_id: int, password: str = Form(...), db: Session = Depends(get_db)):
    """
    删除生命周期规则
    """
    try:
        # 验证管理员密码
        if not verify_admin_password(password):
            return JSONResponse(content={"success": False, "message": "密码错误"}, status_code=401)
        
        rule = db.query(LifecycleRule).filter(LifecycleRule.id == rule_id).first()
        if not rule:
            return JSONResponse(content={"success": False, "message": "规则不存在"}, status_code=404)
        
        db.delete(rule)
        db.commit()
        
        return JSONResponse(content={
            "success": True,
            "message": "生命周期规则删除成功"
        })
        
    except Exception as e:
        db.rollback()
        print(f"删除生命周期规则失败: {e}")
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)


@app.get("/api/devices/lifecycle-status")
async def get_devices_lifecycle_status(
    status_filter: Optional[str] = None,  # normal, warning, expired, all
    db: Session = Depends(get_db)
):
    """
    获取设备生命周期状态
    status_filter: normal(正常), warning(临近超限), expired(已超期), all(全部)
    """
    try:
        from datetime import datetime, timedelta
        import re
        
        # 获取所有设备和规则
        devices = db.query(Device).all()
        rules = {rule.device_type: rule for rule in db.query(LifecycleRule).filter(LifecycleRule.is_active == "true").all()}
        
        result_devices = []
        current_date = datetime.now()
        
        for device in devices:
            # 查找对应的生命周期规则
            rule = rules.get(device.device_type)
            if not rule:
                # 没有规则的设备标记为未知状态
                device_info = {
                    "id": device.id,
                    "asset_id": device.asset_id,
                    "name": device.name,
                    "station": device.station,
                    "model": device.model,
                    "vendor": device.vendor,
                    "commission_date": device.commission_date,
                    "lifecycle_status": "unknown",
                    "lifecycle_status_text": "未配置规则",
                    "days_in_service": None,
                    "remaining_days": None,
                    "rule_years": None
                }
                if not status_filter or status_filter == "all":
                    result_devices.append(device_info)
                continue
            
            # 解析投产日期
            if not device.commission_date:
                device_info = {
                    "id": device.id,
                    "asset_id": device.asset_id,
                    "name": device.name,
                    "station": device.station,
                    "model": device.model,
                    "vendor": device.vendor,
                    "commission_date": device.commission_date,
                    "lifecycle_status": "unknown",
                    "lifecycle_status_text": "投产日期未填写",
                    "days_in_service": None,
                    "remaining_days": None,
                    "rule_years": rule.lifecycle_years
                }
                if not status_filter or status_filter == "all":
                    result_devices.append(device_info)
                continue
            
            # 尝试解析多种日期格式
            commission_date = None
            date_str = device.commission_date.strip()
            
            # 处理特殊格式：YYYYMM (如 202312)
            if re.match(r'^\d{6}$', date_str):
                try:
                    year = int(date_str[:4])
                    month = int(date_str[4:6])
                    commission_date = datetime(year, month, 1)
                except ValueError:
                    pass
            
            # 如果特殊格式解析失败，尝试标准格式
            if not commission_date:
                date_formats = [
                    "%Y-%m-%d",
                    "%Y/%m/%d", 
                    "%Y.%m.%d",
                    "%Y-%m",
                    "%Y/%m",
                    "%Y.%m",
                    "%Y"
                ]
                
                for fmt in date_formats:
                    try:
                        if fmt == "%Y":
                            # 只有年份的情况，默认为该年的1月1日
                            commission_date = datetime.strptime(device.commission_date, fmt).replace(month=1, day=1)
                        elif fmt in ["%Y-%m", "%Y/%m", "%Y.%m"]:
                            # 只有年月的情况，默认为该月的1日
                            commission_date = datetime.strptime(device.commission_date, fmt).replace(day=1)
                        else:
                            commission_date = datetime.strptime(device.commission_date, fmt)
                        break
                    except ValueError:
                        continue
            
            if not commission_date:
                device_info = {
                    "id": device.id,
                    "asset_id": device.asset_id,
                    "name": device.name,
                    "station": device.station,
                    "model": device.model,
                    "vendor": device.vendor,
                    "commission_date": device.commission_date,
                    "lifecycle_status": "unknown",
                    "lifecycle_status_text": "投产日期格式无法识别",
                    "days_in_service": None,
                    "remaining_days": None,
                    "rule_years": rule.lifecycle_years
                }
                if not status_filter or status_filter == "all":
                    result_devices.append(device_info)
                continue
            
            # 计算服役时间和剩余时间
            days_in_service = (current_date - commission_date).days
            lifecycle_days = rule.lifecycle_years * 365
            remaining_days = lifecycle_days - days_in_service
            warning_days = rule.warning_months * 30
            
            # 确定生命周期状态
            if remaining_days < 0:
                lifecycle_status = "expired"
                lifecycle_status_text = f"已超期 {abs(remaining_days)} 天"
            elif remaining_days <= warning_days:
                lifecycle_status = "warning"
                lifecycle_status_text = f"临近超限，剩余 {remaining_days} 天"
            else:
                lifecycle_status = "normal"
                lifecycle_status_text = f"正常，剩余 {remaining_days} 天"
            
            device_info = {
                "id": device.id,
                "asset_id": device.asset_id,
                "name": device.name,
                "station": device.station,
                "model": device.model,
                "vendor": device.vendor,
                "commission_date": device.commission_date,
                "lifecycle_status": lifecycle_status,
                "lifecycle_status_text": lifecycle_status_text,
                "days_in_service": days_in_service,
                "remaining_days": remaining_days,
                "rule_years": rule.lifecycle_years
            }
            
            # 根据筛选条件添加设备
            if not status_filter or status_filter == "all" or status_filter == lifecycle_status:
                result_devices.append(device_info)
        
        # 统计信息
        total_count = len(result_devices)
        normal_count = len([d for d in result_devices if d["lifecycle_status"] == "normal"])
        warning_count = len([d for d in result_devices if d["lifecycle_status"] == "warning"])
        expired_count = len([d for d in result_devices if d["lifecycle_status"] == "expired"])
        unknown_count = len([d for d in result_devices if d["lifecycle_status"] == "unknown"])
        
        return JSONResponse(content={
            "success": True,
            "data": result_devices,
            "statistics": {
                "total": total_count,
                "normal": normal_count,
                "warning": warning_count,
                "expired": expired_count,
                "unknown": unknown_count
            }
        })
        
    except Exception as e:
        print(f"获取设备生命周期状态失败: {e}")
        traceback.print_exc()
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)


@app.get("/test-route")
async def test_route():
    """
    测试路由
    """
    print("=== 测试路由被调用 ===")
    return {"message": "测试路由正常工作", "timestamp": "updated"}

@app.get("/debug-routes")
async def debug_routes():
    """
    调试路由 - 显示所有已注册的路由
    """
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'unknown')
            })
    return {"registered_routes": routes, "total_count": len(routes)}

@app.get("/debug-lifecycle")
async def debug_lifecycle():
    """
    调试生命周期路由
    """
    print("=== 调试生命周期路由被调用 ===")
    return {"message": "调试路由正常工作", "status": "ok"}

@app.post("/api/verify-password")
async def verify_password(request: Request):
    """
    验证管理员密码
    """
    try:
        data = await request.json()
        password = data.get("password", "")
        
        if verify_admin_password(password):
            return {"success": True, "message": "密码验证成功"}
        else:
            return {"success": False, "message": "密码错误"}
    except Exception as e:
        print(f"Error verifying password: {e}")
        return {"success": False, "message": "验证失败"}

@app.get("/lifecycle-management", response_class=HTMLResponse)
async def lifecycle_management_page(request: Request):
    """
    生命周期管理页面
    """
    print("=== 访问生命周期管理页面 ===")
    print(f"请求URL: {request.url}")
    print(f"请求方法: {request.method}")
    try:
        print("正在渲染模板...")
        response = templates.TemplateResponse("lifecycle_management.html", {"request": request})
        print("模板渲染成功")
        return response
    except Exception as e:
        print(f"生命周期管理页面错误: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))