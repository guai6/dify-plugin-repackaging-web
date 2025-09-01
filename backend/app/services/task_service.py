import asyncio
import uuid
import json
import os
import subprocess
import shutil
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.task import Task, TaskCreate, TaskStatus, TaskProgress
from app.core.config import settings
from app.services.websocket_service import WebSocketManager

class TaskService:
    """任务服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task(self, task_data: TaskCreate) -> Task:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        
        # 生成任务名称
        task_name = self._generate_task_name(task_data.mode.value, task_data.parameters)
        
        # 创建任务记录
        task = Task(
            task_id=task_id,
            task_name=task_name,
            mode=task_data.mode.value,
            parameters=json.dumps(task_data.parameters, ensure_ascii=False),
            status=TaskStatus.PENDING,
            progress=0.0,
            total_steps=5
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    def _generate_task_name(self, mode: str, parameters: Dict[str, Any]) -> str:
        """根据模式和参数生成任务名称"""
        timestamp = datetime.now().strftime("%H%M%S")
        
        try:
            if mode == "local":
                # Local模式：优先使用原始文件名（文件名已包含时间戳）
                original_filename = parameters.get("original_filename")
                if original_filename:
                    # 移除文件扩展名，不需要再加时间戳
                    name_without_ext = original_filename.replace('.difypkg', '')
                    return name_without_ext
                else:
                    # 后备方案：使用存储的文件名（也已包含时间戳）
                    file_name = parameters.get("file_name", "unknown.difypkg")
                    name_without_ext = file_name.replace('.difypkg', '')
                    return name_without_ext
                
            elif mode == "market":
                # Market模式：author/name@version
                author = parameters.get("author", "unknown")
                name = parameters.get("name", "unknown")
                version = parameters.get("version", "unknown")
                return f"{author}/{name}@{version}_{timestamp}"
                
            elif mode == "github":
                # Github模式：repo@release
                repo = parameters.get("repo", "unknown/unknown")
                release = parameters.get("release", "unknown")
                return f"{repo}@{release}_{timestamp}"
                
            else:
                return f"{mode}_task_{timestamp}"
                
        except Exception as e:
            # 如果生成名称时出错，返回默认名称
            return f"{mode}_task_{timestamp}"
    
    async def start_task(self, task_id: str, websocket_manager: WebSocketManager):
        """启动任务处理"""
        # 在后台异步执行任务
        asyncio.create_task(self._process_task(task_id, websocket_manager))
    
    async def _process_task(self, task_id: str, websocket_manager: WebSocketManager):
        """处理任务的核心逻辑"""
        print(f"[DEBUG] 开始处理任务: {task_id}")
        
        # 创建新的数据库会话
        from app.core.database import async_session_maker
        
        async with async_session_maker() as db:
            try:
                print(f"[DEBUG] 查询任务信息: {task_id}")
                # 获取任务信息
                result = await db.execute(select(Task).where(Task.task_id == task_id))
                task = result.scalar_one_or_none()
                
                if not task:
                    print(f"[DEBUG] 任务不存在: {task_id}")
                    return
                
                print(f"[DEBUG] 任务模式: {task.mode}, 参数: {task.parameters}")
                
                # 更新任务状态为开始
                print(f"[DEBUG] 更新任务状态为开始: {task_id}")
                await self._update_task_status_with_db(
                    db, task_id, TaskStatus.DOWNLOADING, 0.1, "开始处理任务...",
                    websocket_manager
                )
                
                # 解析参数
                parameters = json.loads(task.parameters) if task.parameters else {}
                
                if task.mode == "market":
                    print(f"[DEBUG] 处理Market任务: {task_id}")
                    await self._process_market_task_with_db(db, task_id, parameters, websocket_manager)
                elif task.mode == "github":
                    print(f"[DEBUG] 处理Github任务: {task_id}")
                    await self._process_github_task_with_db(db, task_id, parameters, websocket_manager)
                elif task.mode == "local":
                    print(f"[DEBUG] 处理Local任务: {task_id}")
                    await self._process_local_task_with_db(db, task_id, parameters, websocket_manager)
                
                print(f"[DEBUG] 任务处理完成: {task_id}")
                
            except Exception as e:
                print(f"[DEBUG] 任务处理异常: {task_id}, 错误: {str(e)}")
                await self._update_task_status_with_db(
                    db, task_id, TaskStatus.FAILED, 0.0, f"任务失败: {str(e)}",
                    websocket_manager, error_message=str(e)
                )
    
    async def _process_market_task_with_db(self, db: AsyncSession, task_id: str, params: Dict[str, Any], websocket_manager: WebSocketManager):
        """处理Market模式任务（带数据库会话）"""
        try:
            author = params.get("author")
            name = params.get("name")
            version = params.get("version")
            platform = params.get("platform", "")
            suffix = params.get("suffix", "offline")
            
            # 构建shell命令参数
            cmd_args = ["bash", "plugin_repackaging.sh"]
            if platform:
                cmd_args.extend(["-p", platform])
            if suffix != "offline":
                cmd_args.extend(["-s", suffix])
            cmd_args.extend(["market", author, name, version])
            
            await self._execute_shell_command_with_db(db, task_id, cmd_args, websocket_manager)
            
        except Exception as e:
            raise Exception(f"Market任务处理失败: {str(e)}")
    
    async def _process_github_task_with_db(self, db: AsyncSession, task_id: str, params: Dict[str, Any], websocket_manager: WebSocketManager):
        """处理Github模式任务（带数据库会话）"""
        try:
            repo = params.get("repo")
            release = params.get("release")
            asset_name = params.get("asset_name")
            platform = params.get("platform", "")
            suffix = params.get("suffix", "offline")
            
            # 构建shell命令参数
            cmd_args = ["bash", "plugin_repackaging.sh"]
            if platform:
                cmd_args.extend(["-p", platform])
            if suffix != "offline":
                cmd_args.extend(["-s", suffix])
            cmd_args.extend(["github", repo, release, asset_name])
            
            await self._execute_shell_command_with_db(db, task_id, cmd_args, websocket_manager)
            
        except Exception as e:
            raise Exception(f"Github任务处理失败: {str(e)}")
    
    async def _process_local_task_with_db(self, db: AsyncSession, task_id: str, params: Dict[str, Any], websocket_manager: WebSocketManager):
        """处理Local模式任务（带数据库会话）"""
        try:
            file_name = params.get("file_name")
            platform = params.get("platform", "")
            suffix = params.get("suffix", "offline")
            
            # 文件路径
            file_path = os.path.join(settings.UPLOAD_DIR, file_name)
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            # 构建shell命令参数
            cmd_args = ["bash", "plugin_repackaging.sh"]
            if platform:
                cmd_args.extend(["-p", platform])
            if suffix != "offline":
                cmd_args.extend(["-s", suffix])
            cmd_args.extend(["local", file_path])
            
            await self._execute_shell_command_with_db(db, task_id, cmd_args, websocket_manager)
            
        except Exception as e:
            raise Exception(f"Local任务处理失败: {str(e)}")
    
    async def _execute_shell_command_with_db(self, db: AsyncSession, task_id: str, cmd_args: list, websocket_manager: WebSocketManager):
        """执行shell命令（带数据库会话）"""
        try:
            # 添加环境调试信息
            import sys
            print(f"[DEBUG] Python版本: {sys.version}")
            print(f"[DEBUG] 任务ID: {task_id}")
            
            await self._update_task_status_with_db(
                db, task_id, TaskStatus.DOWNLOADING, 0.2, "开始下载插件...",
                websocket_manager
            )
            
            # 切换到项目根目录
            cwd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            print(f"[DEBUG] 工作目录: {cwd}")
            print(f"[DEBUG] 执行命令: {' '.join(cmd_args)}")
            
            # 执行命令（不使用text参数，手动处理编码）
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            log_content = ""
            
            # 实时读取输出
            while True:
                line_bytes = await process.stdout.readline()
                if not line_bytes:
                    break
                
                # 手动解码字节为字符串
                try:
                    line = line_bytes.decode('utf-8').strip()
                except UnicodeDecodeError:
                    line = line_bytes.decode('utf-8', errors='ignore').strip()
                
                if line:
                    log_content += line + "\n"
                    print(f"[SHELL OUTPUT] {line}")  # 调试：显示脚本输出
                    
                    # 发送实时日志到WebSocket
                    await websocket_manager.send_log(task_id, line)
                    
                    # 根据输出判断进度并更新状态
                    if "downloading" in line.lower() or "download" in line.lower():
                        await self._update_task_status_with_db(
                            db, task_id, TaskStatus.DOWNLOADING, 0.3, f"下载中: {line}",
                            websocket_manager
                        )
                    elif "unziping" in line.lower() or "unzip" in line.lower() or "extract" in line.lower():
                        await self._update_task_status_with_db(
                            db, task_id, TaskStatus.EXTRACTING, 0.5, f"解压中: {line}",
                            websocket_manager
                        )
                    elif "repackaging" in line.lower() or "package" in line.lower() or "building" in line.lower():
                        await self._update_task_status_with_db(
                            db, task_id, TaskStatus.PACKAGING, 0.7, f"重新打包中: {line}",
                            websocket_manager
                        )
                    elif "success" in line.lower() or "complete" in line.lower():
                        await self._update_task_status_with_db(
                            db, task_id, TaskStatus.PACKAGING, 0.9, f"处理中: {line}",
                            websocket_manager
                        )
                    elif "error" in line.lower() or "failed" in line.lower():
                        await self._update_task_status_with_db(
                            db, task_id, TaskStatus.FAILED, 0.0, f"错误: {line}",
                            websocket_manager, error_message=line
                        )
                        break
            
            # 等待进程完成
            await process.wait()
            
            if process.returncode == 0:
                # 查找输出文件
                output_file = await self._find_output_file(cwd)
                if output_file:
                    # 移动文件到输出目录
                    output_filename = os.path.basename(output_file)
                    final_output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
                    shutil.move(output_file, final_output_path)
                    
                    # 更新任务记录
                    await self._update_task_file_path_with_db(db, task_id, final_output_path)
                
                await self._update_task_status_with_db(
                    db, task_id, TaskStatus.COMPLETED, 1.0, "任务完成",
                    websocket_manager, log_content=log_content
                )
            else:
                raise Exception(f"命令执行失败，返回码: {process.returncode}")
                
        except Exception as e:
            await self._update_task_status_with_db(
                db, task_id, TaskStatus.FAILED, 0.0, f"执行失败: {str(e)}",
                websocket_manager, error_message=str(e)
            )
    
    async def _find_output_file(self, base_dir: str) -> Optional[str]:
        """查找输出文件"""
        try:
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('-offline.difypkg') or file.endswith('.difypkg'):
                        # 排除原始输入文件
                        file_path = os.path.join(root, file)
                        if 'uploads' not in file_path:
                            return file_path
            return None
        except Exception:
            return None
    
    async def _update_task_status_with_db(
        self, 
        db: AsyncSession,
        task_id: str, 
        status: TaskStatus, 
        progress: float, 
        current_step: str,
        websocket_manager: WebSocketManager,
        error_message: str = None,
        log_content: str = None
    ):
        """使用指定数据库会话更新任务状态"""
        try:
            # 构建更新数据 - 使用字符串键而不是 Column 对象
            update_data = {
                "status": status.value,
                "progress": progress,
                "current_step": current_step
            }
            
            if status == TaskStatus.DOWNLOADING and not hasattr(self, f"started_{task_id}"):
                update_data["started_at"] = datetime.now()
                setattr(self, f"started_{task_id}", True)
            
            if status == TaskStatus.COMPLETED:
                update_data["completed_at"] = datetime.now()
            
            if error_message:
                update_data["error_message"] = error_message
            
            if log_content:
                update_data["log_content"] = log_content
            
            # 更新数据库
            await db.execute(
                update(Task).where(Task.task_id == task_id).values(**update_data)
            )
            await db.commit()
            
            # 发送WebSocket消息
            progress_data = TaskProgress(
                task_id=task_id,
                status=status.value,
                progress=progress,
                current_step=current_step,
                message=error_message or current_step,
                timestamp=datetime.now()
            )
            
            await websocket_manager.send_progress(task_id, progress_data)
            
        except Exception as e:
            print(f"更新任务状态失败: {e}")
    
    # 以下是保留的原始方法，用于HTTP请求中的数据库操作
    async def _process_market_task(self, task_id: str, params: Dict[str, Any], websocket_manager: WebSocketManager):
        """处理Market模式任务"""
        try:
            author = params.get("author")
            name = params.get("name")
            version = params.get("version")
            platform = params.get("platform", "")
            suffix = params.get("suffix", "offline")
            
            # 构建shell命令参数
            cmd_args = ["bash", "plugin_repackaging.sh"]
            if platform:
                cmd_args.extend(["-p", platform])
            if suffix != "offline":
                cmd_args.extend(["-s", suffix])
            cmd_args.extend(["market", author, name, version])
            
            await self._execute_shell_command(task_id, cmd_args, websocket_manager)
            
        except Exception as e:
            raise Exception(f"Market任务处理失败: {str(e)}")
    
    async def _process_github_task(self, task_id: str, params: Dict[str, Any], websocket_manager: WebSocketManager):
        """处理Github模式任务"""
        try:
            repo = params.get("repo")
            release = params.get("release")
            asset_name = params.get("asset_name")
            platform = params.get("platform", "")
            suffix = params.get("suffix", "offline")
            
            # 构建shell命令参数
            cmd_args = ["bash", "plugin_repackaging.sh"]
            if platform:
                cmd_args.extend(["-p", platform])
            if suffix != "offline":
                cmd_args.extend(["-s", suffix])
            cmd_args.extend(["github", repo, release, asset_name])
            
            await self._execute_shell_command(task_id, cmd_args, websocket_manager)
            
        except Exception as e:
            raise Exception(f"Github任务处理失败: {str(e)}")
    
    async def _process_local_task(self, task_id: str, params: Dict[str, Any], websocket_manager: WebSocketManager):
        """处理Local模式任务"""
        try:
            file_name = params.get("file_name")
            platform = params.get("platform", "")
            suffix = params.get("suffix", "offline")
            
            # 文件路径
            file_path = os.path.join(settings.UPLOAD_DIR, file_name)
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            # 构建shell命令参数
            cmd_args = ["bash", "plugin_repackaging.sh"]
            if platform:
                cmd_args.extend(["-p", platform])
            if suffix != "offline":
                cmd_args.extend(["-s", suffix])
            cmd_args.extend(["local", file_path])
            
            await self._execute_shell_command(task_id, cmd_args, websocket_manager)
            
        except Exception as e:
            raise Exception(f"Local任务处理失败: {str(e)}")
    
    async def _execute_shell_command(self, task_id: str, cmd_args: list, websocket_manager: WebSocketManager):
        """执行shell命令"""
        try:
            await self._update_task_status(
                task_id, TaskStatus.DOWNLOADING, 0.2, "开始下载插件...",
                websocket_manager
            )
            
            # 切换到项目根目录
            cwd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # 执行命令（不使用text参数，手动处理编码）
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            log_content = ""
            
            # 实时读取输出
            while True:
                line_bytes = await process.stdout.readline()
                if not line_bytes:
                    break
                
                # 手动解码字节为字符串
                try:
                    line = line_bytes.decode('utf-8').strip()
                except UnicodeDecodeError:
                    line = line_bytes.decode('utf-8', errors='ignore').strip()
                
                if line:
                    log_content += line + "\n"
                    print(f"[SHELL OUTPUT] {line}")  # 调试：显示脚本输出
                    
                    # 发送实时日志到WebSocket
                    await websocket_manager.send_log(task_id, line)
                    
                    # 根据输出判断进度并更新状态
                    if "downloading" in line.lower() or "download" in line.lower():
                        await self._update_task_status(
                            task_id, TaskStatus.DOWNLOADING, 0.3, f"下载中: {line}",
                            websocket_manager
                        )
                    elif "unziping" in line.lower() or "unzip" in line.lower() or "extract" in line.lower():
                        await self._update_task_status(
                            task_id, TaskStatus.EXTRACTING, 0.5, f"解压中: {line}",
                            websocket_manager
                        )
                    elif "repackaging" in line.lower() or "package" in line.lower() or "building" in line.lower():
                        await self._update_task_status(
                            task_id, TaskStatus.PACKAGING, 0.7, f"重新打包中: {line}",
                            websocket_manager
                        )
                    elif "success" in line.lower() or "complete" in line.lower():
                        await self._update_task_status(
                            task_id, TaskStatus.PACKAGING, 0.9, f"处理中: {line}",
                            websocket_manager
                        )
                    elif "error" in line.lower() or "failed" in line.lower():
                        await self._update_task_status(
                            task_id, TaskStatus.FAILED, 0.0, f"错误: {line}",
                            websocket_manager, error_message=line
                        )
                        break
            
            # 等待进程完成
            await process.wait()
            
            if process.returncode == 0:
                # 查找输出文件
                output_file = await self._find_output_file(cwd)
                if output_file:
                    # 移动文件到输出目录
                    output_filename = os.path.basename(output_file)
                    final_output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
                    shutil.move(output_file, final_output_path)
                    
                    # 更新任务记录
                    await self._update_task_file_path(task_id, final_output_path)
                
                await self._update_task_status(
                    task_id, TaskStatus.COMPLETED, 1.0, "任务完成",
                    websocket_manager, log_content=log_content
                )
            else:
                raise Exception(f"命令执行失败，返回码: {process.returncode}")
                
        except Exception as e:
            await self._update_task_status(
                task_id, TaskStatus.FAILED, 0.0, f"执行失败: {str(e)}",
                websocket_manager, error_message=str(e)
            )
    
    async def _update_task_status(
        self, 
        task_id: str, 
        status: TaskStatus, 
        progress: float, 
        current_step: str,
        websocket_manager: WebSocketManager,
        error_message: str = None,
        log_content: str = None
    ):
        """更新任务状态"""
        try:
            # 构建更新数据 - 使用字符串键而不是 Column 对象
            update_data = {
                "status": status.value,
                "progress": progress,
                "current_step": current_step
            }
            
            if status == TaskStatus.DOWNLOADING and not hasattr(self, f"started_{task_id}"):
                update_data["started_at"] = datetime.now()
                setattr(self, f"started_{task_id}", True)
            
            if status == TaskStatus.COMPLETED:
                update_data["completed_at"] = datetime.now()
            
            if error_message:
                update_data["error_message"] = error_message
            
            if log_content:
                update_data["log_content"] = log_content
            
            # 更新数据库
            await self.db.execute(
                update(Task).where(Task.task_id == task_id).values(**update_data)
            )
            await self.db.commit()
            
            # 发送WebSocket消息
            progress_data = TaskProgress(
                task_id=task_id,
                status=status.value,
                progress=progress,
                current_step=current_step,
                message=error_message or current_step,
                timestamp=datetime.now()
            )
            
            await websocket_manager.send_progress(task_id, progress_data)
            
        except Exception as e:
            print(f"更新任务状态失败: {e}")
    
    async def update_task_file_info(self, task_id: str, file_path: str, file_size: int):
        """更新任务文件信息"""
        await self.db.execute(
            update(Task).where(Task.task_id == task_id).values(
                input_file_path=file_path,
                file_size=file_size
            )
        )
        await self.db.commit()
    
    async def _update_task_file_path(self, task_id: str, output_path: str):
        """更新任务输出文件路径"""
        await self.db.execute(
            update(Task).where(Task.task_id == task_id).values(
                output_file_path=output_path
            )
        )
        await self.db.commit()
    
    async def _update_task_file_path_with_db(self, db: AsyncSession, task_id: str, output_path: str):
        """使用指定数据库会话更新任务输出文件路径"""
        await db.execute(
            update(Task).where(Task.task_id == task_id).values(
                output_file_path=output_path
            )
        )
        await db.commit()
    
    async def cancel_task(self, task_id: str):
        """取消任务"""
        await self.db.execute(
            update(Task).where(Task.task_id == task_id).values(
                status=TaskStatus.CANCELLED.value,
                completed_at=datetime.now()
            )
        )
        await self.db.commit()