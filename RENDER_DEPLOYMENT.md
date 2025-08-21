# 安吉电信动力设备管理系统 - Render平台部署指南

## 部署前准备

1. **Render账户**：确保您已经在[Render](https://render.com)上注册并登录账户

2. **代码仓库**：将项目代码推送到Git仓库（GitHub、GitLab或Bitbucket）
   ```bash
   git add .
   git commit -m "准备部署到Render"
   git push
   ```

## 部署步骤

### 方法一：使用render.yaml（推荐）

1. **连接Git仓库**
   - 登录Render平台
   - 点击右上角的"New +"
   - 选择"Blueprint"
   - 授权并选择包含项目的Git仓库
   - Render会自动检测项目中的`render.yaml`文件并据此创建服务

2. **确认配置**
   - 检查自动生成的服务配置
   - 根据需要调整环境变量或其他设置
   - 点击"Create New Blueprint"按钮开始部署

### 方法二：手动创建Web服务

1. **创建新服务**
   - 登录Render平台
   - 点击右上角的"New +"
   - 选择"Web Service"
   - 连接到您的Git仓库并选择项目

2. **配置服务**
   - 名称：`dc-asset-manager`（或您喜欢的名称）
   - 环境：`Python`
   - 区域：选择离您用户最近的区域
   - 分支：`main`（或您的部署分支）
   - 构建命令：`pip install -r requirements.txt`
   - 启动命令：`python run.py`

3. **环境变量**
   - 添加以下环境变量：
     - `PYTHON_VERSION`: 3.10.0
     - `PORT`: 10000
     - `RENDER`: true
     - `ADMIN_PASSWORD`: 设置您的管理员密码

4. **创建服务**
   - 点击"Create Web Service"按钮
   - Render将开始构建和部署您的应用

## 部署后操作

1. **验证部署**
   - 部署完成后，Render会提供一个URL（例如`https://dc-asset-manager.onrender.com`）
   - 访问该URL确认应用是否正常运行

2. **查看日志**
   - 在Render控制台中点击您的服务
   - 选择"Logs"选项卡查看运行日志
   - 如有错误，可以根据日志信息进行排查

3. **配置自定义域名（可选）**
   - 在服务详情页面，找到"Custom Domains"部分
   - 点击"Add Custom Domain"并按照指引操作

4. **数据持久化**
   - 在服务配置中添加磁盘卷：
     - 名称：`database`
     - 挂载路径：`/app/database`
     - 大小：`1 GB`
   - 数据库文件将存储在持久化存储中，确保数据不会在部署间丢失

## 注意事项

1. **免费套餐限制**
   - Render的免费套餐有一定的资源限制
   - 服务在15分钟不活动后会自动休眠，下次访问时需要几秒钟启动时间

2. **数据备份**
   - 定期备份数据库文件是个好习惯
   - 可以通过Render的API或手动方式导出数据

3. **环境变量安全**
   - 敏感信息（如管理员密码）应通过环境变量配置，而不是硬编码在代码中
   - 在Render控制台中设置`ADMIN_PASSWORD`环境变量，替换代码中的默认值