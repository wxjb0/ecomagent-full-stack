import pandas as pd
from typing import Dict, Any, List, Optional
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent
from data.mock_data import get_product_candidates

class ProductSelectionAgent(BaseAgent):
    """选品策略Agent - 基于市场洞察生成选品方案"""
    
    def __init__(self, llm: Optional[BaseLLM] = None, memory=None):
        super().__init__(llm, memory, agent_name="ProductSelectionAgent")
        
    def run(self, market_insight: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行选品策略生成
        
        Args:
            market_insight: 市场洞察Agent的输出结果
            
        Returns:
            包含选品方案的字典
        """
        self.log("开始生成选品策略...")
        
        # 1. 获取候选产品
        target_categories = market_insight.get("high_potential_categories", [])
        product_candidates = get_product_candidates(target_categories)
        
        # 2. 产品筛选与评分
        selected_products = self._score_and_select_products(
            product_candidates,
            market_insight
        )
        
        # 3. 生成定价策略
        pricing_strategy = self._generate_pricing_strategy(selected_products)
        
        # 4. 生成选品报告
        selection_report = self._generate_selection_report(
            selected_products,
            pricing_strategy,
            market_insight
        )
        
        # 5. 保存到记忆
        self.save_to_memory(
            f"基于{len(target_categories)}个品类选品",
            f"选定了{len(selected_products)}个产品"
        )
        
        self.log(f"选品策略生成完成，选定{len(selected_products)}个产品")
        
        return {
            "selected_products": selected_products,
            "all_candidates": product_candidates,
            "pricing_strategy": pricing_strategy,
            "selection_report": selection_report,
            "target_categories": [c["category"] for c in target_categories[:3]]
        }
    
    def _score_and_select_products(
        self,
        candidates: List[Dict],
        market_insight: Dict
    ) -> List[Dict]:
        """对候选产品进行评分和筛选"""
        df = pd.DataFrame(candidates)
        
        # 计算产品综合得分
        df["score"] = (
            df["profit_potential"] * 0.35 +
            df["demand_score"] * 0.30 +
            df["competition_score"] * 0.20 +
            df["operational_ease"] * 0.15
        )
        
        # 筛选高分产品
        selected = df[df["score"] >= 70].sort_values("score", ascending=False)
        
        # 为每个产品生成详细信息
        result = []
        for _, row in selected.head(5).iterrows():  # 最多选5个
            product = {
                "product_id": f"P{str(len(result)+1).zfill(3)}",
                "name": row["product_name"],
                "category": row["category"],
                "cost_price": float(row["cost_price"]),
                "suggested_price": float(row["cost_price"] * (1 + row["profit_potential"]/100)),
                "profit_margin": float(row["profit_potential"]),
                "score": float(row["score"]),
                "keywords": row["keywords"].split(","),
                "features": row["key_features"].split(","),
                "target_audience": row["target_audience"],
                "seasonality": row["seasonality"],
                "supply_chain_risk": row["supply_chain_risk"]
            }
            result.append(product)
        
        return result
    
    def _generate_pricing_strategy(self, products: List[Dict]) -> Dict[str, Any]:
        """生成定价策略"""
        if not products:
            return {}
        
        # 价格带分析
        prices = [p["suggested_price"] for p in products]
        costs = [p["cost_price"] for p in products]
        
        return {
            "price_range": {
                "min": min(prices),
                "max": max(prices),
                "avg": sum(prices) / len(prices)
            },
            "pricing_method": "成本加成定价法",
            "target_gross_margin": "55%-65%",
            "discount_strategy": {
                "launch_discount": "首周9折",
                "bundle_discount": "第二件8折",
                "vip_discount": "会员专享95折"
            },
            "competitive_positioning": "中端偏高，强调品质"
        }
    
    def _generate_selection_report(
        self,
        products: List[Dict],
        pricing: Dict,
        market_insight: Dict
    ) -> str:
        """生成选品报告"""
        if not self.llm:
            return self._generate_mock_report(products, pricing)
        
        prompt = PromptTemplate(
            input_variables=["products", "pricing", "market_insight"],
            template="""基于以下信息生成一份专业的选品策略报告：

选定产品：
{products}

定价策略：
{pricing}

市场洞察：
{market_insight}

请生成一份结构清晰的选品报告。"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(
            products=str([p["name"] for p in products]),
            pricing=str(pricing),
            market_insight=str(market_insight.get("high_potential_categories", []))
        )
    
    def _generate_mock_report(self, products: List[Dict], pricing: Dict) -> str:
        """生成模拟报告"""
        product_list = "\n   ".join([
            f"• {p['name']} (¥{p['suggested_price']:.0f}, 评分{p['score']:.1f})"
            for p in products
        ])
        
        return f"""
【选品策略报告】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

选定产品清单：
   {product_list}

定价策略：
   • 方法：{pricing['pricing_method']}
   • 目标毛利率：{pricing['target_gross_margin']}
   • 价格带：¥{pricing['price_range']['min']:.0f} - ¥{pricing['price_range']['max']:.0f}

选品逻辑：
   1. 优先选择高利润、低竞争的细分品类
   2. 确保产品有明确的差异化卖点
   3. 考虑供应链稳定性与季节性因素
   4. 预留足够的营销费用空间

库存建议：
   • 首批备货：按预计月销量的1.5倍准备
   • 安全库存：保持2周销量的安全库存
   • 补货周期：设置7-10天的补货预警

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
