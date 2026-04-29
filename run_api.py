#!/usr/bin/env python3
"""
电商全链路多Agent智能体系统 - API服务入口
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid
import json
from datetime import datetime

from config.settings import get_settings
from core.coordinator import EcommerceAgentCoordinator
from utils.llm_factory import LLMFactory

# 初始化
settings = get_settings()
app = FastAPI(
    title="电商全链路多Agent智能体API",
    description="基于多Agent协作的电商运营解决方案API",
    version="1.0.0"
)

# 存储运行中的任务
tasks = {}

# Pydantic模型
class WorkflowRequest(BaseModel):
    platform: str = Field(..., description="电商平台", example="抖音")
    use_llm: bool = Field(False, description="是否使用LLM")
    llm_provider: Optional[str] = Field("mock", description="LLM提供商")
    
class SingleAgentRequest(BaseModel):
    agent_name: str = Field(..., description="Agent名称", example="market")
    platform: Optional[str] = Field("抖音", description="电商平台")
    inputs: Optional[Dict[str, Any]] = Field(None, description="Agent输入参数")

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    created_at: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# 全局协调器实例
coordinator_instance = None

def get_coordinator(llm_provider: str = "mock"):
    """获取或创建协调器实例"""
    global coordinator_instance
    
    if coordinator_instance is None:
        llm = None
        if llm_provider != "mock":
            try:
                llm = LLMFactory.create_llm(provider=llm_provider)
            except Exception as e:
                print(f"LLM加载失败: {e}")
        
        coordinator_instance = EcommerceAgentCoordinator(llm=llm)
    
    return coordinator_instance

# API路由
@app.get("/")
async def root():
    """根路径 - API信息"""
    return {
        "name": "电商全链路多Agent智能体API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "workflow": "/api/workflow",
            "agent": "/api/agent",
            "tasks": "/api/tasks/{task_id}"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/workflow", response_model=TaskStatusResponse)
async def run_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks
):
    """运行完整工作流"""
    # 验证平台
    valid_platforms = ["抖音", "淘宝", "拼多多", "小红书"]
    if request.platform not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"无效的平台，可选值: {', '.join(valid_platforms)}"
        )
    
    # 创建任务
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }
    
    # 后台运行任务
    background_tasks.add_task(
        run_workflow_background,
        task_id,
        request.platform,
        request.use_llm,
        request.llm_provider
    )
    
    return TaskStatusResponse(
        task_id=task_id,
        status="pending",
        created_at=tasks[task_id]["created_at"]
    )

@app.post("/api/agent", response_model=TaskStatusResponse)
async def run_single_agent(
    request: SingleAgentRequest,
    background_tasks: BackgroundTasks
):
    """运行单个Agent"""
    # 验证Agent名称
    valid_agents = ["market", "product", "content", "ad", "after_sales"]
    if request.agent_name not in valid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"无效的Agent名称，可选值: {', '.join(valid_agents)}"
        )
    
    # 创建任务
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }
    
    # 后台运行任务
    background_tasks.add_task(
        run_agent_background,
        task_id,
        request.agent_name,
        request.platform,
        request.inputs or {}
    )
    
    return TaskStatusResponse(
        task_id=task_id,
        status="pending",
        created_at=tasks[task_id]["created_at"]
    )

@app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        created_at=task["created_at"],
        result=task.get("result"),
        error=task.get("error")
    )

@app.get("/api/tasks")
async def list_tasks():
    """列出所有任务"""
    return {
        "total_tasks": len(tasks),
        "tasks": [
            {
                "task_id": task_id,
                "status": task["status"],
                "created_at": task["created_at"]
            }
            for task_id, task in tasks.items()
        ]
    }

# 后台任务函数
async def run_workflow_background(
    task_id: str,
    platform: str,
    use_llm: bool,
    llm_provider: str
):
    """后台运行完整工作流"""
    try:
        tasks[task_id]["status"] = "running"
        
        # 获取协调器
        coordinator = get_coordinator(llm_provider if use_llm else "mock")
        
        # 运行工作流
        result = coordinator.run_full_workflow(platform=platform)
        
        # 转换结果为可JSON序列化
        result_serializable = make_json_serializable(result)
        
        tasks[task_id]["result"] = result_serializable
        tasks[task_id]["status"] = "completed"
        
    except Exception as e:
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["status"] = "failed"

async def run_agent_background(
    task_id: str,
    agent_name: str,
    platform: str,
    inputs: Dict[str, Any]
):
    """后台运行单个Agent"""
    try:
        tasks[task_id]["status"] = "running"
        
        # 获取协调器
        coordinator = get_coordinator()
        
        # 准备参数
        kwargs = inputs.copy()
        if agent_name == "market" and "platform" not in kwargs:
            kwargs["platform"] = platform
        
        # 运行Agent
        result = coordinator.run_single_agent(agent_name, **kwargs)
        
        # 转换结果为可JSON序列化
        result_serializable = make_json_serializable(result)
        
        tasks[task_id]["result"] = result_serializable
        tasks[task_id]["status"] = "completed"
        
    except Exception as e:
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["status"] = "failed"

def make_json_serializable(obj):
    """使对象可JSON序列化"""
    def convert(o):
        if hasattr(o, 'to_dict'):
            return o.to_dict()
        elif hasattr(o, '__dict__'):
            return o.__dict__
        elif isinstance(o, (int, float, str, bool, type(None))):
            return o
        elif isinstance(o, list):
            return [convert(item) for item in o]
        elif isinstance(o, dict):
            return {str(k): convert(v) for k, v in o.items()}
        else:
            return str(o)
    
    return convert(obj)

# 启动服务
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🛒 电商全链路多Agent智能体API服务")
    print("=" * 60)
    print(f"API文档: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"健康检查: http://{settings.API_HOST}:{settings.API_PORT}/health")
    print("=" * 60)
    
    uvicorn.run(
        "run_api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
