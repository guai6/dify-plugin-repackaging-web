# Dify插件重新打包工具 - Web版

一个现代化的Web界面工具，用于重新打包Dify插件，支持多种插件来源和平台目标。

## 📖 简介

这是Dify插件重新打包工具的Web界面版本，提供了友好的用户界面来替代命令行操作。通过现代化的Web界面，您可以轻松地从不同来源获取插件并重新打包为目标平台格式。

### 支持的插件来源

- **📁 Local模式**：上传本地插件文件

### 重要配置说明

> ⚠️ **使用前请确保Dify平台配置正确**

在Dify的 `.env` 配置文件中需要进行以下设置：

```bash
# 允许安装未审核的插件
FORCE_VERIFYING_SIGNATURE=false

# 允许安装大型插件包（500MB）
PLUGIN_MAX_PACKAGE_SIZE=524288000

# 允许上传大文件（500MB）
NGINX_CLIENT_MAX_BODY_SIZE=500M
```

## ✨ 主要功能

### 🎯 核心功能

| 功能模块 | 描述 | 特点 |
|---------|------|------|
| **多源支持** | Local处理模式 | 灵活的插件获取方式 |
| **实时监控** | WebSocket实时显示处理过程 | 透明的处理状态 |
| **任务管理** | 任务列表、进度跟踪、状态管理 | 完整的任务生命周期 |
| **文件管理** | 文件上传、下载、删除、预览 | 便捷的文件操作 |
| **系统监控** | 资源使用率、存储状态、健康检查 | 全面的系统状态 |

### 🚀 技术架构

**前端技术栈**
- Vue 3 + TypeScript + Element Plus
- Pinia 状态管理
- WebSocket 实时通信
- 响应式设计（支持桌面和移动端）

**后端技术栈**
- Python FastAPI
- SQLite 数据库
- 异步任务处理
- RESTful API + WebSocket

**部署方案**
- Docker 容器化
- Docker Compose 编排
- Nginx 反向代理
- 一键启动脚本

## 🛠️ 快速开始

### 🚀 一键启动

#### 方式一：docker启动（推荐）

```bash
# 1. 创建必要目录
mkdir -p uploads outputs

# 2. 启动服务
docker-compose up --build -d

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志（可选）
docker-compose logs -f
```

#### 方式二：使用启动脚本

**Linux/macOS**
```bash
# 1. 克隆项目
git clone <repository-url>
cd dify-plugin-repackaging-web

# 2. 启动服务
chmod +x start.sh
./start.sh

# 3. 验证服务
netstat -tulpn | grep :8080  # Web界面
netstat -tulpn | grep :5000  # API服务
```



## 🌐 访问地址

启动成功后，可通过以下地址访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| 🖥️ **Web界面** | http://localhost:8080 | 主要操作界面 |
| 📚 **API文档** | http://localhost:5000/docs | Swagger文档 |
| 🔌 **API接口** | http://localhost:5000/api/v1 | RESTful API |

## 📋 使用指南

### 🏪 Marketplace模式

从Dify官方市场下载插件并重新打包。

**操作步骤：**

### 📁 Local模式

上传本地插件文件并重新打包。

**操作步骤：**
1. 选择 "本地文件" 标签页
2. 上传文件：
   - 拖拽 .difypkg 文件到上传区域
   - 或点击选择文件按钮
3. 选择目标平台和包后缀（可选）
4. 点击 "上传并重新打包"

**支持格式：**
- 文件类型：`.difypkg`
- 文件大小：最大 500MB

### 📊 任务管理

系统提供完整的任务生命周期管理功能：

| 功能 | 描述 | 操作 |
|------|------|------|
| **任务列表** | 查看所有任务的状态和进度 | 实时更新任务状态 |
| **实时日志** | 查看任务处理的详细日志 | WebSocket实时推送 |
| **文件下载** | 任务完成后下载重新打包的文件 | 一键下载结果 |
| **任务取消** | 取消正在进行的任务 | 安全终止处理 |

**任务状态说明：**
- 🟡 **等待中**：任务已创建，等待处理
- 🔵 **进行中**：任务正在执行
- 🟢 **已完成**：任务成功完成
- 🔴 **失败**：任务执行失败
- ⚪ **已取消**：任务被用户取消

### 📁 文件管理

提供全面的文件管理功能：

| 功能模块 | 功能描述 |
|----------|----------|
| **文件列表** | 查看上传和输出的所有文件，支持搜索和筛选 |
| **批量操作** | 支持批量下载、删除和移动文件 |
| **存储监控** | 实时查看磁盘使用情况和剩余空间 |
| **自动清理** | 自动清理超过24小时的临时文件 |
| **文件预览** | 支持查看文件基本信息和元数据 |

