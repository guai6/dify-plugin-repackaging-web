from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.models.task import Task
from pydantic import BaseModel

router = APIRouter()

class FileInfo(BaseModel):
    """文件信息模型"""
    name: str
    path: str
    size: int
    type: str  # input, output, temp
    created_at: datetime
    task_id: Optional[str] = None

class StorageInfo(BaseModel):
    """存储信息模型"""
    total_space: int
    used_space: int
    free_space: int
    upload_count: int
    output_count: int

@router.get("", response_model=List[FileInfo])
@router.get("/", response_model=List[FileInfo])
async def list_files(
    file_type: str = "all",  # all, input, output, temp
    db: AsyncSession = Depends(get_db)
):
    """获取文件列表"""
    try:
        files = []
        
        # 获取上传文件
        if file_type in ["all", "input"]:
            if os.path.exists(settings.UPLOAD_DIR):
                for filename in os.listdir(settings.UPLOAD_DIR):
                    file_path = os.path.join(settings.UPLOAD_DIR, filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        files.append(FileInfo(
                            name=filename,
                            path=file_path,
                            size=stat.st_size,
                            type="input",
                            created_at=datetime.fromtimestamp(stat.st_ctime)
                        ))
        
        # 获取输出文件
        if file_type in ["all", "output"]:
            if os.path.exists(settings.OUTPUT_DIR):
                for filename in os.listdir(settings.OUTPUT_DIR):
                    file_path = os.path.join(settings.OUTPUT_DIR, filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        
                        # 查找关联的任务
                        result = await db.execute(
                            select(Task).where(Task.output_file_path == file_path)
                        )
                        task = result.scalar_one_or_none()
                        
                        files.append(FileInfo(
                            name=filename,
                            path=file_path,
                            size=stat.st_size,
                            type="output",
                            created_at=datetime.fromtimestamp(stat.st_ctime),
                            task_id=task.task_id if task else None
                        ))
        
        # 按创建时间排序
        files.sort(key=lambda x: x.created_at, reverse=True)
        return files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/storage", response_model=StorageInfo)
async def get_storage_info():
    """获取存储空间信息"""
    try:
        # 计算磁盘使用情况
        statvfs = shutil.disk_usage(settings.UPLOAD_DIR)
        total_space = statvfs.total
        free_space = statvfs.free
        used_space = total_space - free_space
        
        # 统计文件数量
        upload_count = 0
        output_count = 0
        
        if os.path.exists(settings.UPLOAD_DIR):
            upload_count = len([f for f in os.listdir(settings.UPLOAD_DIR) 
                              if os.path.isfile(os.path.join(settings.UPLOAD_DIR, f))])
        
        if os.path.exists(settings.OUTPUT_DIR):
            output_count = len([f for f in os.listdir(settings.OUTPUT_DIR) 
                              if os.path.isfile(os.path.join(settings.OUTPUT_DIR, f))])
        
        return StorageInfo(
            total_space=total_space,
            used_space=used_space,
            free_space=free_space,
            upload_count=upload_count,
            output_count=output_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_type}/{filename}")
async def download_file(file_type: str, filename: str):
    """下载文件"""
    try:
        if file_type == "input":
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
        elif file_type == "output":
            file_path = os.path.join(settings.OUTPUT_DIR, filename)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_type}/{filename}")
async def delete_file(file_type: str, filename: str):
    """删除文件"""
    try:
        if file_type == "input":
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
        elif file_type == "output":
            file_path = os.path.join(settings.OUTPUT_DIR, filename)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        os.remove(file_path)
        return {"message": "文件删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/{file_type}/{filename}")
async def get_file_content(file_type: str, filename: str):
    """获取文件内容（用于文本文件预览）"""
    try:
        if file_type == "input":
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
        elif file_type == "output":
            file_path = os.path.join(settings.OUTPUT_DIR, filename)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 检查文件大小（限制在1MB）
        file_size = os.path.getsize(file_path)
        if file_size > 1024 * 1024:  # 1MB
            raise HTTPException(status_code=413, detail="文件过大，不支持预览")
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果是UTF-8解码失败，尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="文件编码不支持或非文本文件")
        
        return Response(content=content, media_type="text/plain; charset=utf-8")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_temp_files():
    """清理临时文件"""
    try:
        cleanup_count = 0
        
        # 清理上传目录中的临时文件（超过24小时的文件）
        if os.path.exists(settings.UPLOAD_DIR):
            current_time = datetime.now().timestamp()
            for filename in os.listdir(settings.UPLOAD_DIR):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    file_time = os.path.getctime(file_path)
                    if current_time - file_time > 24 * 3600:  # 24小时
                        os.remove(file_path)
                        cleanup_count += 1
        
        return {"message": f"清理完成，删除了 {cleanup_count} 个临时文件"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))