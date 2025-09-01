from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "Dify插件重新打包工具"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:8080",
        # 生产环境IP地址
        "http://154.64.250.181:8080",
        "http://154.64.250.181:5000",
        "http://154.64.250.181"
    ]
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 文件存储配置
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs")
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    # API配置
    DEFAULT_GITHUB_API_URL: str = "https://github.com"
    DEFAULT_MARKETPLACE_API_URL: str = "https://marketplace.dify.ai"
    DEFAULT_PIP_MIRROR_URL: str = "https://mirrors.aliyun.com/pypi/simple"
    
    # 任务配置
    TASK_TIMEOUT: int = 1800  # 30分钟
    MAX_CONCURRENT_TASKS: int = 5
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()