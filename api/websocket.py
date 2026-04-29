"""
WebSocket模块 - 支持实时推送和协作
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接
        self.active_connections: Dict[str, WebSocket] = {}
        # 房间管理（按workflow_id分组）
        self.rooms: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """建立连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        """断开连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # 从所有房间中移除
        for room in self.rooms.values():
            room.discard(client_id)
    
    def join_room(self, client_id: str, room_id: str):
        """加入房间"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(client_id)
    
    def leave_room(self, client_id: str, room_id: str):
        """离开房间"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(client_id)
    
    async def send_personal_message(self, message: dict, client_id: str):
        """发送个人消息"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict):
        """广播给所有连接"""
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except:
                disconnected.append(client_id)
        
        # 清理断开连接
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def broadcast_to_room(self, room_id: str, message: dict):
        """广播给房间内所有连接"""
        if room_id not in self.rooms:
            return
        
        disconnected = []
        for client_id in self.rooms[room_id]:
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json(message)
                except:
                    disconnected.append(client_id)
        
        # 清理断开连接
        for client_id in disconnected:
            self.disconnect(client_id)
            self.rooms[room_id].discard(client_id)

# 全局连接管理器
manager = ConnectionManager()

async def notify_workflow_progress(workflow_id: str, agent_name: str, 
                                   current_step: int, total_steps: int,
                                   status: str = "running"):
    """通知工作流进度"""
    await manager.broadcast_to_room(
        workflow_id,
        {
            "type": "workflow_progress",
            "workflow_id": workflow_id,
            "agent_name": agent_name,
            "current_step": current_step,
            "total_steps": total_steps,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    )

async def notify_agent_status(agent_name: str, status: str, message: str = ""):
    """通知Agent状态变化"""
    await manager.broadcast(
        {
            "type": "agent_status",
            "agent_name": agent_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    )

async def notify_analysis_complete(workflow_id: str, result_summary: dict):
    """通知分析完成"""
    await manager.broadcast_to_room(
        workflow_id,
        {
            "type": "analysis_complete",
            "workflow_id": workflow_id,
            "summary": result_summary,
            "timestamp": datetime.now().isoformat()
        }
    )
