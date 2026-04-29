"""
增强版API服务 - 包含WebSocket实时推送、缓存、高级分析
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid
import json
from datetime import datetime
import asyncio

from config.settings import get_settings
from core.coordinator import EcommerceAgentCoordinator
from utils.llm_factory import LLMFactory
from data.database import db_manager
from api.websocket import manager, notify_workflow_progress, notify_analysis_complete
from core.cache_manager import cache_manager

# 初始化
settings = get_settings()

app = FastAPI(
    title="🚀 电商全链路多Agent智能体API - 增强版",
    description="支持实时推送、智能缓存、高级分析的增强版API",
    version="2.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储运行中的任务
tasks = {}
coordinator_instances = {}

# ==================== Pydantic模型 ====================

class WorkflowRequest(BaseModel):
    platform: str = Field(..., description="电商平台", example="抖音")
    use_llm: bool = Field(False, description="是否使用LLM")
    llm_provider: Optional[str] = Field("mock", description="LLM提供商")
    use_cache: bool = Field(True, description="是否使用缓存")
    cache_ttl: Optional[int] = Field(3600, description="缓存有效期(秒)")

class SingleAgentRequest(BaseModel):
    agent_name: str = Field(..., description="Agent名称", example="market")
    platform: Optional[str] = Field("抖音", description="电商平台")
    inputs: Optional[Dict[str, Any]] = Field(None, description="Agent输入参数")
    use_cache: bool = Field(True, description="是否使用缓存")

class CacheRequest(BaseModel):
    cache_key: str = Field(..., description="缓存键")

class UserPreferenceRequest(BaseModel):
    user_id: str = Field(..., description="用户ID")
    default_platform: Optional[str] = Field("抖音", description="默认平台")
    llm_provider: Optional[str] = Field("mock", description="默认LLM")
    theme: Optional[str] = Field("dark", description="主题")

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    created_at: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    cache_hit: bool = False

# ==================== 工具函数 ====================

def get_coordinator(llm_provider: str = "mock", task_id: str = None):
    """获取或创建协调器实例"""
    cache_key = f"{task_id}:{llm_provider}" if task_id else llm_provider
    
    if cache_key not in coordinator_instances:
        llm = None
        if llm_provider != "mock":
            try:
                llm = LLMFactory.create_llm(provider=llm_provider)
            except Exception as e:
                print(f"LLM加载失败: {e}")
        
        coordinator_instances[cache_key] = EcommerceAgentCoordinator(llm=llm)
    
    return coordinator_instances[cache_key]

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
        elif isinstance(o, datetime):
            return o.isoformat()
        else:
            return str(o)
    
    return convert(obj)

# ==================== WebSocket路由 ====================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket连接端点"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理消息类型
            if message.get("type") == "join_workflow":
                workflow_id = message.get("workflow_id")
                manager.join_room(client_id, workflow_id)
                await manager.send_personal_message(
                    {"type": "joined", "workflow_id": workflow_id},
                    client_id
                )
            
            elif message.get("type") == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now().isoformat()},
                    client_id
                )
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# ==================== API路由 ====================

@app.get("/")
async def root():
    """API信息"""
    return {
        "name": "🚀 电商全链路多Agent智能体API - 增强版",
        "version": "2.0.0",
        "features": [
            "实时WebSocket推送",
            "智能结果缓存",
            "高级数据分析",
            "用户偏好管理",
            "性能监控"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "websocket": "/ws/{client_id}",
            "workflow": "/api/workflow",
            "agent": "/api/agent",
            "cache": "/api/cache/{cache_key}",
            "tasks": "/api/tasks/{task_id}",
            "preferences": "/api/preferences"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    # 检查数据库连接
    try:
        runs = db_manager.get_recent_runs(limit=1)
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "active_tasks": len(tasks),
        "active_connections": len(manager.active_connections)
    }

@app.post("/api/workflow", response_model=TaskStatusResponse)
async def run_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks
):
    """运行完整工作流（支持缓存）"""
    valid_platforms = ["抖音", "淘宝", "拼多多", "小红书"]
    if request.platform not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"无效的平台，可选值: {', '.join(valid_platforms)}"
        )
    
    # 生成缓存键
    cache_key = cache_manager.generate_cache_key(
        "workflow", 
        request.platform, 
        request.llm_provider,
        request.use_llm
    )
    
    # 检查缓存
    if request.use_cache:
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return TaskStatusResponse(
                task_id="cached",
                status="completed",
                created_at=datetime.now().isoformat(),
                result=cached_result,
                cache_hit=True
            )
    
    # 创建任务
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None,
        "cache_key": cache_key if request.use_cache else None,
        "platform": request.platform
    }
    
    # 后台运行任务
    background_tasks.add_task(
        run_workflow_background,
        task_id,
        request.platform,
        request.use_llm,
        request.llm_provider,
        request.cache_ttl
    )
    
    return TaskStatusResponse(
        task_id=task_id,
        status="pending",
        created_at=tasks[task_id]["created_at"],
        cache_hit=False
    )

@app.post("/api/agent", response_model=TaskStatusResponse)
async def run_single_agent(request: SingleAgentRequest):
    """运行单个Agent（同步执行）"""
    valid_agents = ["market", "product", "content", "ad", "after_sales"]
    if request.agent_name not in valid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"无效的Agent名称，可选值: {', '.join(valid_agents)}"
        )
    
    # 检查缓存
    if request.use_cache:
        cache_key = cache_manager.generate_cache_key(
            f"agent_{request.agent_name}",
            request.platform,
            request.inputs
        )
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return TaskStatusResponse(
                task_id="cached",
                status="completed",
                created_at=datetime.now().isoformat(),
                result=cached_result,
                cache_hit=True
            )
    
    # 执行Agent
    try:
        coordinator = get_coordinator()
        kwargs = request.inputs or {}
        if request.agent_name == "market":
            kwargs["platform"] = request.platform
        
        result = coordinator.run_single_agent(request.agent_name, **kwargs)
        result_serializable = make_json_serializable(result)
        
        # 保存缓存
        if request.use_cache:
            cache_manager.set(
                cache_key, 
                result_serializable, 
                request.platform,
                f"agent_{request.agent_name}"
            )
        
        return TaskStatusResponse(
            task_id=str(uuid.uuid4()),
            status="completed",
            created_at=datetime.now().isoformat(),
            result=result_serializable,
            cache_hit=False
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cache/{cache_key}")
async def get_cache(cache_key: str):
    """获取缓存值"""
    cached = cache_manager.get(cache_key)
    if cached:
        return {"cached": True, "data": cached}
    return {"cached": False}

@app.delete("/api/cache/{cache_key}")
async def delete_cache(cache_key: str):
    """删除缓存"""
    cache_manager.delete(cache_key)
    return {"deleted": True}

@app.post("/api/cache/clear")
async def clear_all_cache():
    """清空所有缓存"""
    count = db_manager.clear_expired_cache()
    cache_manager.clear()
    return {"cleared": True, "expired_entries": count}

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
        error=task.get("error"),
        cache_hit=False
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
                "created_at": task["created_at"],
                "platform": task.get("platform", "unknown")
            }
            for task_id, task in tasks.items()
        ]
    }

@app.post("/api/preferences")
async def save_preferences(request: UserPreferenceRequest):
    """保存用户偏好"""
    preferences = {
        "default_platform": request.default_platform,
        "llm_provider": request.llm_provider,
        "theme": request.theme
    }
    db_manager.save_user_preference(request.user_id, preferences)
    return {"saved": True}

@app.get("/api/preferences/{user_id}")
async def get_preferences(user_id: str):
    """获取用户偏好"""
    prefs = db_manager.get_user_preference(user_id)
    if prefs:
        return {"found": True, "preferences": prefs}
    return {"found": False}

@app.get("/api/analytics/agents")
async def get_agent_analytics(agent_name: Optional[str] = None, days: int = 30):
    """获取Agent性能分析"""
    stats = db_manager.get_agent_performance_stats(agent_name, days)
    if stats:
        return {"found": True, "stats": stats}
    return {"found": False, "message": "No data available"}

@app.get("/api/analytics/workflows")
async def get_workflow_analytics(limit: int = 10):
    """获取工作流分析历史"""
    runs = db_manager.get_recent_runs(limit=limit)
    return {
        "workflows": [
            {
                "id": run.id,
                "platform": run.platform,
                "status": run.status,
                "start_time": run.start_time.isoformat() if run.start_time else None,
                "execution_time": run.execution_time_seconds
            }
            for run in runs
        ]
    }

# ==================== 后台任务函数 ====================

async def run_workflow_background(
    task_id: str,
    platform: str,
    use_llm: bool,
    llm_provider: str,
    cache_ttl: int
):
    """后台运行完整工作流"""
    try:
        tasks[task_id]["status"] = "running"
        
        # 通知开始
        await notify_workflow_progress(task_id, "market", 1, 5, "running")
        
        # 获取协调器
        coordinator = get_coordinator(llm_provider if use_llm else "mock", task_id)
        
        # 创建WebSocket回调
        async def websocket_callback(agent_name: str, current: int, total: int):
            await notify_workflow_progress(task_id, agent_name, current, total, "running")
        
        # 运行工作流
        result = coordinator.run_full_workflow(
            platform=platform,
            callback=lambda a, c, t: asyncio.create_task(websocket_callback(a, c, t))
        )
        
        # 转换结果为可JSON序列化
        result_serializable = make_json_serializable(result)
        
        # 保存结果
        tasks[task_id]["result"] = result_serializable
        tasks[task_id]["status"] = "completed"
        
        # 保存到数据库
        db_manager.save_workflow_run(platform, result)
        
        # 保存到缓存
        if tasks[task_id].get("cache_key"):
            cache_manager.set(
                tasks[task_id]["cache_key"],
                result_serializable,
                platform,
                "workflow",
                cache_ttl
            )
        
        # 通知完成
        await notify_analysis_complete(task_id, result.get("summary_kpis", {}))
        
    except Exception as e:
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["status"] = "failed"
        await notify_workflow_progress(task_id, "error", 0, 5, "error")

# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🚀 电商全链路多Agent智能体API - 增强版 v2.0")
    print("=" * 70)
    print(f"📚 API文档: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"💓 健康检查: http://{settings.API_HOST}:{settings.API_PORT}/health")
    print(f"🔌 WebSocket: ws://{settings.API_HOST}:{settings.API_PORT}/ws/{{client_id}}")
    print("=" * 70)
    print("✨ 新特性:")
    print("   • 实时WebSocket推送")
    print("   • 智能结果缓存")
    print("   • 高级数据分析")
    print("   • 用户偏好管理")
    print("=" * 70)
    
    uvicorn.run(
        "run_api_enhanced:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
