"""
数据库模块 - 支持SQLite/MySQL/PostgreSQL
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config.settings import get_settings

settings = get_settings()

Base = declarative_base()

class WorkflowRun(Base):
    """工作流运行记录"""
    __tablename__ = "workflow_runs"
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50))
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime)
    status = Column(String(20))
    execution_time_seconds = Column(Float)
    result_summary = Column(JSON)
    full_result = Column(JSON)

class AgentOutput(Base):
    """Agent输出记录"""
    __tablename__ = "agent_outputs"
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer)
    agent_name = Column(String(50))
    output_data = Column(JSON)
    execution_time_seconds = Column(Float)
    status = Column(String(20))  # success, error, timeout
    created_at = Column(DateTime, default=datetime.now)

class AnalysisCache(Base):
    """分析结果缓存 - 避免重复计算"""
    __tablename__ = "analysis_cache"
    
    id = Column(Integer, primary_key=True)
    cache_key = Column(String(255), unique=True, index=True)  # 平台+参数哈希
    platform = Column(String(50))
    cache_type = Column(String(50))  # workflow, market, product等
    result_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)  # 缓存过期时间
    hit_count = Column(Integer, default=0)  # 命中次数

class UserPreference(Base):
    """用户偏好设置"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, index=True)
    default_platform = Column(String(50), default="抖音")
    llm_provider = Column(String(50), default="mock")
    auto_save_results = Column(Integer, default=1)
    theme = Column(String(20), default="dark")
    language = Column(String(10), default="zh")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

class WorkflowAnalytics(Base):
    """工作流分析统计"""
    __tablename__ = "workflow_analytics"
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, index=True)
    agent_name = Column(String(50))
    
    # 性能指标
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    execution_time_ms = Column(Integer)
    memory_usage_mb = Column(Float)
    
    # 业务指标
    input_size = Column(Integer)  # 输入数据大小
    output_size = Column(Integer)  # 输出数据大小
    processing_steps = Column(Integer)  # 处理步骤数
    
    # 异常记录
    has_error = Column(Integer, default=0)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.now)

class AgentPerformance(Base):
    """Agent性能历史"""
    __tablename__ = "agent_performance"
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(50), index=True)
    date = Column(DateTime, index=True)
    
    # 统计指标
    total_runs = Column(Integer, default=0)
    success_runs = Column(Integer, default=0)
    error_runs = Column(Integer, default=0)
    avg_execution_time = Column(Float)
    avg_memory_usage = Column(Float)
    
    # 业务效果指标
    avg_roi_improvement = Column(Float)  # 平均ROI提升
    avg_cost_reduction = Column(Float)  # 平均成本降低
    customer_satisfaction = Column(Float)  # 客户满意度
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

class MarketTrend(Base):
    """市场趋势历史数据"""
    __tablename__ = "market_trends"
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), index=True)
    category = Column(String(100), index=True)
    date = Column(DateTime, index=True)
    
    # 市场指标
    growth_rate = Column(Float)
    competition_score = Column(Float)
    profit_margin = Column(Float)
    market_size = Column(Float)
    
    # 趋势分析
    trend_direction = Column(String(20))  # up, down, stable
    confidence_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.now)

