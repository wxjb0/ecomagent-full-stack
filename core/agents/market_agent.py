import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent
from data.mock_data import get_market_data

class MarketInsightAgent(BaseAgent):
    """市场洞察Agent - 负责分析市场趋势、竞争格局和潜力品类"""
    
    def __init__(self, llm: Optional[BaseLLM] = None, memory=None):
        super().__init__(llm, memory, agent_name="MarketInsightAgent")
        self.market_data = None
        
    def run(self, platform: str = "抖音", **kwargs) -> Dict[str, Any]:
        """
        执行市场洞察分析
        
        Args:
            platform: 电商平台名称 (抖音/淘宝/拼多多/小红书)
            
        Returns:
            包含市场洞察结果的字典
        """
        self.log(f"开始分析{platform}平台市场数据...")
        
        # 1. 获取市场数据
        self.market_data = get_market_data()
        
        # 2. 数据分析
        analysis_result = self._analyze_market_data(platform)
        
        # 3. 生成洞察报告
        insight_report = self._generate_insight_report(analysis_result, platform)
        
        # 4. 保存到记忆
        self.save_to_memory(
            f"分析{platform}平台市场",
            f"发现{len(analysis_result['high_potential_categories'])}个高潜力品类"
        )
        
        self.log("市场洞察分析完成")
        
        return {
            "platform": platform,
            "raw_market_data": self.market_data.to_dict("records"),
            "analysis_result": analysis_result,
            "insight_report": insight_report,
            "high_potential_categories": analysis_result["high_potential_categories"]
        }
    
    def _analyze_market_data(self, platform: str) -> Dict[str, Any]:
        """分析市场数据"""
        df = self.market_data
        
        # 计算综合得分
        df["composite_score"] = (
            df["growth_rate"] * 0.3 +
            (1 - df["competition_score"] / 100) * 0.3 +
            df["profit_margin"] * 0.4
        )
        
        # 筛选高潜力品类
        high_potential = df[
            (df["growth_rate"] > 0.2) &
            (df["competition_score"] < 80)
        ].sort_values("composite_score", ascending=False)
        
        # 平台特定调整
        platform_factors = {
            "抖音": {"growth_weight": 1.2, "profit_weight": 1.0},
            "淘宝": {"growth_weight": 1.0, "profit_weight": 1.1},
            "拼多多": {"growth_weight": 1.0, "profit_weight": 0.8},
            "小红书": {"growth_weight": 1.3, "profit_weight": 1.2}
        }
        
        factors = platform_factors.get(platform, platform_factors["抖音"])
        
        return {
            "all_categories": df.to_dict("records"),
            "high_potential_categories": high_potential.to_dict("records"),
            "top_3_categories": high_potential.head(3)["category"].tolist(),
            "platform_factors": factors,
            "market_summary": {
                "total_categories": len(df),
                "avg_growth_rate": float(df["growth_rate"].mean()),
                "avg_competition": float(df["competition_score"].mean()),
                "avg_profit_margin": float(df["profit_margin"].mean())
            }
        }
    
    def _generate_insight_report(self, analysis_result: Dict, platform: str) -> str:
        """生成洞察报告"""
        if not self.llm:
            return self._generate_mock_report(analysis_result, platform)
        
        # 使用LLM生成报告
        prompt = PromptTemplate(
            input_variables=["platform", "analysis_data"],
            template="""你是一位资深电商分析师。基于以下数据，为{platform}平台生成一份专业的市场洞察报告。

数据分析结果：
{analysis_data}

请生成一份结构清晰、见解深刻的报告，包含：
1. 市场概览
2. 高潜力品类分析
3. 竞争格局分析
4. 具体建议与切入点

报告要求专业、简洁、有数据支撑。"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            platform=platform,
            analysis_data=str(analysis_result)
        )
    
    def _generate_mock_report(self, analysis_result: Dict, platform: str) -> str:
        """生成模拟报告（无LLM时使用）"""
        top_cats = analysis_result["top_3_categories"]
        summary = analysis_result["market_summary"]
        
        return f"""
【{platform}平台市场洞察报告】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 市场概览
   • 监测品类：{summary['total_categories']}个
   • 平均增长率：{summary['avg_growth_rate']:.1%}
   • 平均竞争度：{summary['avg_competition']:.1f}分
   • 平均利润率：{summary['avg_profit_margin']:.1%}

2. 高潜力品类TOP3
   🏆 {top_cats[0]} - 综合表现最佳
   🥈 {top_cats[1]} - 增长势头强劲
   🥉 {top_cats[2]} - 利润空间可观

3. 竞争格局分析
   市场呈现"结构性机会"特征，头部品类竞争激烈，但细分赛道仍有空白。
   建议避开竞争度>80分的红海品类。

4. 具体建议
   ✓ 切入点：聚焦{top_cats[0]}赛道的细分场景
   ✓ 策略：差异化定位，主打功能创新
   ✓ 定价：利用高利润率特性，采取中端定价策略

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
