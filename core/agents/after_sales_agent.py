import pandas as pd
from typing import Dict, Any, List, Optional
from collections import Counter
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent
from data.mock_data import get_customer_reviews

class AfterSalesAgent(BaseAgent):
    """售后舆情Agent - 处理售后问题与舆情分析"""
    
    def __init__(self, llm: Optional[BaseLLM] = None, memory=None):
        super().__init__(llm, memory, agent_name="AfterSalesAgent")
        
    def run(self, ad_optimization: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行售后舆情分析
        
        Args:
            ad_optimization: 投放优化Agent的输出
            
        Returns:
            包含售后舆情分析结果的字典
        """
        self.log("开始售后舆情分析...")
        
        # 1. 获取评论数据
        reviews = get_customer_reviews()
        
        # 2. 情感分析
        sentiment_analysis = self._analyze_sentiment(reviews)
        
        # 3. 问题分类
        issue_analysis = self._classify_issues(reviews)
        
        # 4. 生成解决方案
        solutions = self._generate_solutions(issue_analysis, reviews)
        
        # 5. 产品迭代建议
        product_suggestions = self._generate_product_suggestions(issue_analysis)
        
        # 6. 生成舆情报告
        report = self._generate_report(
            sentiment_analysis,
            issue_analysis,
            solutions,
            product_suggestions
        )
        
        self.save_to_memory(
            "分析售后舆情",
            f"处理了{len(reviews)}条评论，发现{len(issue_analysis['main_issues'])}个主要问题"
        )
        
        self.log("售后舆情分析完成")
        
        return {
            "reviews": reviews,
            "sentiment_analysis": sentiment_analysis,
            "issue_analysis": issue_analysis,
            "solutions": solutions,
            "product_suggestions": product_suggestions,
            "report": report,
            "response_templates": self._generate_response_templates()
        }
    
    def _analyze_sentiment(self, reviews: List[Dict]) -> Dict[str, Any]:
        """情感分析"""
        df = pd.DataFrame(reviews)
        
        # 统计情感分布
        sentiment_counts = df["sentiment"].value_counts().to_dict()
        total = len(reviews)
        
        # 计算情感分数
        sentiment_score_map = {"positive": 1, "neutral": 0, "negative": -1}
        df["sentiment_score"] = df["sentiment"].map(sentiment_score_map)
        
        # 按产品分析
        product_sentiment = df.groupby("product")["sentiment_score"].agg([
            "count", "mean"
        ]).reset_index()
        product_sentiment.columns = ["product", "review_count", "avg_sentiment"]
        
        return {
            "overall": {
                "total_reviews": total,
                "positive_count": sentiment_counts.get("positive", 0),
                "neutral_count": sentiment_counts.get("neutral", 0),
                "negative_count": sentiment_counts.get("negative", 0),
                "positive_rate": sentiment_counts.get("positive", 0) / total,
                "negative_rate": sentiment_counts.get("negative", 0) / total,
                "overall_sentiment_score": float(df["sentiment_score"].mean())
            },
            "by_product": product_sentiment.to_dict("records"),
            "trend": "improving" if sentiment_counts.get("positive", 0) > sentiment_counts.get("negative", 0) * 2 else "needs_attention",
            "alert_level": "low" if sentiment_counts.get("negative", 0) / total < 0.1 else "medium" if sentiment_counts.get("negative", 0) / total < 0.2 else "high"
        }
    
    def _classify_issues(self, reviews: List[Dict]) -> Dict[str, Any]:
        """问题分类"""
        issues = []
        for review in reviews:
            if review.get("issue"):
                issues.append(review["issue"])
        
        # 统计问题频率
        issue_counter = Counter(issues)
        
        # 分类问题
        issue_categories = {
            "物流问题": ["物流", "快递", "发货", "配送", "慢"],
            "质量问题": ["质量", "坏的", "破损", "故障", "不能用"],
            "服务问题": ["客服", "服务", "态度", "售后", "不理"],
            "产品问题": ["产品", "功能", "效果", "不好用", "失望"],
            "价格问题": ["价格", "贵", "不值", "降价", "优惠"]
        }
        
        categorized_issues = {}
        for category, keywords in issue_categories.items():
            categorized_issues[category] = [
                issue for issue in issues
                if any(keyword in issue for keyword in keywords)
            ]
        
        return {
            "main_issues": issue_counter.most_common(5),
            "total_issues_count": len(issues),
            "issue_rate": len(issues) / len(reviews),
            "categorized_issues": {
                cat: len(issues) for cat, issues in categorized_issues.items()
            },
            "top_issue_category": max(
                categorized_issues.items(),
                key=lambda x: len(x[1])
            )[0] if issues else "无"
        }
    
    def _generate_solutions(
        self,
        issue_analysis: Dict,
        reviews: List[Dict]
    ) -> List[Dict]:
        """生成解决方案"""
        solutions = []
        
        # 为主要问题生成解决方案
        for issue, count in issue_analysis["main_issues"]:
            solution = self._get_solution_for_issue(issue, count)
            solutions.append(solution)
        
        # 为负面评论生成具体回复
        negative_reviews = [r for r in reviews if r["sentiment"] == "negative"]
        for review in negative_reviews[:3]:  # 只处理前3条
            solutions.append({
                "type": "individual_response",
                "review_id": review.get("review_id", "unknown"),
                "review_text": review["text"],
                "response": self._generate_personalized_response(review),
                "priority": "high" if review.get("issue") else "medium"
            })
        
        return solutions
    
    def _get_solution_for_issue(self, issue: str, count: int) -> Dict:
        """获取特定问题的解决方案"""
        solution_templates = {
            "物流": {
                "action": "优化物流配送",
                "details": "联系物流公司，协商改善配送时效；考虑增加备用物流商",
                "prevention": "在详情页明确说明发货时效，设置合理预期"
            },
            "质量": {
                "action": "加强质量管控",
                "details": "增加出库前质检环节，改进包装防止运输破损",
                "prevention": "为质量问题客户提供优先退换货服务"
            },
            "客服": {
                "action": "提升客服服务质量",
                "details": "加强客服培训，建立快速响应机制（30分钟内回复）",
                "prevention": "设置客服满意度评价，与绩效挂钩"
            }
        }
        
        # 匹配问题类型
        for key, template in solution_templates.items():
            if key in issue:
                return {
                    "type": "systemic_solution",
                    "issue": issue,
                    "affected_count": count,
                    **template,
                    "priority": "high" if count > 5 else "medium"
                }
        
        # 默认解决方案
        return {
            "type": "general_solution",
            "issue": issue,
            "affected_count": count,
            "action": "调查并改进",
            "details": f"针对'{issue}'问题进行深入调查，制定改进方案",
            "priority": "medium"
        }
    
    def _generate_personalized_response(self, review: Dict) -> str:
        """生成个性化回复"""
        product = review.get("product", "您购买的产品")
        
        return f"""
亲，非常抱歉给您带来了不好的体验！

关于您反馈的问题，我们非常重视。请您私信我们的客服，提供订单号，我们会立即为您处理：
• 如需退换货，我们会为您安排上门取件
• 如有质量问题，我们会为您优先补发
• 我们会认真听取您的建议，持续改进

再次向您致以诚挚的歉意！
        """.strip()
    
    def _generate_product_suggestions(self, issue_analysis: Dict) -> List[Dict]:
        """生成产品迭代建议"""
        suggestions = []
        
        main_issue = issue_analysis["top_issue_category"]
        
        if main_issue == "质量问题":
            suggestions.append({
                "area": "产品质量",
                "suggestion": "优化生产工艺，加强质量检测",
                "priority": "high",
                "expected_impact": "减少质量相关负面评价60%"
            })
        elif main_issue == "物流问题":
            suggestions.append({
                "area": "包装与物流",
                "suggestion": "改进包装设计，选择更可靠的物流合作伙伴",
                "priority": "high",
                "expected_impact": "减少物流破损率70%"
            })
        
        # 通用建议
        suggestions.extend([
            {
                "area": "用户体验",
                "suggestion": "优化产品说明书，增加使用视频教程",
                "priority": "medium",
                "expected_impact": "提升用户满意度"
            },
            {
                "area": "售后服务",
                "suggestion": "建立主动回访机制，及时发现并解决问题",
                "priority": "medium",
                "expected_impact": "提升品牌好感度"
            }
        ])
        
        return suggestions
    
    def _generate_response_templates(self) -> Dict[str, str]:
        """生成回复模板"""
        return {
            "positive": """
亲，感谢您的好评！很高兴您喜欢我们的产品！
您的满意是我们最大的动力，期待再次为您服务！❤️
            """.strip(),
            
            "neutral": """
亲，感谢您的反馈！我们会继续努力改进，
争取为您带来更好的体验！
            """.strip(),
            
            "negative": """
亲，非常抱歉给您带来不好的体验！
请您私信我们，我们会立即为您处理解决！
            """.strip(),
            
            "logistics_issue": """
亲，关于物流问题我们非常抱歉！
我们已联系物流公司加急处理，
同时为您申请了一张5元优惠券作为补偿！
            """.strip()
        }
    
    def _generate_report(
        self,
        sentiment: Dict,
        issues: Dict,
        solutions: List[Dict],
        product_suggestions: List[Dict]
    ) -> str:
        """生成舆情报告"""
        overall = sentiment["overall"]
        
        return f"""
【售后舆情分析报告】
━━━━━━━━━━━━━━━━━━━━━━━

📊 数据概览
━━━━━━━━━━━━━━━━━━━━━━━
• 总评论数：{overall['total_reviews']}条
• 好评率：{overall['positive_rate']:.1%}
• 差评率：{overall['negative_rate']:.1%}
• 预警等级：{sentiment['alert_level'].upper()}

🔍 问题分析
━━━━━━━━━━━━━━━━━━━━━━━
• 主要问题类型：{issues['top_issue_category']}
• 问题发生率：{issues['issue_rate']:.1%}

⚠️ 主要问题Top5：
{chr(10).join([f"  {i+1}. {issue} ({count}条)" for i, (issue, count) in enumerate(issues['main_issues'])])}

✅ 解决方案
━━━━━━━━━━━━━━━━━━━━━━━
• 已生成解决方案：{len(solutions)}条
• 高优先级问题：{sum(1 for s in solutions if s.get('priority') == 'high')}个

🔄 产品迭代建议
━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join([f"• {s['area']}：{s['suggestion']} ({s['priority'].upper()})" for s in product_suggestions])}

📈 舆情趋势：{sentiment['trend']}
━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
