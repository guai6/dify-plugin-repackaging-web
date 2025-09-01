from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import psutil
import platform
import os
import subprocess
from datetime import datetime

from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()

class SystemStatus(BaseModel):
    """系统状态模型"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    system_info: Dict[str, str]
    app_info: Dict[str, str]
    timestamp: datetime

class ApiConfig(BaseModel):
    """API配置模型"""
    github_api_url: str
    marketplace_api_url: str
    pip_mirror_url: str

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """获取系统状态"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 磁盘使用率
        disk = psutil.disk_usage(settings.UPLOAD_DIR)
        disk_percent = (disk.used / disk.total) * 100
        
        # 系统信息
        system_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
        
        # 应用信息
        app_info = {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "debug": str(settings.DEBUG),
            "upload_dir": settings.UPLOAD_DIR,
            "output_dir": settings.OUTPUT_DIR,
            "max_file_size": f"{settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        }
        
        return SystemStatus(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            system_info=system_info,
            app_info=app_info,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config", response_model=ApiConfig)
async def get_api_config():
    """获取API配置"""
    return ApiConfig(
        github_api_url=settings.DEFAULT_GITHUB_API_URL,
        marketplace_api_url=settings.DEFAULT_MARKETPLACE_API_URL,
        pip_mirror_url=settings.DEFAULT_PIP_MIRROR_URL
    )

@router.put("/config")
async def update_api_config(config: ApiConfig):
    """更新API配置"""
    try:
        # 这里可以实现配置更新逻辑
        # 暂时返回成功信息
        return {"message": "配置更新成功", "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查目录是否存在且可写
        upload_dir_ok = os.path.exists(settings.UPLOAD_DIR) and os.access(settings.UPLOAD_DIR, os.W_OK)
        output_dir_ok = os.path.exists(settings.OUTPUT_DIR) and os.access(settings.OUTPUT_DIR, os.W_OK)
        
        # 检查系统资源
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(settings.UPLOAD_DIR)
        
        low_memory = memory.percent > 90
        low_disk = (disk.used / disk.total) * 100 > 90
        
        status = "healthy"
        issues = []
        
        if not upload_dir_ok:
            issues.append("上传目录不可访问")
            status = "warning"
        
        if not output_dir_ok:
            issues.append("输出目录不可访问")
            status = "warning"
        
        if low_memory:
            issues.append("内存使用率过高")
            status = "warning"
        
        if low_disk:
            issues.append("磁盘空间不足")
            status = "warning"
        
        return {
            "status": status,
            "timestamp": datetime.now(),
            "checks": {
                "upload_dir": upload_dir_ok,
                "output_dir": output_dir_ok,
                "memory_ok": not low_memory,
                "disk_ok": not low_disk
            },
            "issues": issues
        }
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now(),
            "error": str(e)
        }

@router.get("/version")
async def get_version():
    """获取版本信息"""
    try:
        # 尝试获取Git信息
        git_info = {}
        try:
            git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
            git_info["commit"] = git_hash[:8]
        except:
            git_info["commit"] = "unknown"
        
        try:
            git_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
            git_info["branch"] = git_branch
        except:
            git_info["branch"] = "unknown"
        
        return {
            "app_name": settings.APP_NAME,
            "version": settings.VERSION,
            "build_time": datetime.now().isoformat(),
            "git": git_info,
            "python_version": platform.python_version(),
            "platform": platform.system()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))