class DatabaseManager:
    """增强版数据库管理器 - 支持缓存、分析、监控等创新功能"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    # ==================== 工作流管理 ====================
    def save_workflow_run(self, platform: str, result: dict, status: str = "completed") -> int:
        """保存工作流运行记录"""
        session = self.Session()
        try:
            run = WorkflowRun(
                platform=platform,
                status=status,
                end_time=datetime.now(),
                execution_time_seconds=result.get("execution_info", {}).get("execution_time_seconds"),
                result_summary=result.get("summary_kpis"),
                full_result=result
            )
            session.add(run)
            session.commit()
            workflow_id = run.id
            
            # 同时保存各Agent的输出
            if "results" in result:
                for agent_name, output in result["results"].items():
                    agent_record = AgentOutput(
                        workflow_id=workflow_id,
                        agent_name=agent_name,
                        output_data=output,
                        status="success"
                    )
                    session.add(agent_record)
            
            session.commit()
            return workflow_id
        finally:
            session.close()
    
    def get_recent_runs(self, limit: int = 10, platform: str = None):
        """获取最近的运行记录"""
        session = self.Session()
        try:
            query = session.query(WorkflowRun)
            if platform:
                query = query.filter(WorkflowRun.platform == platform)
            runs = query.order_by(WorkflowRun.start_time.desc()).limit(limit).all()
            return runs
        finally:
            session.close()
    
    def get_workflow_by_id(self, workflow_id: int):
        """获取特定工作流详情"""
        session = self.Session()
        try:
            return session.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
        finally:
            session.close()
    
    # ==================== 缓存管理 ====================
    def get_cached_result(self, cache_key: str) -> dict:
        """获取缓存结果"""
        session = self.Session()
        try:
            cache = session.query(AnalysisCache).filter(
                AnalysisCache.cache_key == cache_key,
                AnalysisCache.expires_at > datetime.now()
            ).first()
            
            if cache:
                cache.hit_count += 1
                session.commit()
                return cache.result_data
            return None
        finally:
            session.close()
    
    def set_cached_result(self, cache_key: str, platform: str, 
                         cache_type: str, result: dict, 
                         expire_hours: int = 24):
        """设置缓存结果"""
        session = self.Session()
        try:
            # 检查是否已存在
            existing = session.query(AnalysisCache).filter(
                AnalysisCache.cache_key == cache_key
            ).first()
            
            if existing:
                existing.result_data = result
                existing.expires_at = datetime.now() + timedelta(hours=expire_hours)
                existing.hit_count = 0
            else:
                cache = AnalysisCache(
                    cache_key=cache_key,
                    platform=platform,
                    cache_type=cache_type,
                    result_data=result,
                    expires_at=datetime.now() + timedelta(hours=expire_hours)
                )
                session.add(cache)
            
            session.commit()
        finally:
            session.close()
    
    def clear_expired_cache(self):
        """清理过期缓存"""
        session = self.Session()
        try:
            expired = session.query(AnalysisCache).filter(
                AnalysisCache.expires_at < datetime.now()
            ).all()
            for cache in expired:
                session.delete(cache)
            session.commit()
            return len(expired)
        finally:
            session.close()
    
    # ==================== 用户偏好 ====================
    def get_user_preference(self, user_id: str) -> dict:
        """获取用户偏好"""
        session = self.Session()
        try:
            pref = session.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if pref:
                return {
                    "default_platform": pref.default_platform,
                    "llm_provider": pref.llm_provider,
                    "auto_save_results": bool(pref.auto_save_results),
                    "theme": pref.theme,
                    "language": pref.language
                }
            return None
        finally:
            session.close()
    
    def save_user_preference(self, user_id: str, preferences: dict):
        """保存用户偏好"""
        session = self.Session()
        try:
            pref = session.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if pref:
                pref.default_platform = preferences.get("default_platform", pref.default_platform)
                pref.llm_provider = preferences.get("llm_provider", pref.llm_provider)
                pref.auto_save_results = 1 if preferences.get("auto_save_results", True) else 0
                pref.theme = preferences.get("theme", pref.theme)
                pref.language = preferences.get("language", pref.language)
                pref.updated_at = datetime.now()
            else:
                pref = UserPreference(
                    user_id=user_id,
                    default_platform=preferences.get("default_platform", "抖音"),
                    llm_provider=preferences.get("llm_provider", "mock"),
                    auto_save_results=1 if preferences.get("auto_save_results", True) else 0,
                    theme=preferences.get("theme", "dark"),
                    language=preferences.get("language", "zh")
                )
                session.add(pref)
            
            session.commit()
        finally:
            session.close()
    
    # ==================== 性能分析 ====================
    def record_workflow_analytics(self, workflow_id: int, agent_name: str,
                                 start_time: datetime, end_time: datetime,
                                 input_size: int, output_size: int,
                                 has_error: bool = False, error_message: str = None):
        """记录工作流分析数据"""
        session = self.Session()
        try:
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            analytics = WorkflowAnalytics(
                workflow_id=workflow_id,
                agent_name=agent_name,
                start_time=start_time,
                end_time=end_time,
                execution_time_ms=execution_time_ms,
                input_size=input_size,
                output_size=output_size,
                has_error=1 if has_error else 0,
                error_message=error_message
            )
            session.add(analytics)
            session.commit()
        finally:
            session.close()
    
    def get_agent_performance_stats(self, agent_name: str = None, days: int = 30):
        """获取Agent性能统计"""
        session = self.Session()
        try:
            from_date = datetime.now() - timedelta(days=days)
            query = session.query(WorkflowAnalytics).filter(
                WorkflowAnalytics.created_at >= from_date
            )
            
            if agent_name:
                query = query.filter(WorkflowAnalytics.agent_name == agent_name)
            
            analytics = query.all()
            
            if not analytics:
                return None
            
            total_runs = len(analytics)
            error_runs = sum(1 for a in analytics if a.has_error)
            success_runs = total_runs - error_runs
            avg_time = sum(a.execution_time_ms for a in analytics) / total_runs
            
            return {
                "total_runs": total_runs,
                "success_runs": success_runs,
                "error_runs": error_runs,
                "success_rate": success_runs / total_runs if total_runs > 0 else 0,
                "avg_execution_time_ms": avg_time,
                "date_range": f"{from_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}"
            }
        finally:
            session.close()
    
    # ==================== 市场趋势 ====================
    def save_market_trend(self, platform: str, category: str,
                         growth_rate: float, competition_score: float,
                         profit_margin: float, market_size: float,
                         trend_direction: str, confidence_score: float):
        """保存市场趋势数据"""
        session = self.Session()
        try:
            trend = MarketTrend(
                platform=platform,
                category=category,
                date=datetime.now(),
                growth_rate=growth_rate,
                competition_score=competition_score,
                profit_margin=profit_margin,
                market_size=market_size,
                trend_direction=trend_direction,
                confidence_score=confidence_score
            )
            session.add(trend)
            session.commit()
        finally:
            session.close()
    
    def get_market_trends(self, platform: str, category: str = None, days: int = 30):
        """获取市场趋势历史"""
        session = self.Session()
        try:
            from_date = datetime.now() - timedelta(days=days)
            query = session.query(MarketTrend).filter(
                MarketTrend.platform == platform,
                MarketTrend.date >= from_date
            )
            
            if category:
                query = query.filter(MarketTrend.category == category)
            
            trends = query.order_by(MarketTrend.date.desc()).all()
            return trends
        finally:
            session.close()
    
    # ==================== 报表导出 ====================
    def export_workflow_report(self, workflow_id: int) -> dict:
        """导出工作流完整报告"""
        session = self.Session()
        try:
            workflow = session.query(WorkflowRun).filter(
                WorkflowRun.id == workflow_id
            ).first()
            
            if not workflow:
                return None
            
            agent_outputs = session.query(AgentOutput).filter(
                AgentOutput.workflow_id == workflow_id
            ).all()
            
            return {
                "workflow": {
                    "id": workflow.id,
                    "platform": workflow.platform,
                    "start_time": workflow.start_time,
                    "end_time": workflow.end_time,
                    "status": workflow.status,
                    "execution_time": workflow.execution_time_seconds
                },
                "agent_outputs": [
                    {
                        "agent": output.agent_name,
                        "status": output.status,
                        "output": output.output_data
                    }
                    for output in agent_outputs
                ],
                "summary": workflow.result_summary
            }
        finally:
            session.close()

# 全局数据库管理器实例
db_manager = DatabaseManager()
