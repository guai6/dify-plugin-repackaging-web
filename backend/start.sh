#!/bin/bash

echo "🚀 启动Dify插件重新打包工具后端服务..."

# 设置shell脚本执行权限（如果存在）
if [ -f "/app/plugin_repackaging.sh" ]; then
    echo "📄 设置plugin_repackaging.sh执行权限..."
    chmod +x /app/plugin_repackaging.sh
    echo "✅ 权限设置完成"
else
    echo "⚠️  plugin_repackaging.sh不存在，跳过权限设置"
fi

# 创建必要的目录
mkdir -p /app/uploads /app/outputs

# 启动FastAPI应用
echo "🌐 启动FastAPI服务..."
exec uvicorn app.main:app --host 0.0.0.0 --port 5000