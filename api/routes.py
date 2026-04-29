"""
API路由定义
简单的API路由模块，可与FastAPI配合使用
"""

from typing import Dict, Any, List
from pydantic import BaseModel

class WorkflowRequest(BaseModel):
    """工作流请求模型"""
    platform: str = "抖音"
    use_llm: bool = False
    llm_provider: str = "mock"

class SingleAgentRequest(BaseModel):
    """单Agent请求模型"""
    agent_name: str
    platform: str = "抖音"
    inputs: Dict[str, Any] = {}

class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str
    status: str
    result: Dict[str, Any] = {}
    error: str = ""
