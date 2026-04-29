import streamlit as st
import pandas as pd
import time
from config.settings import get_settings
from core.coordinator import EcommerceAgentCoordinator
from utils.llm_factory import LLMFactory

# 页面配置
st.set_page_config(
    page_title="电商全链路多Agent智能体系统",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化配置
settings = get_settings()

# 页面标题
st.title("🛒 电商全链路多Agent智能体系统")
st.markdown("---")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    # 平台选择
    platform = st.selectbox(
        "选择电商平台",
        ["抖音", "淘宝", "拼多多", "小红书"],
        index=0
    )
    
    # LLM配置
    st.subheader("🤖 LLM配置")
    use_llm = st.checkbox("启用真实LLM (需要API Key)", value=False)
    
    if use_llm:
        llm_provider = st.selectbox(
            "选择LLM提供商",
            ["openai", "anthropic"],
            index=0
        )
        
        api_key = st.text_input(
            "API Key",
            type="password",
            value=settings.OPENAI_API_KEY or ""
        )
        
        if api_key:
            import os
            os.environ[f"{llm_provider.upper()}_API_KEY"] = api_key
    else:
        llm_provider = "mock"
    
    st.markdown("---")
    
    # 运行按钮
    run_button = st.button(
        "🚀 启动全链路分析",
        type="primary",
        use_container_width=True
    )
    
    # 重置按钮
    reset_button = st.button(
        "🔄 重置系统",
        use_container_width=True
    )
    
    st.markdown("---")
    st.info("💡 提示：首次使用建议先不启用LLM，体验完整流程")

# 初始化Session State
if "coordinator" not in st.session_state:
    st.session_state.coordinator = None
if "result" not in st.session_state:
    st.session_state.result = None
if "execution_history" not in st.session_state:
    st.session_state.execution_history = []

# 重置系统
if reset_button:
    st.session_state.coordinator = None
    st.session_state.result = None
    st.success("✅ 系统已重置")
    time.sleep(0.5)
    st.rerun()

# 主程序逻辑
if run_button:
    # 创建协调器
    if not st.session_state.coordinator:
        llm = None
        if use_llm:
            try:
                llm = LLMFactory.create_llm(provider=llm_provider)
                st.success(f"✅ 成功加载{llm_provider}模型")
            except Exception as e:
                st.error(f"❌ 加载LLM失败: {str(e)}")
                st.info("将使用模拟模式运行")
        
        st.session_state.coordinator = EcommerceAgentCoordinator(llm=llm)
    
    coordinator = st.session_state.coordinator
    
    # 进度显示
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 回调函数更新进度
    def progress_callback(agent_name: str, current: int, total: int):
        progress = current / total
        progress_bar.progress(progress)
        
        agent_names = {
            "market": "📊 市场洞察",
            "product": "🛒 选品策略",
            "content": "✍️ 内容创作",
            "ad": "📈 投放优化",
            "after_sales": "💬 售后舆情"
        }
        
        status_text.text(f"正在执行: {agent_names.get(agent_name, agent_name)} ({current}/{total})")
    
    # 运行工作流
    try:
        with st.spinner("Agent们正在努力工作中..."):
            result = coordinator.run_full_workflow(
                platform=platform,
                callback=progress_callback
            )
        
        st.session_state.result = result
        
        # 保存到历史
        st.session_state.execution_history.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "platform": platform,
            "result": result
        })
        
        progress_bar.progress(1.0)
        status_text.text("✅ 执行完成！")
        
        time.sleep(0.5)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 执行出错: {str(e)}")
        st.exception(e)

