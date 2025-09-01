from typing import Dict, List
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime

from app.models.task import TaskProgress

class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储每个任务的WebSocket连接
        self.connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str):
        """连接WebSocket"""
        await websocket.accept()
        
        if task_id not in self.connections:
            self.connections[task_id] = []
        
        self.connections[task_id].append(websocket)
        print(f"WebSocket connected for task {task_id}, total connections: {len(self.connections[task_id])}")
    
    def disconnect(self, websocket: WebSocket, task_id: str):
        """断开WebSocket连接"""
        if task_id in self.connections:
            if websocket in self.connections[task_id]:
                self.connections[task_id].remove(websocket)
            
            # 如果没有连接了，删除task_id
            if not self.connections[task_id]:
                del self.connections[task_id]
        
        print(f"WebSocket disconnected for task {task_id}")
    
    async def send_progress(self, task_id: str, progress: TaskProgress):
        """发送进度信息"""
        if task_id not in self.connections:
            return
        
        # 准备消息数据
        message = {
            "type": "progress",
            "data": {
                "task_id": progress.task_id,
                "status": progress.status,
                "progress": progress.progress,
                "current_step": progress.current_step,
                "message": progress.message,
                "timestamp": progress.timestamp.isoformat()
            }
        }
        
        message_text = json.dumps(message, ensure_ascii=False)
        
        # 发送给所有连接
        disconnected_connections = []
        
        for websocket in self.connections[task_id]:
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                print(f"Failed to send message to websocket: {e}")
                disconnected_connections.append(websocket)
        
        # 清理断开的连接
        for websocket in disconnected_connections:
            self.disconnect(websocket, task_id)
    
    async def send_log(self, task_id: str, log_line: str):
        """发送实时日志"""
        if task_id not in self.connections:
            return
        
        # 准备日志消息
        message = {
            "type": "log",
            "data": {
                "task_id": task_id,
                "log": log_line,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        message_text = json.dumps(message, ensure_ascii=False)
        
        # 发送给所有连接
        disconnected_connections = []
        
        for websocket in self.connections[task_id]:
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                print(f"Failed to send log to websocket: {e}")
                disconnected_connections.append(websocket)
        
        # 清理断开的连接
        for websocket in disconnected_connections:
            self.disconnect(websocket, task_id)
    
    async def send_message(self, task_id: str, message_type: str, data: dict):
        """发送自定义消息"""
        if task_id not in self.connections:
            return
        
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        message_text = json.dumps(message, ensure_ascii=False)
        
        disconnected_connections = []
        
        for websocket in self.connections[task_id]:
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                print(f"Failed to send custom message to websocket: {e}")
                disconnected_connections.append(websocket)
        
        # 清理断开的连接
        for websocket in disconnected_connections:
            self.disconnect(websocket, task_id)
    
    def get_connection_count(self, task_id: str) -> int:
        """获取指定任务的连接数"""
        return len(self.connections.get(task_id, []))
    
    def get_all_connections_count(self) -> int:
        """获取总连接数"""
        return sum(len(connections) for connections in self.connections.values())
    
    async def broadcast_system_message(self, message: str):
        """广播系统消息给所有连接"""
        system_message = {
            "type": "system",
            "data": {
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        message_text = json.dumps(system_message, ensure_ascii=False)
        
        for task_id, connections in self.connections.items():
            disconnected_connections = []
            
            for websocket in connections:
                try:
                    await websocket.send_text(message_text)
                except Exception as e:
                    print(f"Failed to broadcast system message: {e}")
                    disconnected_connections.append(websocket)
            
            # 清理断开的连接
            for websocket in disconnected_connections:
                self.disconnect(websocket, task_id)