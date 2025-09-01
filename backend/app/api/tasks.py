from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional, Dict, Any
import uuid
import json
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.models.task import Task, TaskCreate, TaskResponse, TaskProgress, TaskStatus, ProcessMode
from app.models.task import MarketParams, GithubParams, LocalParams
from app.services.task_service import TaskService
from app.services.websocket_service import WebSocketManager
from app.core.config import settings

router = APIRouter()

# WebSocket管理器
manager = WebSocketManager()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新任务"""
    try:
        task_service = TaskService(db)
        task = await task_service.create_task(task_data)
        
        # 启动异步任务处理
        await task_service.start_task(task.task_id, manager)
        
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/market", response_model=TaskResponse)
async def create_market_task(
    params: MarketParams,
    db: AsyncSession = Depends(get_db)
):
    """创建Market模式任务"""
    task_data = TaskCreate(
        mode=ProcessMode.MARKET,
        parameters=params.dict()
    )
    return await create_task(task_data, db)

@router.post("/github", response_model=TaskResponse)
async def create_github_task(
    params: GithubParams,
    db: AsyncSession = Depends(get_db)
):
    """创建Github模式任务"""
    task_data = TaskCreate(
        mode=ProcessMode.GITHUB,
        parameters=params.dict()
    )
    return await create_task(task_data, db)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    platform: Optional[str] = Form(None),
    suffix: Optional[str] = Form("offline"),
    db: AsyncSession = Depends(get_db)
):
    """上传文件并创建Local模式任务"""
    
    # 验证文件类型
    if not file.filename.endswith('.difypkg'):
        raise HTTPException(status_code=400, detail="只支持.difypkg文件")
    
    # 验证文件大小
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"文件大小超过限制({settings.MAX_FILE_SIZE / 1024 / 1024}MB)")
    
    try:
        # 生成基于原文件名的唯一文件名
        original_name = os.path.splitext(file.filename)[0]  # 原文件名（不含扩展名）
        file_extension = os.path.splitext(file.filename)[1]  # 文件扩展名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 时间戳
        saved_filename = f"{original_name}_{timestamp}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 创建任务
        params = LocalParams(
            file_name=saved_filename,
            original_filename=file.filename,
            platform=platform,
            suffix=suffix or "offline"
        )
        
        task_data = TaskCreate(
            mode=ProcessMode.LOCAL,
            parameters=params.dict()
        )
        
        task_service = TaskService(db)
        task = await task_service.create_task(task_data)
        
        # 更新任务的输入文件路径
        await task_service.update_task_file_info(task.task_id, file_path, file.size)
        
        # 启动异步任务处理
        await task_service.start_task(task.task_id, manager)
        
        return {
            "task_id": task.task_id,
            "filename": file.filename,
            "size": file.size,
            "status": "uploaded"
        }
        
    except Exception as e:
        # 清理已上传的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.get("", response_model=List[TaskResponse])
@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取任务列表"""
    try:
        query = select(Task).order_by(desc(Task.created_at))
        
        if status:
            query = query.where(Task.status == status)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        # 转换参数字段
        task_responses = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "task_id": task.task_id,
                "task_name": task.task_name,
                "mode": task.mode,
                "status": task.status,
                "progress": task.progress,
                "current_step": task.current_step,
                "total_steps": task.total_steps,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "input_file_path": task.input_file_path,
                "output_file_path": task.output_file_path,
                "file_size": task.file_size,
                "error_message": task.error_message
            }
            
            # 解析参数JSON
            if task.parameters:
                try:
                    task_dict["parameters"] = json.loads(task.parameters)
                except:
                    task_dict["parameters"] = {}
            else:
                task_dict["parameters"] = {}
            
            task_responses.append(TaskResponse(**task_dict))
        
        return task_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取单个任务详情"""
    try:
        result = await db.execute(select(Task).where(Task.task_id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 构建响应
        task_dict = {
            "id": task.id,
            "task_id": task.task_id,
            "task_name": task.task_name,
            "mode": task.mode,
            "status": task.status,
            "progress": task.progress,
            "current_step": task.current_step,
            "total_steps": task.total_steps,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "input_file_path": task.input_file_path,
            "output_file_path": task.output_file_path,
            "file_size": task.file_size,
            "error_message": task.error_message
        }
        
        # 解析参数JSON
        if task.parameters:
            try:
                task_dict["parameters"] = json.loads(task.parameters)
            except:
                task_dict["parameters"] = {}
        else:
            task_dict["parameters"] = {}
        
        return TaskResponse(**task_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """取消任务"""
    try:
        task_service = TaskService(db)
        await task_service.cancel_task(task_id)
        return {"message": "任务已取消"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{task_id}/download")
async def download_result(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """下载任务结果文件"""
    try:
        result = await db.execute(select(Task).where(Task.task_id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task.status != TaskStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="任务未完成")
        
        if not task.output_file_path or not os.path.exists(task.output_file_path):
            raise HTTPException(status_code=404, detail="结果文件不存在")
        
        return FileResponse(
            path=task.output_file_path,
            filename=os.path.basename(task.output_file_path),
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{task_id}")
async def websocket_task_progress(websocket: WebSocket, task_id: str):
    """WebSocket连接，实时推送任务进度"""
    await manager.connect(websocket, task_id)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)