FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    git \
    bash \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置启动脚本权限
RUN chmod +x start.sh

# 创建必要的目录
RUN mkdir -p uploads outputs static

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["./start.sh"]