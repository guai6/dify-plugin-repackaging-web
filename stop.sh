#!/bin/bash
# Dify插件重新打包工具Web版停止脚本

echo "🛑 停止 Dify插件重新打包工具Web版..."

# 停止所有服务
docker-compose down

echo "✅ 服务已停止"
echo ""
echo "💡 如需完全清理，可执行："
echo "   docker-compose down -v  # 删除数据卷"
echo "   docker system prune     # 清理未使用的镜像"