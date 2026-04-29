"""
模拟数据模块 - 提供测试数据，无需真实电商数据即可体验系统
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta

def get_market_data() -> pd.DataFrame:
    """获取市场数据"""
    categories = [
        "智能家居", "数码配件", "美妆护肤", "厨房用品", "宠物用品",
        "运动户外", "母婴用品", "办公文具", "汽车用品", "食品饮料"
    ]
    
    data = {
        "category": categories,
        "growth_rate": [0.35, 0.28, 0.42, 0.31, 0.55, 0.25, 0.38, 0.18, 0.22, 0.15],
        "market_size": [850, 420, 680, 350, 280, 520, 450, 180, 320, 890],
        "competition_score": [75, 60, 85, 55, 45, 70, 80, 50, 65, 90],
        "profit_margin": [0.45, 0.35, 0.55, 0.40, 0.50, 0.38, 0.42, 0.48, 0.32, 0.25]
    }
    
    return pd.DataFrame(data)

def get_product_candidates(target_categories: List[Dict] = None) -> List[Dict]:
    """获取候选产品"""
    candidates = [
        {
            "product_name": "智能感应垃圾桶",
            "category": "智能家居",
            "cost_price": 45.0,
            "profit_potential": 65.0,
            "demand_score": 78.0,
            "competition_score": 55.0,
            "operational_ease": 85.0,
            "keywords": "智能,感应,垃圾桶,自动,家用",
            "key_features": "自动感应开盖,静音设计,大容量,防异味",
            "target_audience": "年轻家庭,注重生活品质的人群",
            "seasonality": "全年",
            "supply_chain_risk": "低"
        },
        {
            "product_name": "便携无线充电宝",
            "category": "数码配件",
            "cost_price": 35.0,
            "profit_potential": 55.0,
            "demand_score": 82.0,
            "competition_score": 70.0,
            "operational_ease": 80.0,
            "keywords": "充电宝,无线,便携,快充,移动电源",
            "key_features": "无线快充,轻薄便携,多口输出,安全保护",
            "target_audience": "商务人士,学生,户外爱好者",
            "seasonality": "全年",
            "supply_chain_risk": "中"
        },
        {
            "product_name": "玻尿酸补水面膜",
            "category": "美妆护肤",
            "cost_price": 12.0,
            "profit_potential": 75.0,
            "demand_score": 88.0,
            "competition_score": 80.0,
            "operational_ease": 75.0,
            "keywords": "面膜,玻尿酸,补水,保湿,护肤",
            "key_features": "深层补水,温和配方,贴合度高,性价比高",
            "target_audience": "18-35岁女性,护肤爱好者",
            "seasonality": "全年,冬季更旺",
            "supply_chain_risk": "低"
        },
        {
            "product_name": "多功能切菜神器",
            "category": "厨房用品",
            "cost_price": 25.0,
            "profit_potential": 60.0,
            "demand_score": 72.0,
            "competition_score": 50.0,
            "operational_ease": 88.0,
            "keywords": "切菜器,厨房,多功能,切丝,切片",
            "key_features": "多种刀头,安全护手,易清洗,节省时间",
            "target_audience": "家庭主妇,烹饪爱好者,厨房新手",
            "seasonality": "全年",
            "supply_chain_risk": "低"
        },
        {
            "product_name": "宠物自动喂食器",
            "category": "宠物用品",
            "cost_price": 85.0,
            "profit_potential": 58.0,
            "demand_score": 75.0,
            "competition_score": 45.0,
            "operational_ease": 70.0,
            "keywords": "宠物,喂食器,自动,定时,智能",
            "key_features": "定时定量,远程控制,保鲜设计,大容量",
            "target_audience": "养宠人群,上班族,经常出差者",
            "seasonality": "全年,节假日需求高",
            "supply_chain_risk": "中"
        },
        {
            "product_name": "瑜伽弹力带套装",
            "category": "运动户外",
            "cost_price": 18.0,
            "profit_potential": 70.0,
            "demand_score": 68.0,
            "competition_score": 60.0,
            "operational_ease": 90.0,
            "keywords": "瑜伽,弹力带,健身,家用,运动",
            "key_features": "多阻力等级,环保材质,便携收纳,附送教程",
            "target_audience": "健身爱好者,瑜伽练习者,康复训练者",
            "seasonality": "春季夏季较旺",
            "supply_chain_risk": "低"
        },
        {
            "product_name": "婴儿辅食研磨碗",
            "category": "母婴用品",
            "cost_price": 28.0,
            "profit_potential": 62.0,
            "demand_score": 70.0,
            "competition_score": 55.0,
            "operational_ease": 85.0,
            "keywords": "婴儿,辅食,研磨碗,喂食,餐具",
            "key_features": "食品级材质,多功能研磨,易清洗,便携设计",
            "target_audience": "0-3岁婴幼儿父母",
            "seasonality": "全年",
            "supply_chain_risk": "低"
        },
        {
            "product_name": "桌面收纳整理盒",
            "category": "办公文具",
            "cost_price": 15.0,
            "profit_potential": 68.0,
            "demand_score": 65.0,
            "competition_score": 65.0,
            "operational_ease": 92.0,
            "keywords": "收纳,整理,桌面,办公,文具",
            "key_features": "分格设计,可叠加,透明可视,耐用材质",
            "target_audience": "上班族,学生,整理爱好者",
            "seasonality": "开学季,年初需求高",
            "supply_chain_risk": "低"
        }
    ]
    
    return candidates

def get_ad_performance_data() -> pd.DataFrame:
    """获取广告表现数据"""
    plans = ["Plan_A", "Plan_B", "Plan_C", "Plan_D", "Plan_E"]
    products = ["智能感应垃圾桶", "便携无线充电宝", "玻尿酸补水面膜", "多功能切菜神器", "宠物自动喂食器"]
    
    data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(100):
        plan = np.random.choice(plans)
        product = np.random.choice(products)
        
        impressions = np.random.randint(1000, 50000)
        ctr = np.random.uniform(0.01, 0.10)
        clicks = int(impressions * ctr)
        cpc = np.random.uniform(0.5, 3.0)
        cost = clicks * cpc
        conversion_rate = np.random.uniform(0.01, 0.05)
        conversions = int(clicks * conversion_rate)
        aov = np.random.uniform(50, 200)
        revenue = conversions * aov
        roi = revenue / cost if cost > 0 else 0
        
        data.append({
            "date": (base_date + timedelta(days=i % 30)).strftime("%Y-%m-%d"),
            "plan_id": plan,
            "product": product,
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round(ctr, 4),
            "cpc": round(cpc, 2),
            "cost": round(cost, 2),
            "conversions": conversions,
            "conversion_rate": round(conversion_rate, 4),
            "revenue": round(revenue, 2),
            "roi": round(roi, 2)
        })
    
    return pd.DataFrame(data)

def get_customer_reviews() -> List[Dict]:
    """获取客户评论数据"""
    reviews = [
        {
            "review_id": "R001",
            "product": "智能感应垃圾桶",
            "text": "太好用了！感应很灵敏，盖子开关很顺滑，家里人都很喜欢",
            "sentiment": "positive",
            "rating": 5,
            "issue": None
        },
        {
            "review_id": "R002",
            "product": "智能感应垃圾桶",
            "text": "物流太慢了，等了快一周才到，不过产品本身还可以",
            "sentiment": "neutral",
            "rating": 3,
            "issue": "物流慢"
        },
        {
            "review_id": "R003",
            "product": "便携无线充电宝",
            "text": "充电速度很快，但是用了两天就充不进电了，质量有问题",
            "sentiment": "negative",
            "rating": 2,
            "issue": "质量问题"
        },
        {
            "review_id": "R004",
            "product": "玻尿酸补水面膜",
            "text": "补水效果很好，用完皮肤很水润，会回购的",
            "sentiment": "positive",
            "rating": 5,
            "issue": None
        },
        {
            "review_id": "R005",
            "product": "多功能切菜神器",
            "text": "切丝切片都很方便，清洗也很简单，推荐购买",
            "sentiment": "positive",
            "rating": 5,
            "issue": None
        },
        {
            "review_id": "R006",
            "product": "宠物自动喂食器",
            "text": "设置有点复杂，说明书不够详细，研究了很久才会用",
            "sentiment": "neutral",
            "rating": 3,
            "issue": "使用复杂"
        },
        {
            "review_id": "R007",
            "product": "瑜伽弹力带套装",
            "text": "性价比高，质量很好，还送了使用教程，新手很适用",
            "sentiment": "positive",
            "rating": 5,
            "issue": None
        },
        {
            "review_id": "R008",
            "product": "婴儿辅食研磨碗",
            "text": "给宝宝的辅食工具，材质安全放心，研磨细腻",
            "sentiment": "positive",
            "rating": 5,
            "issue": None
        },
        {
            "review_id": "R009",
            "product": "桌面收纳整理盒",
            "text": "大小合适，桌面整洁多了，办公效率都提高了",
            "sentiment": "positive",
            "rating": 4,
            "issue": None
        },
        {
            "review_id": "R010",
            "product": "便携无线充电宝",
            "text": "客服态度太差了，问个问题半天不回，体验很不好",
            "sentiment": "negative",
            "rating": 1,
            "issue": "客服态度"
        },
        {
            "review_id": "R011",
            "product": "智能感应垃圾桶",
            "text": "感应距离有点短，要离很近才会开盖，不太方便",
            "sentiment": "neutral",
            "rating": 3,
            "issue": "功能问题"
        },
        {
            "review_id": "R012",
            "product": "玻尿酸补水面膜",
            "text": "价格有点贵，但是效果确实不错，一周用两次",
            "sentiment": "positive",
            "rating": 4,
            "issue": None
        },
        {
            "review_id": "R013",
            "product": "宠物自动喂食器",
            "text": "容量够大，出差一周也不用担心猫饿着了，很实用",
            "sentiment": "positive",
            "rating": 5,
            "issue": None
        },
        {
            "review_id": "R014",
            "product": "多功能切菜神器",
            "text": "刀片很锋利，但是不小心割到手了，大家使用要小心",
            "sentiment": "neutral",
            "rating": 4,
            "issue": "安全风险"
        },
        {
            "review_id": "R015",
            "product": "瑜伽弹力带套装",
            "text": "弹力刚刚好，不会断裂，用完收纳也方便",
            "sentiment": "positive",
            "rating": 5,
            "issue": None
        }
    ]
    
    return reviews