## ⚙️ 配置说明

### 🔧 环境变量配置

可通过修改 `docker-compose.yml` 中的环境变量来配置系统行为：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DEBUG` | `false` | 调试模式开关 |
| `HOST` | `0.0.0.0` | 服务绑定地址 |
| `PORT` | `5000` | 后端服务端口 |
| `MAX_FILE_SIZE` | `524288000` | 最大文件大小（500MB） |
| `DEFAULT_GITHUB_API_URL` | `https://github.com` | Github API地址 |
| `DEFAULT_MARKETPLACE_API_URL` | `https://marketplace.dify.ai` | Marketplace API地址 |
| `DEFAULT_PIP_MIRROR_URL` | `https://mirrors.aliyun.com/pypi/simple` | Python包镜像源 |

**配置示例：**
```yaml
environment:
  - DEBUG=false
  - HOST=0.0.0.0
  - PORT=5000
  - MAX_FILE_SIZE=524288000
  - DEFAULT_GITHUB_API_URL=https://github.com
  - DEFAULT_MARKETPLACE_API_URL=https://marketplace.dify.ai
  - DEFAULT_PIP_MIRROR_URL=https://mirrors.aliyun.com/pypi/simple
```

### 🌐 Web界面配置

在Web界面的 "系统设置" 页面可以动态配置：

- **🐙 Github设置**
  - API地址配置
  - 访问令牌设置
  - 代理配置

- **🏪 Marketplace设置**
  - API地址配置
  - 认证信息
  - 超时设置

- **📦 包管理设置**
  - Pip镜像源
  - 下载超时
  - 重试次数

## 🗂️ 项目结构

```
dify-plugin-repackaging-web/
├── 📁 backend/                    # 🐍 Python后端服务
│   ├── 📁 app/
│   │   ├── 📁 api/               # 🔌 API路由和端点
│   │   ├── 📁 core/              # ⚙️ 核心配置和设置
│   │   ├── 📁 models/            # 📊 数据模型定义
│   │   ├── 📁 services/          # 🔧 业务逻辑服务
│   │   └── 📁 utils/             # 🛠️ 工具函数库
│   ├── 📄 requirements.txt       # 📦 Python依赖包
│   ├── 📄 Dockerfile            # 🐳 后端容器配置
│   └── 📄 run.py                # 🚀 应用启动入口
├── 📁 frontend/                   # 🌐 Vue.js前端应用
│   ├── 📁 src/
│   │   ├── 📁 api/              # 🔗 API客户端封装
│   │   ├── 📁 components/       # 🧩 可复用Vue组件
│   │   ├── 📁 stores/           # 🗃️ Pinia状态管理
│   │   ├── 📁 types/            # 📝 TypeScript类型定义
│   │   ├── 📁 utils/            # 🔧 前端工具函数
│   │   ├── 📁 views/            # 📄 页面级组件
│   │   └── 📁 router/           # 🛣️ 路由配置
│   ├── 📄 package.json          # 📦 Node.js依赖
│   ├── 📄 nginx.conf            # 🌐 Nginx服务器配置
│   ├── 📄 Dockerfile           # 🐳 前端容器配置
│   └── 📄 vite.config.ts       # ⚡ Vite构建配置
├── 📁 uploads/                    # 📤 用户上传文件存储
├── 📁 outputs/                    # 📥 处理结果文件存储
├── 📁 images/                     # 🖼️ 文档图片资源
├── 📄 docker-compose.yml         # 🐳 Docker编排配置
├── 📄 start.sh                   # 🐧 Linux/macOS启动脚本
├── 📄 start.bat                  # 🪟 Windows启动脚本
├── 📄 stop.sh                    # ⏹️ 服务停止脚本
└── 📄 WEB-README.md              # 📖 项目文档
```

### 📋 目录说明

| 目录/文件 | 用途 | 技术栈 |
|-----------|------|--------|
| `backend/` | 后端API服务 | Python + FastAPI |
| `frontend/` | 前端Web界面 | Vue 3 + TypeScript |
| `uploads/` | 用户上传的插件文件 | 文件存储 |
| `outputs/` | 重新打包后的文件 | 文件存储 |
| `images/` | 文档和界面图片 | 静态资源 |

## 🔧 开发指南

### 🐍 后端开发

**环境准备**
```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

**开发运行**
```bash
# 启动开发服务器（热重载）
python run.py

# 或使用uvicorn直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

### 🌐 前端开发

**环境准备**
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
# 或使用yarn
yarn install
```

**开发运行**
```bash
# 启动开发服务器（热重载）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 📚 API文档

启动后端服务后，可通过以下地址查看API文档：
- **Swagger UI**：http://localhost:5000/docs
- **ReDoc**：http://localhost:5000/redoc
- **OpenAPI JSON**：http://localhost:5000/openapi.json

