@echo off
chcp 65001 > nul
echo 🚀 启动 Dify插件重新打包工具Web版...
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

REM 创建必要的目录
echo 📁 创建必要的目录...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs

REM 构建和启动服务
echo 🏗️ 构建和启动服务...
docker-compose up --build -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak > nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose ps

REM 显示访问信息
echo.
echo ✅ 服务启动完成！
echo.
echo 🌐 Web界面访问地址：
echo    http://localhost:8080
echo.
echo 🔧 API文档地址：
echo    http://localhost:5000/docs
echo.
echo 📊 服务状态查看：
echo    docker-compose ps
echo.
echo 📋 查看日志：
echo    docker-compose logs -f
echo.
echo 🛑 停止服务：
echo    docker-compose down
echo.
pause