#!/bin/bash
# Dify插件重新打包工具Web版启动脚本

echo "🚀 启动 Dify插件重新打包工具Web版..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查本地Python版本（可选）
echo "🐍 检查本地Python版本..."
if command -v python3 &> /dev/null; then
    LOCAL_PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "   本地Python版本: $LOCAL_PYTHON_VERSION"
    
    # 检查是否为3.12+
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
        echo "   ✅ 本地Python版本符合要求 (3.12+)"
    else
        echo "   ⚠️  本地Python版本较低，但Docker容器内将使用Python 3.12"
    fi
else
    echo "   ⚠️  未找到本地Python，但Docker容器内将使用Python 3.12"
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p uploads outputs

# 设置权限
echo "🔧 设置文件权限..."
chmod +x plugin_repackaging.sh
chmod +x dify-plugin-*
chmod +x check_python_version.sh

# 构建和启动服务
echo "🏗️ 构建和启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查Docker容器内的Python版本
echo "🐳 检查Docker容器内Python版本..."
DOCKER_PYTHON_VERSION=$(docker-compose exec -T backend python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null | tr -d '\r')

if [ $? -eq 0 ] && [ ! -z "$DOCKER_PYTHON_VERSION" ]; then
    echo "   Docker容器Python版本: $DOCKER_PYTHON_VERSION"
    
    # 检查是否为3.12+
    if docker-compose exec -T backend python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
        echo "   ✅ Docker容器Python版本符合要求 (3.12+)"
    else
        echo "   ❌ Docker容器Python版本过低！需要3.12或更高版本"
        echo "   💡 请检查backend/Dockerfile中的基础镜像"
        echo "   🛑 建议停止服务并更新Dockerfile"
    fi
else
    echo "   ⚠️  无法获取Docker容器Python版本，服务可能未正常启动"
fi

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "✅ 服务启动完成！"
echo ""
echo "🌐 Web界面访问地址："
echo "   http://localhost:8080"
echo ""
echo "🔧 API文档地址："
echo "   http://localhost:5000/docs"
echo ""
echo "📊 服务状态查看："
echo "   docker-compose ps"
echo ""
echo "📋 查看日志："
echo "   docker-compose logs -f"
echo ""
echo "🐍 检查Python版本："
echo "   ./check_python_version.sh  (完整检查工具)"
echo "   docker-compose exec backend python3 --version  (快速检查)"
echo ""
echo "🧪 测试修复效果："
echo "   python3 test_fixes.py  (测试文件名、任务名称、日志等修复)"
echo ""
echo "🛑 停止服务："
echo "   docker-compose down"
echo ""