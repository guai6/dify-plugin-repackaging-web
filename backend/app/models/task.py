from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    EXTRACTING = "extracting"
    PACKAGING = "packaging"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessMode(str, Enum):
    """处理模式枚举"""
    MARKET = "market"
    GITHUB = "github"
    LOCAL = "local"

class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(50), unique=True, index=True, nullable=False)
    task_name = Column(String(200), nullable=True)  # 任务显示名称
    mode = Column(String(20), nullable=False)  # market, github, local
    status = Column(String(20), default=TaskStatus.PENDING)
    
    # 任务参数（JSON字符串）
    parameters = Column(Text, nullable=True)
    
    # 文件信息
    input_file_path = Column(String(500), nullable=True)
    output_file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # 进度信息
    progress = Column(Float, default=0.0)
    current_step = Column(String(100), nullable=True)
    total_steps = Column(Integer, default=5)
    
    # 时间信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 结果信息
    error_message = Column(Text, nullable=True)
    log_content = Column(Text, nullable=True)

# Pydantic模型
class TaskCreate(BaseModel):
    """创建任务请求模型"""
    mode: ProcessMode
    parameters: Dict[str, Any]

class TaskResponse(BaseModel):
    """任务响应模型"""
    id: int
    task_id: str
    task_name: Optional[str] = None
    mode: str
    status: str
    parameters: Optional[Dict[str, Any]] = None
    progress: float
    current_step: Optional[str] = None
    total_steps: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input_file_path: Optional[str] = None
    output_file_path: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class TaskProgress(BaseModel):
    """任务进度模型"""
    task_id: str
    status: str
    progress: float
    current_step: str
    message: str
    timestamp: datetime

class MarketParams(BaseModel):
    """Market模式参数"""
    author: str
    name: str
    version: str
    platform: Optional[str] = None
    suffix: Optional[str] = "offline"

class GithubParams(BaseModel):
    """Github模式参数"""
    repo: str
    release: str
    asset_name: str
    platform: Optional[str] = None
    suffix: Optional[str] = "offline"

class LocalParams(BaseModel):
    """Local模式参数"""
    file_name: str
    original_filename: Optional[str] = None
    platform: Optional[str] = None
    suffix: Optional[str] = "offline"