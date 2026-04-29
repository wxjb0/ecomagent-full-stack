import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent
from data.mock_data import get_ad_performance_data

class AdOptimizationAgent(BaseAgent):
    """投放优化Agent - 优化广告投放策略"""
    
    def __init__(self, llm: Optional[BaseLLM] = None, memory=None):
        super().__init__(llm, memory, agent_name="AdOptimizationAgent")
        
    def run(self, content_matrix: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行投放优化
        
        Args:
            content_matrix: 内容创作Agent的输出
            
        Returns:
            包含投放优化方案的字典
        """
        self.log("开始广告投放优化分析...")
        
        # 1. 获取广告表现数据
        ad_data = get_ad_performance_data()
        
        # 2. 分析当前投放效果
        performance_analysis = self._analyze_performance(ad_data)
        
        # 3. 生成优化建议
        optimization_actions = self._generate_optimizations(
            performance_analysis,
            content_matrix
        )
        
        # 4. 生成投放计划
        media_plan = self._generate_media_plan(
            optimization_actions,
            content_matrix
        )
        
        # 5. 生成优化报告
        optimization_report = self._generate_optimization_report(
            performance_analysis,
            optimization_actions,
            media_plan
        )
        
        self.save_to_memory(
            "优化广告投放",
            f"生成了{len(optimization_actions)}条优化建议"
        )
        
        self.log("投放优化完成")
        
        return {
            "ad_performance_data": ad_data.to_dict("records"),
            "performance_analysis": performance_analysis,
            "optimization_actions": optimization_actions,
            "media_plan": media_plan,
            "optimization_report": optimization_report,
            "expected_improvement": {
                "ctr": "+15-20%",
                "roi": "+20-25%",
                "cpc": "-10-15%"
            }
        }
    
    def _analyze_performance(self, ad_data: pd.DataFrame) -> Dict[str, Any]:
        """分析广告表现数据"""
        df = ad_data.copy()
        
        # 计算综合指标
        df["efficiency_score"] = (
            df["roi"] * 0.4 +
            (df["ctr"] * 100) * 0.3 +
            (1 / df["cpc"]) * 0.3
        )
        
        # 按计划分析
        plan_analysis = df.groupby("plan_id").agg({
            "impressions": "sum",
            "clicks": "sum",
            "cost": "sum",
            "revenue": "sum",
            "ctr": "mean",
            "cpc": "mean",
            "roi": "mean"
        }).reset_index()
        
        # 按产品分析
        product_analysis = df.groupby("product").agg({
            "roi": "mean",
            "ctr": "mean",
            "cpc": "mean"
        }).sort_values("roi", ascending=False).reset_index()
        
        # 按时段分析（模拟）
        time_slots = ["0-6", "6-12", "12-18", "18-24"]
        time_performance = pd.DataFrame({
            "time_slot": time_slots,
            "ctr": [0.021, 0.042, 0.058, 0.085],
            "cpc": [0.8, 1.2, 1.5, 1.8],
            "roi": [1.2, 2.1, 2.8, 3.5]
        })
        
        return {
            "overall_metrics": {
                "total_impressions": int(df["impressions"].sum()),
                "total_clicks": int(df["clicks"].sum()),
                "total_cost": float(df["cost"].sum()),
                "total_revenue": float(df["revenue"].sum()),
                "avg_ctr": float(df["ctr"].mean()),
                "avg_cpc": float(df["cpc"].mean()),
                "overall_roi": float(df["revenue"].sum() / df["cost"].sum())
            },
            "plan_analysis": plan_analysis.to_dict("records"),
            "product_analysis": product_analysis.to_dict("records"),
            "time_performance": time_performance.to_dict("records"),
            "top_performers": {
                "best_plan": df.loc[df["roi"].idxmax(), "plan_id"],
                "best_product": df.loc[df["roi"].idxmax(), "product"],
                "best_time_slot": "18-24"
            },
            "underperformers": {
                "worst_plan": df.loc[df["roi"].idxmin(), "plan_id"],
                "low_roi_plans": df[df["roi"] < 2.0]["plan_id"].tolist()
            }
        }
    
    def _generate_optimizations(
        self,
        analysis: Dict,
        content_matrix: Dict
    ) -> List[Dict]:
        """生成优化建议"""
        optimizations = []
        
        # 1. 预算分配优化
        overall = analysis["overall_metrics"]
        optimizations.append({
            "type": "budget_allocation",
            "priority": "high",
            "action": "增加高ROI计划预算，削减低ROI计划",
            "details": f"将{analysis['underperformers']['worst_plan']}的预算削减30%，转移到{analysis['top_performers']['best_plan']}",
            "expected_impact": "ROI提升10-15%"
        })
        
        # 2. 出价优化
        avg_cpc = overall["avg_cpc"]
        optimizations.append({
            "type": "bid_optimization",
            "priority": "high",
            "action": "分时出价策略",
            "details": "在18-24点黄金时段提高出价20%，在0-6点降低出价40%",
            "expected_impact": "CTR提升8-12%，CPC降低5-8%"
        })
        
        # 3. 人群定向优化
        optimizations.append({
            "type": "targeting",
            "priority": "medium",
            "action": "精细化人群定向",
            "details": "基于高转化人群特征，扩展相似人群（Lookalike），排除低转化人群",
            "expected_impact": "转化率提升15-20%"
        })
        
        # 4. 创意优化
        optimizations.append({
            "type": "creative",
            "priority": "medium",
            "action": "A/B测试不同创意素材",
            "details": "为每个产品准备3-5套创意素材，进行A/B测试，保留CTR最高的素材",
            "expected_impact": "CTR提升10-15%"
        })
        
        # 5. 产品组合优化
        product_analysis = analysis["product_analysis"]
        if len(product_analysis) > 1:
            optimizations.append({
                "type": "product_mix",
                "priority": "medium",
                "action": "优化产品投放组合",
                "details": f"重点投放{product_analysis[0]['product']}，考虑暂停或优化{product_analysis[-1]['product']}",
                "expected_impact": "整体ROI提升8-10%"
            })
        
        return optimizations
    
    def _generate_media_plan(
        self,
        optimizations: List[Dict],
        content_matrix: Dict
    ) -> Dict[str, Any]:
        """生成媒体投放计划"""
        products = list(content_matrix.keys())
        
        return {
            "budget_allocation": {
                "total_daily_budget": 5000,
                "distribution": {
                    "抖音": 0.5,
                    "快手": 0.2,
                    "淘宝直通车": 0.2,
                    "其他": 0.1
                }
            },
            "time_schedule": {
                "prime_time": {
                    "hours": "18:00-24:00",
                    "budget_percentage": 60,
                    "bid_multiplier": 1.2
                },
                "normal_time": {
                    "hours": "6:00-18:00",
                    "budget_percentage": 35,
                    "bid_multiplier": 1.0
                },
                "low_time": {
                    "hours": "0:00-6:00",
                    "budget_percentage": 5,
                    "bid_multiplier": 0.6
                }
            },
            "product_priority": {
                product: "high" if i < 2 else "medium"
                for i, product in enumerate(products)
            },
            "kpi_targets": {
                "ctr": ">6%",
                "cpc": "<1.5元",
                "roi": ">3.0",
                "conversion_rate": ">3%"
            },
            "optimization_frequency": {
                "bid_adjustment": "每日",
                "creative_refresh": "每周",
                "targeting_review": "每两周"
            }
        }
    
    def _generate_optimization_report(
        self,
        analysis: Dict,
        optimizations: List[Dict],
        media_plan: Dict
    ) -> str:
        """生成优化报告"""
        overall = analysis["overall_metrics"]
        
        return f"""
【广告投放优化报告】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

当前表现概览：
  • 总曝光：{overall['total_impressions']:,}次
  • 总点击：{overall['total_clicks']:,}次
  • 平均CTR：{overall['avg_ctr']:.2%}
  • 平均CPC：¥{overall['avg_cpc']:.2f}
  • 整体ROI：{overall['overall_roi']:.2f}

优化建议汇总：
{chr(10).join([
    f"{i+1}. [{opt['priority'].upper()}] {opt['action']}"
    for i, opt in enumerate(optimizations)
])}

预期提升：
  • CTR：+15-20%
  • ROI：+20-25%
  • CPC：-10-15%

建议立即执行高优先级优化动作，并在3天后评估效果。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
