from typing import Dict, Any, List, Optional
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .base_agent import BaseAgent

class ContentCreationAgent(BaseAgent):
    """内容创作Agent - 生成多平台营销内容"""
    
    def __init__(self, llm: Optional[BaseLLM] = None, memory=None):
        super().__init__(llm, memory, agent_name="ContentCreationAgent")
        
    def run(self, selected_products: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        执行内容创作
        
        Args:
            selected_products: 选品Agent输出的产品列表
            
        Returns:
            包含多平台内容矩阵的字典
        """
        self.log(f"开始为{len(selected_products)}个产品创作内容...")
        
        content_matrix = {}
        
        for product in selected_products:
            product_name = product["name"]
            self.log(f"正在创作: {product_name}")
            
            content_matrix[product_name] = {
                "product_info": product,
                "douyin": self._create_douyin_content(product),
                "taobao": self._create_taobao_content(product),
                "xiaohongshu": self._create_xiaohongshu_content(product),
                "kuaishou": self._create_kuaishou_content(product)
            }
        
        # 生成内容策略报告
        strategy_report = self._generate_content_strategy(content_matrix)
        
        self.save_to_memory(
            f"为{len(selected_products)}个产品创作内容",
            "完成了抖音/淘宝/小红书/快手多平台内容"
        )
        
        self.log("内容创作完成")
        
        return {
            "content_matrix": content_matrix,
            "strategy_report": strategy_report,
            "platforms": ["抖音", "淘宝", "小红书", "快手"]
        }
    
    def _create_douyin_content(self, product: Dict) -> Dict[str, Any]:
        """创建抖音内容"""
        if self.llm:
            return self._create_douyin_with_llm(product)
        return self._create_douyin_mock(product)
    
    def _create_douyin_mock(self, product: Dict) -> Dict[str, Any]:
        """模拟抖音内容"""
        keywords = " ".join(product["keywords"][:3])
        
        return {
            "video_script": f"""
【抖音短视频脚本】
产品：{product['name']}

⏱️ 0-3s (钩子)
画面：痛点场景特写
台词：{self._get_pain_point(product)}
特效：大号字幕 + 惊讶表情

⏱️ 3-8s (展示)
画面：产品使用展示
台词：别担心！今天给大家推荐这款{product['name']}
特效：产品特写 + 箭头指示

⏱️ 8-15s (卖点)
画面：分屏展示{len(product['features'])}个卖点
台词：
✓ {product['features'][0]}
✓ {product['features'][1] if len(product['features'])>1 else '品质保证'}
✓ {product['features'][2] if len(product['features'])>2 else '价格实惠'}
特效：勾选动画

⏱️ 15-20s (转化)
画面：小黄车弹窗 + 价格展示
台词：今天只要¥{product['suggested_price']:.0f}！点击小黄车带回家！
特效：价格放大 + 倒计时

#话题 #{keywords} #好物推荐 #种草
            """.strip(),
            "video_length": "20-25秒",
            "suggested_music": "热门BGM - 轻快节奏",
            "hashtags": product["keywords"] + ["好物推荐", "种草"],
            "cta": "点击小黄车购买"
        }
    
    def _create_taobao_content(self, product: Dict) -> Dict[str, Any]:
        """创建淘宝内容"""
        keywords = " ".join(product["keywords"])
        
        return {
            "title": f"{product['name']} 2024新款 {keywords} 包邮",
            "short_title": f"{product['name']} {keywords}",
            "description": f"""
【宝贝描述】

✨ 产品亮点
{chr(10).join([f'• {feature}' for feature in product['features']])}

📦 产品参数
• 名称：{product['name']}
• 价格：¥{product['suggested_price']:.0f}
• 适用人群：{product['target_audience']}

💝 购买须知
• 发货时间：24小时内发货
• 运费险：赠送运费险
• 售后服务：7天无理由退换

👉 现在下单享优惠！
            """.strip(),
            "bullet_points": product["features"],
            "main_image_concept": f"产品主图：{product['name']}使用场景，突出{product['features'][0]}",
            "video_concept": "1分钟详细展示视频，包含开箱、使用、对比"
        }
    
    def _create_xiaohongshu_content(self, product: Dict) -> Dict[str, Any]:
        """创建小红书内容"""
        keywords = product["keywords"]
        
        return {
            "note_title": f"绝绝子！这个{product['name']}也太好用了吧！",
            "note_content": f"""
姐妹们！今天必须给你们安利这个宝藏好物！{product['name']}真的改变了我的生活！😭

✨ 为什么我推荐它：
{chr(10).join([f'1️⃣ {feature}' for feature in product['features']])}

💡 使用感受：
真的！用了一次就爱上了！{product['target_audience']}的姐妹一定要试试！

💰 价格也很友好：
只要¥{product['suggested_price']:.0f}！一杯奶茶钱就能提升幸福感！

👉 链接放左下角了，赶紧冲！

#{product['name'].replace(' ', '')} #{' #'.join(keywords)} #好物分享 #种草 #生活好物
            """.strip(),
            "image_suggestions": [
                "产品精美包装图",
                "使用前后对比图",
                "细节特写图",
                "使用场景图"
            ],
            "emoji_style": "活泼可爱"
        }
    
    def _create_kuaishou_content(self, product: Dict) -> Dict[str, Any]:
        """创建快手内容"""
        return {
            "live_script": f"""
【快手直播脚本片段】

家人们！看过来！今天给你们带的这款{product['name']}，真的是工厂直供价！

• 看这质量！（展示产品）
• 看这效果！（演示使用）
• 今天在我直播间，不要¥{product['suggested_price']*2:.0f}！
• 只要¥{product['suggested_price']:.0f}！
• 前100单再送赠品！

家人们，小黄车1号链接，拼手速的时候到了！
3！2！1！上链接！
            """.strip(),
            "style": "接地气、高性价比、紧迫感",
            "interaction_points": [
                "问直播间的家人们有没有同样的困扰",
                "让需要的家人扣1",
                "展示已下单数量"
            ]
        }
    
    def _create_douyin_with_llm(self, product: Dict) -> Dict[str, Any]:
        """使用LLM创建抖音内容"""
        prompt = PromptTemplate(
            input_variables=["product"],
            template="为以下产品创建一个抖音短视频脚本：{product}"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        script = chain.run(product=str(product))
        
        return {
            "video_script": script,
            "video_length": "20-30秒",
            "hashtags": product["keywords"],
            "generated_with_llm": True
        }
    
    def _generate_content_strategy(self, content_matrix: Dict) -> str:
        """生成内容策略报告"""
        return f"""
【内容营销策略报告】

内容概览：
• 覆盖产品：{len(content_matrix)}个
• 覆盖平台：抖音、淘宝、小红书、快手
• 内容形式：短视频、图文、直播、详情页

发布节奏建议：
• 抖音：每日1条，黄金时段(19-22点)发布
• 小红书：每周3篇，午间(12-14点)发布
• 淘宝：持续优化详情页，每周更新买家秀
• 快手：每周2场直播，晚间(20-23点)进行

内容测试建议：
• A/B测试不同开头钩子
• 测试不同价格展示方式
• 监测完播率、点击率、转化率
        """.strip()
    
    def _get_pain_point(self, product: Dict) -> str:
        """获取痛点文案"""
        pain_points = {
            "家居": "是不是还在为家里乱糟糟而烦恼？",
            "数码": "是不是还在因为数据线缠绕而抓狂？",
            "美妆": "是不是还在为找不到合适的化妆品而发愁？",
            "厨房": "是不是还在为做饭麻烦而头疼？"
        }
        
        category = product.get("category", "")
        for key, point in pain_points.items():
            if key in category:
                return point
        
        return "是不是还在为生活中的小麻烦而困扰？"