### 🧪 测试

```bash
# 后端测试
cd backend
pytest tests/

# 前端测试
cd frontend
npm run test
```

## 📊 系统监控

Web界面提供了完整的系统监控功能：

### 📈 实时监控面板

| 监控项目 | 监控内容 | 更新频率 |
|----------|----------|----------|
| **系统资源** | CPU、内存、磁盘使用率 | 实时 |
| **存储状态** | 已用空间、剩余空间、文件统计 | 实时 |
| **任务状态** | 运行中任务、完成任务、失败任务 | 实时 |
| **服务健康** | API响应时间、WebSocket连接状态 | 实时 |

### 🔍 健康检查

系统会自动进行以下健康检查：

- ✅ **目录权限检查**：验证上传和输出目录的读写权限
- ✅ **磁盘空间检查**：监控可用磁盘空间，低于阈值时告警
- ✅ **服务可用性检查**：检查后端API和数据库连接状态
- ✅ **依赖服务检查**：验证外部API（Github、Marketplace）的可访问性

## 🛡️ 安全说明

### 🔒 文件安全

| 安全措施 | 实现方式 | 防护目标 |
|----------|----------|----------|
| **文件类型验证** | 只允许.difypkg格式 | 防止恶意文件上传 |
| **文件大小限制** | 最大500MB限制 | 防止资源耗尽攻击 |
| **路径安全检查** | 禁止路径遍历 | 防止目录遍历攻击 |
| **文件内容扫描** | 基础恶意代码检测 | 防止恶意插件 |
| **临时文件清理** | 自动清理机制 | 防止磁盘空间耗尽 |

### 🔐 系统安全

| 安全层面 | 安全措施 | 说明 |
|----------|----------|------|
| **容器隔离** | Docker容器化运行 | 进程和文件系统隔离 |
| **资源限制** | CPU和内存使用限制 | 防止资源耗尽 |
| **网络安全** | 内部网络通信 | 服务间安全通信 |
| **数据脱敏** | 错误信息脱敏 | 防止敏感信息泄露 |
| **访问控制** | 文件权限控制 | 最小权限原则 |

### 🔑 最佳实践

- 🚫 **不要在生产环境中启用DEBUG模式**
- 🔒 **定期更新Docker镜像和依赖包**
- 📊 **监控系统资源使用情况**
- 🗂️ **定期备份重要数据**
- 🌐 **使用HTTPS进行生产部署**

## 📝 故障排除

### 🚨 常见问题及解决方案

#### 1️⃣ 服务无法启动

**问题症状：**
- Docker容器启动失败
- 端口访问不通
- 服务异常退出

**排查步骤：**
```bash
# 1. 检查Docker服务状态
sudo systemctl status docker

# 2. 检查端口占用情况
netstat -tulpn | grep :8080  # Web界面端口
netstat -tulpn | grep :5000  # API服务端口

# 3. 查看容器状态
docker-compose ps

# 4. 查看详细日志
docker-compose logs --tail=50
```

#### 2️⃣ 文件上传失败

**可能原因及解决方案：**

| 问题 | 检查项 | 解决方案 |
|------|--------|----------|
| 文件格式错误 | 确认文件扩展名为.difypkg | 使用正确格式的插件文件 |
| 文件过大 | 检查文件大小是否超过500MB | 压缩文件或调整大小限制 |
| 磁盘空间不足 | 查看磁盘使用情况 | 清理磁盘空间 |
| 权限问题 | 检查uploads目录权限 | 修复目录权限 |

#### 3️⃣ 任务处理失败

**排查流程：**
1. 查看任务详情页面的错误信息
2. 检查网络连接是否正常
3. 验证Github/Marketplace地址可访问性
4. 查看后端服务日志

```bash
# 测试网络连通性
curl -I https://github.com
curl -I https://marketplace.dify.ai

# 查看任务处理日志
docker-compose logs backend | grep ERROR
```

#### 4️⃣ WebSocket连接失败

**常见原因：**
- 防火墙阻止WebSocket连接
- 代理服务器配置问题
- 浏览器兼容性问题

**解决方案：**
```bash
# 检查防火墙状态
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # CentOS

# 测试WebSocket连接
wscat ws://localhost:5000/ws
```

### 📋 日志管理

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 实时跟踪日志
docker-compose logs -f

# 查看最近的日志
docker-compose logs --tail=100

# 按时间过滤日志
docker-compose logs --since="2024-01-01T00:00:00"
```


## 📞 技术支持

如有问题，请通过以下方式联系：

B站：https://space.bilibili.com/11791508

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

---

**享受使用 Dify插件重新打包工具Web版！** 🎉
