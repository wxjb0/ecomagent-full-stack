"""
多Agent协调器 - 管理整个电商全链路工作流
"""

import time
from typing import Dict, Any, List, Optional, Callable
from langchain.llms import BaseLLM

from core.memory import SharedAgentMemory
from core.agents.market_agent import MarketInsightAgent
from core.agents.product_agent import ProductSelectionAgent
from core.agents.content_agent import ContentCreationAgent
from core.agents.ad_agent import AdOptimizationAgent
from core.agents.after_sales_agent import AfterSalesAgent

class EcommerceAgentCoordinator:
    """多Agent协调器 - 管理整个电商全链路工作流"""
    
    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        use_shared_memory: bool = True
    ):
        self.llm = llm
        self.use_shared_memory = use_shared_memory
        
        # 初始化共享记忆
        self.shared_memory = SharedAgentMemory() if use_shared_memory else None
        
        # 初始化所有Agent
        self._init_agents()
        
        # 工作流状态
        self.workflow_state = {}
        self.execution_log = []
        
    def _init_agents(self):
        """初始化所有Agent"""
        memory = self.shared_memory.get_memory() if self.shared_memory else None
        
        self.agents = {
            "market": MarketInsightAgent(self.llm, memory),
            "product": ProductSelectionAgent(self.llm, memory),
            "content": ContentCreationAgent(self.llm, memory),
            "ad": AdOptimizationAgent(self.llm, memory),
            "after_sales": AfterSalesAgent(self.llm, memory)
        }
    
    def run_full_workflow(
        self,
        platform: str = "抖音",
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        执行完整的电商全链路工作流
        
        Args:
            platform: 电商平台名称
            callback: 进度回调函数
            
        Returns:
            包含所有Agent输出结果的完整字典
        """
        self._log("info", f"🚀 启动电商全链路多Agent系统，平台：{platform}")
        start_time = time.time()
        
        try:
            # Step 1: 市场洞察
            self._log("info", "📊 [1/5] 执行市场洞察分析...")
            if callback:
                callback("market", 1, 5)
            market_result = self.agents["market"].run(platform=platform)
            self.workflow_state["market"] = market_result
            self._save_to_shared_memory("market", market_result)
            
            # Step 2: 选品策略
            self._log("info", "🛒 [2/5] 生成选品策略...")
            if callback:
                callback("product", 2, 5)
            product_result = self.agents["product"].run(market_insight=market_result)
            self.workflow_state["product"] = product_result
            self._save_to_shared_memory("product", product_result)
            
            # Step 3: 内容创作
            self._log("info", "✍️ [3/5] 创作多平台营销内容...")
            if callback:
                callback("content", 3, 5)
            content_result = self.agents["content"].run(
                selected_products=product_result["selected_products"]
            )
            self.workflow_state["content"] = content_result
            self._save_to_shared_memory("content", content_result)
            
            # Step 4: 投放优化
            self._log("info", "📈 [4/5] 优化广告投放策略...")
            if callback:
                callback("ad", 4, 5)
            ad_result = self.agents["ad"].run(content_matrix=content_result["content_matrix"])
            self.workflow_state["ad"] = ad_result
            self._save_to_shared_memory("ad", ad_result)
            
            # Step 5: 售后舆情
            self._log("info", "💬 [5/5] 分析售后舆情...")
            if callback:
                callback("after_sales", 5, 5)
            after_sales_result = self.agents["after_sales"].run(ad_optimization=ad_result)
            self.workflow_state["after_sales"] = after_sales_result
            self._save_to_shared_memory("after_sales", after_sales_result)
            
            # 生成最终汇总
            final_result = self._generate_final_result(platform, start_time)
            
            self._log("success", "✅ 全链路工作流执行完成！")
            
            return final_result
            
        except Exception as e:
            self._log("error", f"❌ 工作流执行出错：{str(e)}")
            raise
    
    def run_single_agent(
        self,
        agent_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        单独运行某个Agent
        
        Args:
            agent_name: Agent名称 (market/product/content/ad/after_sales)
            **kwargs: 传递给Agent的参数
            
        Returns:
            Agent的输出结果
        """
        if agent_name not in self.agents:
            raise ValueError(f"未知的Agent: {agent_name}")
        
        self._log("info", f"运行单个Agent: {agent_name}")
        result = self.agents[agent_name].run(**kwargs)
        
        self.workflow_state[agent_name] = result
        self._save_to_shared_memory(agent_name, result)
        
        return result
    
    def get_workflow_state(self) -> Dict[str, Any]:
        """获取当前工作流状态"""
        return self.workflow_state
    
    def get_execution_log(self) -> List[Dict]:
        """获取执行日志"""
        return self.execution_log
    
    def reset_workflow(self):
        """重置工作流"""
        self.workflow_state = {}
        self.execution_log = []
        if self.shared_memory:
            self.shared_memory.clear()
        self._init_agents()
        self._log("info", "工作流已重置")
    
    def _generate_final_result(self, platform: str, start_time: float) -> Dict[str, Any]:
        """生成最终汇总结果"""
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 从各Agent结果中提取关键指标
        market = self.workflow_state.get("market", {})
        product = self.workflow_state.get("product", {})
        content = self.workflow_state.get("content", {})
        ad = self.workflow_state.get("ad", {})
        after_sales = self.workflow_state.get("after_sales", {})
        
        # 汇总KPI
        kpis = self._aggregate_kpis(market, product, content, ad, after_sales)
        
        return {
            "platform": platform,
            "execution_info": {
                "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)),
                "end_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)),
                "execution_time_seconds": round(execution_time, 2),
                "agents_executed": list(self.workflow_state.keys())
            },
            "results": {
                "market_insight": market,
                "product_selection": product,
                "content_creation": content,
                "ad_optimization": ad,
                "after_sales": after_sales
            },
            "summary_kpis": kpis,
            "executive_summary": self._generate_executive_summary(kpis, platform),
            "execution_log": self.execution_log
        }
    
    def _aggregate_kpis(
        self,
        market: Dict,
        product: Dict,
        content: Dict,
        ad: Dict,
        after_sales: Dict
    ) -> Dict[str, Any]:
        """汇总关键指标"""
        # 从各Agent结果中提取KPI
        product_count = len(product.get("selected_products", []))
        platforms_covered = content.get("platforms", [])
        
        ad_expected = ad.get("expected_improvement", {})
        sentiment = after_sales.get("sentiment_analysis", {}).get("overall", {})
        
        return {
            "operational": {
                "selected_products": product_count,
                "platforms_covered": platforms_covered,
                "content_types": ["短视频", "图文", "直播", "详情页"]
            },
            "performance_improvement": {
                "estimated_ctr_improvement": ad_expected.get("ctr", "+15-20%"),
                "estimated_roi_improvement": ad_expected.get("roi", "+20-25%"),
                "estimated_cpc_reduction": ad_expected.get("cpc", "-10-15%"),
                "estimated_cost_reduction": "65%",
                "estimated_efficiency_improvement": "70%"
            },
            "customer_feedback": {
                "positive_rate": f"{sentiment.get('positive_rate', 0):.1%}",
                "alert_level": after_sales.get("sentiment_analysis", {}).get("alert_level", "low")
            }
        }
    
    def _generate_executive_summary(self, kpis: Dict, platform: str) -> str:
        """生成执行摘要"""
        perf = kpis["performance_improvement"]
        
        return f"""
【电商全链路运营方案执行摘要】

平台：{platform}

核心成果：
✓ 完成市场洞察分析，识别高潜力品类
✓ 选定{kpis['operational']['selected_products']}个核心产品
✓ 生成覆盖{kpis['operational']['platforms_covered']}的全平台内容矩阵
✓ 制定精细化广告投放优化方案
✓ 建立售后舆情监测与响应机制

预期提升：
• 人力成本降低：{perf['estimated_cost_reduction']}
• 运营效率提升：{perf['estimated_efficiency_improvement']}
• 广告ROI提升：{perf['estimated_roi_improvement']}
• 点击率提升：{perf['estimated_ctr_improvement']}

建议立即启动执行，并建立每周复盘机制。
        """.strip()
    
    def _save_to_shared_memory(self, agent_name: str, result: Dict):
        """保存结果到共享记忆"""
        if self.shared_memory:
            self.shared_memory.save_agent_output(agent_name, result)
    
    def _log(self, level: str, message: str):
        """记录日志"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "level": level.upper(),
            "message": message
        }
        self.execution_log.append(log_entry)
        
        # 同时打印到控制台
        prefix = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }.get(level, "•")
        
        print(f"{prefix} {message}")