# 显示结果
if st.session_state.result:
    result = st.session_state.result
    
    # 顶部摘要
    st.header("📊 执行概览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "执行时间",
            f"{result['execution_info']['execution_time_seconds']}秒"
        )
    
    kpis = result['summary_kpis']['performance_improvement']
    
    with col2:
        st.metric(
            "预期ROI提升",
            kpis['estimated_roi_improvement']
        )
    
    with col3:
        st.metric(
            "预期成本降低",
            kpis['estimated_cost_reduction']
        )
    
    with col4:
        st.metric(
            "平台",
            result['platform']
        )
    
    st.markdown("---")
    
    # 分Tab展示详细结果
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 执行摘要",
        "📊 市场洞察",
        "🛒 选品方案",
        "✍️ 内容创作",
        "📈 投放优化",
        "💬 售后舆情"
    ])
    
    # Tab 1: 执行摘要
    with tab1:
        st.subheader("📋 执行摘要")
        
        st.info(result['executive_summary'])
        
        st.subheader("⏱️ 执行信息")
        exec_info = result['execution_info']
        st.write(f"**开始时间**: {exec_info['start_time']}")
        st.write(f"**结束时间**: {exec_info['end_time']}")
        st.write(f"**执行Agent**: {', '.join(exec_info['agents_executed'])}")
        
        st.subheader("📝 执行日志")
        log_df = pd.DataFrame(result['execution_log'])
        st.dataframe(log_df, use_container_width=True)
    
    # Tab 2: 市场洞察
    with tab2:
        st.subheader("📊 市场洞察分析")
        
        market = result['results']['market_insight']
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 市场数据")
            market_df = pd.DataFrame(market['raw_market_data'])
            st.dataframe(market_df, use_container_width=True)
        
        with col2:
            st.markdown("### 高潜力品类")
            high_potential = pd.DataFrame(market['high_potential_categories'])
            if not high_potential.empty:
                st.dataframe(high_potential[['category', 'growth_rate', 'competition_score', 'profit_margin']], 
                           use_container_width=True)
        
        st.markdown("### 📝 洞察报告")
        st.markdown(market['insight_report'])
    
    # Tab 3: 选品方案
    with tab3:
        st.subheader("🛒 选品策略")
        
        product = result['results']['product_selection']
        
        st.markdown("### 选定产品")
        products_df = pd.DataFrame(product['selected_products'])
        if not products_df.empty:
            display_cols = ['product_id', 'name', 'category', 'cost_price', 'suggested_price', 'score']
            st.dataframe(products_df[display_cols], use_container_width=True)
        
        st.markdown("### 💰 定价策略")
        st.json(product['pricing_strategy'])
        
        st.markdown("### 📝 选品报告")
        st.markdown(product['selection_report'])
    
    # Tab 4: 内容创作
    with tab4:
        st.subheader("✍️ 内容创作矩阵")
        
        content = result['results']['content_creation']
        content_matrix = content['content_matrix']
        
        for product_name, product_content in content_matrix.items():
            with st.expander(f"📦 {product_name}"):
                platform_tabs = st.tabs(["抖音", "淘宝", "小红书", "快手"])
                
                with platform_tabs[0]:
                    st.markdown("### 抖音短视频脚本")
                    st.text(product_content['douyin']['video_script'])
                
                with platform_tabs[1]:
                    st.markdown("### 淘宝内容")
                    st.write(f"**标题**: {product_content['taobao']['title']}")
                    st.markdown(product_content['taobao']['description'])
                
                with platform_tabs[2]:
                    st.markdown("### 小红书笔记")
                    st.write(f"**标题**: {product_content['xiaohongshu']['note_title']}")
                    st.markdown(product_content['xiaohongshu']['note_content'])
                
                with platform_tabs[3]:
                    st.markdown("### 快手内容")
                    st.text(product_content['kuaishou']['live_script'])
    
    # Tab 5: 投放优化
    with tab5:
        st.subheader("📈 广告投放优化")
        
        ad = result['results']['ad_optimization']
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 广告表现数据")
            ad_df = pd.DataFrame(ad['ad_performance_data'])
            st.dataframe(ad_df, use_container_width=True)
        
        with col2:
            st.markdown("### 预期提升")
            expected = ad['expected_improvement']
            for metric, improvement in expected.items():
                st.metric(metric.upper(), improvement)
        
        st.markdown("### 🎯 优化建议")
        for i, opt in enumerate(ad['optimization_actions'], 1):
            with st.expander(f"建议 {i}: {opt['action']} ({opt['priority'].upper()})"):
                st.write(f"**详情**: {opt['details']}")
                st.write(f"**预期影响**: {opt['expected_impact']}")
        
        st.markdown("### 📅 媒体投放计划")
        st.json(ad['media_plan'])
        
        st.markdown("### 📝 优化报告")
        st.markdown(ad['optimization_report'])
    
    # Tab 6: 售后舆情
    with tab6:
        st.subheader("💬 售后舆情分析")
        
        after_sales = result['results']['after_sales']
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 情感分析概览")
            sentiment = after_sales['sentiment_analysis']['overall']
            st.metric("好评率", f"{sentiment['positive_rate']:.1%}")
            st.metric("差评率", f"{sentiment['negative_rate']:.1%}")
            st.metric("预警等级", after_sales['sentiment_analysis']['alert_level'].upper())
        
        with col2:
            st.markdown("### 主要问题")
            issues = after_sales['issue_analysis']['main_issues']
            for issue, count in issues:
                st.write(f"• {issue} ({count}条)")
        
        st.markdown("### 📝 客户评论")
        reviews_df = pd.DataFrame(after_sales['reviews'])
        st.dataframe(reviews_df, use_container_width=True)
        
        st.markdown("### ✅ 解决方案")
        for sol in after_sales['solutions']:
            if sol.get('type') == 'individual_response':
                with st.expander(f"回复评论: {sol['review_text'][:50]}..."):
                    st.write(f"**优先级**: {sol['priority']}")
                    st.markdown(sol['response'])
            else:
                with st.expander(f"系统方案: {sol.get('action', sol['issue'])}"):
                    st.write(f"**问题**: {sol.get('issue', 'N/A')}")
                    st.write(f"**详情**: {sol.get('details', 'N/A')}")
        
        st.markdown("### 🔄 产品迭代建议")
        for sug in after_sales['product_suggestions']:
            st.write(f"• **{sug['area']}**: {sug['suggestion']} ({sug['priority'].upper()})")
        
        st.markdown("### 📝 舆情报告")
        st.markdown(after_sales['report'])

