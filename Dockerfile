# 使用官方 Python 镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件到工作目录
# 将这一步和下一步分开，可以利用Docker的缓存机制，
# 只有当 requirements.txt 文件改变时才会重新安装依赖。
COPY requirements.txt .

# 安装项目依赖
# 使用 --no-cache-dir 选项可以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码到工作目录
COPY . .

# 容器启动时执行的命令
# 启动 uvicorn 服务器，并监听所有网络接口的 8000 端口，以便可以从容器外部访问
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]