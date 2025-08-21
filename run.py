#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 用于启动FastAPI应用
"""

import uvicorn
from config import PORT

if __name__ == "__main__":
    print(f"启动服务器在端口 {PORT}...")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)