else:
    # 欢迎界面
    st.markdown("""
    ## 👋 欢迎使用电商全链路多Agent智能体系统
    
    本系统集成了5个专业Agent，为您提供完整的电商运营解决方案：
    
    1. **📊 市场洞察Agent** - 分析市场趋势，识别高潜力品类
    2. **🛒 选品策略Agent** - 基于市场数据，制定最优选品方案
    3. **✍️ 内容创作Agent** - 生成多平台营销内容（抖音/淘宝/小红书/快手）
    4. **📈 投放优化Agent** - 优化广告投放策略，提升ROI
    5. **💬 售后舆情Agent** - 监测售后舆情，生成解决方案
    
    ### 🚀 快速开始
    
    1. 在左侧选择目标电商平台
    2. （可选）配置LLM以获得更智能的分析
    3. 点击"启动全链路分析"按钮
    4. 等待系统完成分析，查看详细结果
    
    ### 💡 使用提示
    
    - 首次使用建议先不启用LLM，快速体验完整流程
    - 系统内置模拟数据，无需真实电商数据即可体验
    - 支持抖音、淘宝、拼多多、小红书多个平台
    """)
    
    # 展示系统架构图
    st.markdown("---")
    st.subheader("🏗️ 系统架构")
    
    st.info("""
    **多Agent协作流程**:
    
    市场洞察 → 选品策略 → 内容创作 → 投放优化 → 售后舆情
    
    每个Agent都可以独立运行，也可以协同工作，形成完整的电商运营闭环。
    """)
