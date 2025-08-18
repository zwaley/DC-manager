import os
from fastapi import FastAPI, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import pandas as pd
from typing import List
from urllib.parse import quote
import io
import traceback # 导入 traceback 用于打印详细的错误堆栈

# 修正了导入，使用正确的函数名和模型
from models import SessionLocal, Device, Connection, create_db_and_tables

# --- FastAPI 应用设置 ---

app = FastAPI(
    title="动力资源资产管理系统",
    description="一个用于管理和可视化数据中心动力设备资产的Web应用。",
    version="1.0.0"
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
# 设置模板目录
templates = Jinja2Templates(directory="templates")

# --- 数据库会话管理 ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 应用启动事件 ---

@app.on_event("startup")
def on_startup():
    if not os.path.exists('./database'):
        os.makedirs('./database')
    create_db_and_tables()

# --- 路由和视图函数 ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    devices = db.query(Device).order_by(Device.id).all()
    upload_error = request.query_params.get("error")
    return templates.TemplateResponse("index.html", {"request": request, "devices": devices, "upload_error": upload_error})

@app.post("/upload")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    处理 Excel 文件上传。
    如果失败，则重定向回主页并附带详细错误信息。
    增加了详细的日志记录来跟踪处理过程。
    """
    print("\n--- 开始处理上传的Excel文件 ---")
    try:
        # 步骤 1: 清空旧数据
        print("步骤 1: 清空旧的设备和连接数据...")
        db.query(Connection).delete()
        db.query(Device).delete()
        db.commit()
        print("步骤 1: 完成。")

        contents = await file.read()
        buffer = io.BytesIO(contents)
        
        # 步骤 2: 读取Excel文件
        print("步骤 2: 使用 pandas 读取Excel文件...")
        df = pd.read_excel(buffer)
        df = df.where(pd.notna(df), None) # 将 NaN 替换为 None
        print(f"步骤 2: 完成。读取到 {len(df)} 行数据。")
        print(f"Excel 文件列名: {df.columns.tolist()}") # 打印列名以供调试

        devices_map = {}
        devices_created_count = 0

        # 步骤 3: 创建设备
        print("步骤 3: 开始第一遍处理 - 创建设备...")
        for index, row in df.iterrows():
            # 更新：使用 '设备名称' 作为列名
            device_name = row.get("设备名称")
            if isinstance(device_name, str):
                device_name = device_name.strip()

            if not device_name:
                print(f"  - 第 {index+2} 行：跳过，因为'设备名称'为空。")
                continue
            
            # 更新：使用Excel文件中的实际列名来获取设备属性
            device = Device(
                name=device_name,
                model=row.get("设备型号"),
                location=row.get("机房内空间位置"),
                power_rating=row.get("设备额定容量"),
                vendor=row.get("设备生产厂家"),
                commission_date=row.get("设备投产时间"),
                remark=row.get("备注")
            )
            db.add(device)
            devices_map[device.name] = device
            devices_created_count += 1
            print(f"  - 第 {index+2} 行：准备创建设备 \'{device_name}\'。")
        
        db.commit()
        print(f"步骤 3: 完成。共创建 {devices_created_count} 个设备。")

        connections_created_count = 0
        # 步骤 4: 创建连接
        print("步骤 4: 开始第二遍处理 - 创建连接...")
        for index, row in df.iterrows():
            # 更新：同样使用 '设备名称' 作为列名
            device_name = row.get("设备名称")
            if isinstance(device_name, str):
                device_name = device_name.strip()
            
            parent_name = row.get("上级设备")
            
            if device_name and parent_name and parent_name in devices_map:
                source_device = devices_map[parent_name]
                target_device = devices_map[device_name]
                
                connection = Connection(
                    source_device_id=source_device.id,
                    source_port=row.get("上级端口"),
                    target_device_id=target_device.id,
                    target_port=row.get("本端端口"),
                    cable_type=row.get("线缆类型")
                )
                db.add(connection)
                connections_created_count += 1
                print(f"  - 第 {index+2} 行：准备创建从 \'{parent_name}\' 到 \'{device_name}\' 的连接。")
        
        db.commit()
        print(f"步骤 4: 完成。共创建 {connections_created_count} 个连接。")
        print("--- Excel文件处理成功 ---")

    except Exception as e:
        db.rollback()
        error_message = f"处理Excel文件时出错: {e}"
        print(f"--- Excel文件处理失败 ---")
        print(f"错误: {error_message}")
        traceback.print_exc() # 打印完整的错误堆栈信息
        print("--------------------------")
        return RedirectResponse(url=f"/?error={quote(error_message)}", status_code=303)

    return RedirectResponse(url="/", status_code=303)

@app.post("/devices")
async def create_device(
    name: str = Form(...),
    model: str = Form(None),
    location: str = Form(None),
    power_rating: str = Form(None),
    db: Session = Depends(get_db)
):
    new_device = Device(
        name=name,
        model=model,
        location=location,
        power_rating=power_rating
    )
    db.add(new_device)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/graph_data/{device_id}")
async def get_graph_data(device_id: int, db: Session = Depends(get_db)):
    nodes = []
    edges = []
    processed_ids = set()

    queue = [db.query(Device).filter(Device.id == device_id).first()]
    
    if not queue[0]:
        raise HTTPException(status_code=404, detail="Device not found")

    visited_ids = {device_id}

    while queue:
        current_device = queue.pop(0)

        if current_device.id not in processed_ids:
            nodes.append({
                "id": current_device.id,
                "label": current_device.name,
                "title": f"""<b>名称:</b> {current_device.name}<br>
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