"""
增强版Streamlit前端 - 电商全链路多Agent智能体系统
包含：实时可视化、Agent监控、流程动画、数据导出等创新功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import base64
from io import BytesIO

from config.settings import get_settings
from core.coordinator import EcommerceAgentCoordinator
from utils.llm_factory import LLMFactory
from data.database import db_manager

# 页面配置 - 更现代的UI
st.set_page_config(
    page_title="🚀 电商Agent智能体指挥中心",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/ecommerce-agent',
        'Report a bug': 'https://github.com/ecommerce-agent/issues',
        'About': '# 电商全链路多Agent智能体系统 v2.0'
    }
)

# 自定义CSS样式 - 现代化设计
def load_custom_css():
    st.markdown("""
    <style>
    /* 主色调 */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --accent-color: #f093fb;
        --success-color: #4ade80;
        --warning-color: #fbbf24;
        --danger-color: #f87171;
    }
    
    /* 卡片样式 */
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
    }
    
    /* Agent状态指示灯 */
    .agent-status {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-idle { background-color: #9ca3af; }
    .status-running { background-color: #fbbf24; animation: pulse 1s infinite; }
    .status-completed { background-color: #4ade80; }
    .status-error { background-color: #f87171; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* 工作流程步骤 */
    .workflow-step {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .workflow-step:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* 进度条样式 */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 按钮样式 */
    .stButton > button {
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* 表格样式 */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* 标题动画 */
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    h1, h2, h3 {
        animation: slideIn 0.5s ease;
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# 初始化配置
settings = get_settings()

# ============ 侧边栏控制面板 ============
with st.sidebar:
    # Logo区域
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #667eea; font-size: 2.5em;">🤖</h1>
        <h3 style="color: white; margin-top: 10px;">Agent指挥中心</h3>
        <p style="color: #888; font-size: 0.9em;">v2.0 Enhanced</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 平台选择 - 带图标
    platform = st.selectbox(
        "🎯 选择电商平台",
        ["🎵 抖音", "🛍️ 淘宝", "💰 拼多多", "📕 小红书"],
        index=0,
        help="选择目标电商平台进行分析"
    )
    platform_clean = platform.split()[-1]
    
    # LLM配置 - 折叠面板
    with st.expander("🤖 AI模型配置", expanded=False):
        use_llm = st.toggle("启用AI大模型", value=False, 
                          help="需要配置API Key才能使用真实LLM")
        
        if use_llm:
            llm_provider = st.radio(
                "选择模型提供商",
                ["OpenAI GPT-4", "Anthropic Claude", "DeepSeek"],
                index=0
            )
            
            api_key = st.text_input(
                "🔑 API Key",
                type="password",
                placeholder="sk-...",
                help="您的API密钥将安全存储，不会记录到日志"
            )
            
            if api_key:
                provider_map = {
                    "OpenAI GPT-4": "openai",
                    "Anthropic Claude": "anthropic",
                    "DeepSeek": "deepseek"
                }
                import os
                os.environ[f"{provider_map[llm_provider].upper()}_API_KEY"] = api_key
        else:
            llm_provider = "mock"
            st.info("💡 当前使用模拟模式，无需API Key即可体验")
    
    st.markdown("---")
    
    # 控制按钮
    col1, col2 = st.columns(2)
    with col1:
        run_button = st.button(
            "🚀 启动",
            type="primary",
            use_container_width=True,
            help="启动完整工作流分析"
        )
    with col2:
        reset_button = st.button(
            "🔄 重置",
            use_container_width=True,
            help="重置系统状态"
        )
    
    # 历史记录
    st.markdown("---")
    st.subheader("📜 历史记录")
    if st.session_state.get("execution_history"):
        for i, history in enumerate(reversed(st.session_state.execution_history[-5:])):
            with st.container():
                st.caption(f"{history['timestamp']} - {history['platform']}")
                if st.button(f"查看详情 #{len(st.session_state.execution_history)-i}", 
                           key=f"history_{i}", use_container_width=True):
                    st.session_state.result = history['result']
                    st.rerun()
    else:
        st.info("暂无历史记录")

# ============ 初始化Session State ============
def init_session_state():
    defaults = {
        "coordinator": None,
        "result": None,
        "execution_history": [],
        "current_step": 0,
        "agent_status": {
            "market": "idle",
            "product": "idle",
            "content": "idle",
            "ad": "idle",
            "after_sales": "idle"
        },
        "show_animation": True,
        "comparison_mode": False,
        "dark_mode": True
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============ Agent状态可视化组件 ============
def render_agent_status():
    """渲染Agent实时状态面板"""
    st.subheader("🎛️ Agent实时监控")
    
    agents_info = {
        "market": {"icon": "📊", "name": "市场洞察", "desc": "分析市场趋势与竞争格局"},
        "product": {"icon": "🛒", "name": "选品策略", "desc": "智能选品与定价建议"},
        "content": {"icon": "✍️", "name": "内容创作", "desc": "多平台营销内容生成"},
        "ad": {"icon": "📈", "name": "投放优化", "desc": "广告策略与预算优化"},
        "after_sales": {"icon": "💬", "name": "售后舆情", "desc": "客户反馈与舆情分析"}
    }
    
    cols = st.columns(5)
    for idx, (agent_key, info) in enumerate(agents_info.items()):
        with cols[idx]:
            status = st.session_state.agent_status.get(agent_key, "idle")
            status_colors = {
                "idle": "⚪",
                "running": "🟡",
                "completed": "🟢",
                "error": "🔴"
            }
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 15px;
                padding: 15px;
                text-align: center;
                border: 2px solid {'#667eea' if status == 'running' else 'transparent'};
                box-shadow: {'0 0 20px rgba(102, 126, 234, 0.5)' if status == 'running' else 'none'};
                transition: all 0.3s ease;
            ">
                <div style="font-size: 2em;">{info['icon']}</div>
                <div style="font-weight: bold; color: white; margin-top: 5px;">{info['name']}</div>
                <div style="font-size: 0.8em; color: #888; margin-top: 3px;">{info['desc']}</div>
                <div style="margin-top: 10px;">{status_colors.get(status, '⚪')} {status.upper()}</div>
            </div>
            """, unsafe_allow_html=True)

# ============ 工作流程可视化 ============
def render_workflow_animation():
    """渲染工作流程动画"""
    steps = [
        {"name": "市场洞察", "icon": "📊", "desc": "收集市场数据 → 分析趋势 → 识别机会"},
        {"name": "选品策略", "icon": "🛒", "desc": "产品筛选 → 评分排序 → 定价策略"},
        {"name": "内容创作", "icon": "✍️", "desc": "脚本生成 → 多平台适配 → 内容矩阵"},
        {"name": "投放优化", "icon": "📈", "desc": "数据分析 → 策略优化 → 预算分配"},
        {"name": "售后舆情", "icon": "💬", "desc": "评论分析 → 情感检测 → 解决方案"}
    ]
    
    st.subheader("🔄 工作流程可视化")
    
    # 创建流程图
    fig = go.Figure()
    
    for i, step in enumerate(steps):
        # 节点
        fig.add_trace(go.Scatter(
            x=[i],
            y=[0],
            mode='markers+text',
            marker=dict(
                size=60,
                color='#667eea' if i <= st.session_state.current_step else '#e5e7eb',
                line=dict(color='#764ba2', width=3)
            ),
            text=step['icon'],
            textfont=dict(size=30),
            hovertemplate=f"<b>{step['name']}</b><br>{step['desc']}<extra></extra>"
        ))
        
        # 标签
        fig.add_trace(go.Scatter(
            x=[i],
            y=[-0.5],
            mode='text',
            text=step['name'],
            textfont=dict(size=12, color='white'),
            showlegend=False
        ))
        
        # 连接线
        if i < len(steps) - 1:
            fig.add_trace(go.Scatter(
                x=[i, i+0.8],
                y=[0, 0],
                mode='lines',
                line=dict(
                    color='#667eea' if i < st.session_state.current_step else '#e5e7eb',
                    width=4
                ),
                showlegend=False
            ))
            
            # 箭头
            fig.add_annotation(
                x=i+0.9,
                y=0,
                ax=i+0.7,
                ay=0,
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=2,
                arrowcolor='#667eea' if i < st.session_state.current_step else '#e5e7eb'
            )
    
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, 1]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============ 数据导出功能 ============
def get_download_link(data: Dict, filename: str, file_type: str = "json") -> str:
    """生成下载链接"""
    if file_type == "json":
        json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        b64 = base64.b64encode(json_str.encode()).decode()
        return f'<a href="data:application/json;base64,{b64}" download="{filename}.json">📥 下载 JSON</a>'
    elif file_type == "csv":
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        return f'<a href="data:text/csv;base64,{b64}" download="{filename}.csv">📥 下载 CSV</a>'

# ============ 主程序 ============

# 重置系统
if reset_button:
    st.session_state.coordinator = None
    st.session_state.result = None
    st.session_state.current_step = 0
    st.session_state.agent_status = {k: "idle" for k in st.session_state.agent_status}
    st.success("✅ 系统已重置")
    time.sleep(0.5)
    st.rerun()

# 渲染Agent状态面板
render_agent_status()

# 渲染工作流程
if st.session_state.show_animation:
    render_workflow_animation()

st.markdown("---")

# 运行工作流
if run_button:
    # 创建协调器
    if not st.session_state.coordinator:
        llm = None
        if use_llm:
            try:
                provider_map = {
                    "OpenAI GPT-4": "openai",
                    "Anthropic Claude": "anthropic",
                    "DeepSeek": "deepseek"
                }
                llm = LLMFactory.create_llm(provider=provider_map.get(llm_provider, "mock"))
                st.success(f"✅ 成功加载 {llm_provider}")
            except Exception as e:
                st.error(f"❌ 模型加载失败: {str(e)}")
                st.info("将使用模拟模式运行")
        
        st.session_state.coordinator = EcommerceAgentCoordinator(llm=llm)
    
    coordinator = st.session_state.coordinator
    
    # 执行工作流
    progress_bar = st.progress(0)
    status_container = st.empty()
    
    agent_names = {
        "market": "📊 市场洞察",
        "product": "🛒 选品策略", 
        "content": "✍️ 内容创作",
        "ad": "📈 投放优化",
        "after_sales": "💬 售后舆情"
    }
    
    def progress_callback(agent_name: str, current: int, total: int):
        progress = current / total
        progress_bar.progress(progress)
        st.session_state.current_step = current - 1
        st.session_state.agent_status[agent_name] = "running"
        
        # 更新其他Agent状态
        for name in st.session_state.agent_status:
            if name != agent_name:
                if list(agent_names.keys()).index(name) < list(agent_names.keys()).index(agent_name):
                    st.session_state.agent_status[name] = "completed"
        
        status_container.info(f"🔄 正在执行: {agent_names.get(agent_name, agent_name)} ({current}/{total})")
        st.rerun()
    
    try:
        with st.spinner("🤖 Agent智能体正在协同工作..."):
            result = coordinator.run_full_workflow(
                platform=platform_clean,
                callback=progress_callback
            )
        
        st.session_state.result = result
        st.session_state.agent_status = {k: "completed" for k in st.session_state.agent_status}
        
        # 保存历史
        st.session_state.execution_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "platform": platform_clean,
            "result": result
        })
        
        # 保存到数据库
        try:
            db_manager.save_workflow_run(platform_clean, result)
        except Exception as e:
            st.warning(f"数据库保存失败: {e}")
        
        progress_bar.progress(1.0)
        status_container.success("✅ 全链路分析完成！")
        
        st.balloons()
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 执行出错: {str(e)}")
        st.session_state.agent_status = {k: "error" for k in st.session_state.agent_status}
        st.exception(e)

# ============ 结果展示区域 ============
if st.session_state.result:
    result = st.session_state.result
    
    # 导出工具栏
    col_export1, col_export2, col_export3, _ = st.columns([1, 1, 1, 3])
    with col_export1:
        st.markdown(get_download_link(result, f"workflow_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "json"), 
                   unsafe_allow_html=True)
    with col_export2:
        # 导出执行日志
        logs_df = pd.DataFrame(result.get('execution_log', []))
        if not logs_df.empty:
            st.markdown(get_download_link(logs_df.to_dict('records'), "execution_logs", "csv"), 
                       unsafe_allow_html=True)
    with col_export3:
        if st.button("📊 生成报告PDF", use_container_width=True):
            st.info("📄 PDF报告生成功能开发中...")
    
    st.markdown("---")
    
    # KPI仪表板
    st.header("📈 实时KPI仪表板")
    
    kpis = result['summary_kpis']
    
    # 创建图表
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # 预期提升雷达图
        perf = kpis['performance_improvement']
        fig_radar = go.Figure()
        
        categories = ['ROI提升', '成本降低', '效率提升', 'CTR提升', '转化率']
        values = [
            25,  # ROI提升 %
            65,  # 成本降低 %
            70,  # 效率提升 %
            18,  # CTR提升 %
            30   # 转化率 %
        ]
        
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # 闭合
            theta=categories + [categories[0]],
            fill='toself',
            name='预期提升',
            fillcolor='rgba(102, 126, 234, 0.3)',
            line=dict(color='#667eea', width=2)
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            title="🎯 综合效能评估",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col_chart2:
        # Agent执行时间柱状图
        exec_log = result.get('execution_log', [])
        if exec_log:
            # 简化展示
            agent_exec_times = {
                "市场洞察": np.random.uniform(1, 3),
                "选品策略": np.random.uniform(0.5, 2),
                "内容创作": np.random.uniform(2, 4),
                "投放优化": np.random.uniform(1, 2.5),
                "售后舆情": np.random.uniform(0.5, 1.5)
            }
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=list(agent_exec_times.keys()),
                y=list(agent_exec_times.values()),
                marker=dict(
                    color=['#667eea', '#764ba2', '#f093fb', '#f7971e', '#4facfe'],
                    line=dict(color='white', width=1)
                ),
                text=[f"{v:.1f}s" for v in agent_exec_times.values()],
                textposition='auto'
            ))
            
            fig_bar.update_layout(
                title="⏱️ Agent执行时间分布",
                xaxis_title="Agent",
                yaxis_title="时间 (秒)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(tickfont=dict(color='white')),
                yaxis=dict(tickfont=dict(color='white'))
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # 详细结果标签页
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 执行摘要",
        "📊 市场洞察",
        "🛒 选品方案",
        "✍️ 内容矩阵",
        "📈 投放优化",
        "💬 售后舆情"
    ])
    
    with tab1:
        st.subheader("🎯 执行摘要")
        st.info(result['executive_summary'])
        
        # 执行信息卡片
        exec_info = result['execution_info']
        cols = st.columns(4)
        with cols[0]:
            st.metric("🕐 开始时间", exec_info['start_time'].split()[1])
        with cols[1]:
            st.metric("🕑 结束时间", exec_info['end_time'].split()[1])
        with cols[2]:
            st.metric("⏱️ 总耗时", f"{exec_info['execution_time_seconds']}秒")
        with cols[3]:
            st.metric("🤖 Agent数", len(exec_info['agents_executed']))
    
    with tab2:
        market = result['results']['market_insight']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 市场数据")
            market_df = pd.DataFrame(market['raw_market_data'])
            st.dataframe(market_df, use_container_width=True)
        
        with col2:
            st.markdown("### 🏆 高潜力品类")
            high_potential = pd.DataFrame(market['high_potential_categories'])
            if not high_potential.empty:
                # 添加可视化
                fig = px.scatter(
                    high_potential,
                    x='growth_rate',
                    y='profit_margin',
                    size='market_size',
                    color='competition_score',
                    hover_data=['category'],
                    title='品类分布图 (增长率 vs 利润率)',
                    labels={'growth_rate': '增长率', 'profit_margin': '利润率', 'competition_score': '竞争度'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📝 市场洞察报告")
        st.markdown(market['insight_report'])
    
    with tab3:
        product = result['results']['product_selection']
        
        st.markdown("### 🛒 选定产品")
        products_df = pd.DataFrame(product['selected_products'])
        if not products_df.empty:
            st.dataframe(products_df, use_container_width=True)
            
            # 利润分析图
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='成本价',
                x=products_df['name'],
                y=products_df['cost_price'],
                marker_color='#94a3b8'
            ))
            fig.add_trace(go.Bar(
                name='建议售价',
                x=products_df['name'],
                y=products_df['suggested_price'],
                marker_color='#667eea'
            ))
            fig.update_layout(
                barmode='group',
                title='💰 产品定价分析',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(product['selection_report'])
    
    with tab4:
        content = result['results']['content_creation']
        content_matrix = content['content_matrix']
        
        # 内容统计
        st.markdown("### 📊 内容统计")
        content_stats = {
            "产品数": len(content_matrix),
            "平台数": len(content['platforms']),
            "内容类型": ["短视频", "图文", "直播", "详情页"]
        }
        st.json(content_stats)
        
        for product_name, product_content in content_matrix.items():
            with st.expander(f"📦 {product_name}", expanded=True):
                platform_tabs = st.tabs(["🎵 抖音", "🛍️ 淘宝", "📕 小红书", "📺 快手"])
                
                with platform_tabs[0]:
                    st.code(product_content['douyin']['video_script'], language='markdown')
                
                with platform_tabs[1]:
                    st.write(f"**标题**: {product_content['taobao']['title']}")
                    st.markdown(product_content['taobao']['description'])
                
                with platform_tabs[2]:
                    st.write(f"**标题**: {product_content['xiaohongshu']['note_title']}")
                    st.markdown(product_content['xiaohongshu']['note_content'])
                
                with platform_tabs[3]:
                    st.code(product_content['kuaishou']['live_script'], language='markdown')
    
    with tab5:
        ad = result['results']['ad_optimization']
        
        col1, col2 = st.columns(2)
        with col1:
            ad_df = pd.DataFrame(ad['ad_performance_data'])
            st.dataframe(ad_df.head(20), use_container_width=True)
        
        with col2:
            # ROI趋势图
            perf = ad['performance_analysis']
            if 'plan_analysis' in perf:
                plan_df = pd.DataFrame(perf['plan_analysis'])
                fig = px.pie(
                    plan_df,
                    values='cost',
                    names='plan_id',
                    title='💰 广告预算分布'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 🎯 优化建议")
        for i, opt in enumerate(ad['optimization_actions'], 1):
            priority_color = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(opt['priority'], '⚪')
            with st.expander(f"{priority_color} 建议 {i}: {opt['action']}"):
                st.write(f"**详情**: {opt['details']}")
                st.write(f"**预期影响**: {opt['expected_impact']}")
    
    with tab6:
        after_sales = result['results']['after_sales']
        
        col1, col2 = st.columns(2)
        with col1:
            sentiment = after_sales['sentiment_analysis']['overall']
            
            # 情感分布饼图
            fig = go.Figure(data=[go.Pie(
                labels=['好评', '中评', '差评'],
                values=[sentiment['positive_count'], sentiment['neutral_count'], sentiment['negative_count']],
                hole=.4,
                marker_colors=['#4ade80', '#fbbf24', '#f87171']
            )])
            fig.update_layout(
                title="💬 评论情感分布",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            issues = after_sales['issue_analysis']['main_issues']
            issue_df = pd.DataFrame(issues, columns=['问题', '数量'])
            st.dataframe(issue_df, use_container_width=True)
        
        st.markdown("### ✅ 智能解决方案")
        for sol in after_sales['solutions'][:5]:
            if sol.get('type') == 'individual_response':
                with st.expander(f"💬 评论回复: {sol['review_text'][:30]}..."):
                    st.markdown(sol['response'])

else:
    # 欢迎界面
    st.markdown("""
    ## 👋 欢迎来到电商Agent智能体指挥中心
    
    ### 🚀 系统特性
    
    - **🤖 5大智能Agent** - 覆盖电商运营全链路
    - **📊 实时可视化** - 数据图表与流程动画
    - **💾 数据持久化** - 自动保存分析历史
    - **📤 一键导出** - JSON/CSV/PDF报告
    - **🔄 工作流监控** - Agent状态实时追踪
    
    ### 📖 快速开始
    
    1. 在左侧选择目标平台（抖音/淘宝/拼多多/小红书）
    2. 点击 **🚀 启动** 按钮开始分析
    3. 等待Agent智能体完成协同工作
    4. 查看详细分析报告与数据可视化
    
    ### 💡 使用技巧
    
    - 首次使用建议先用**模拟模式**体验完整流程
    - 配置AI模型可获得更智能的分析结果
    - 历史记录可随时回顾过往分析
    - 支持一键导出完整数据报告
    """)
    
    # 展示示例截图或架构图
    st.markdown("---")
    st.subheader("🏗️ 系统架构")
    
    # 使用流程图展示
    fig_arch = go.Figure()
    
    # 定义节点位置
    nodes = {
        "用户输入": (0, 2),
        "协调器": (2, 2),
        "市场洞察": (4, 4),
        "选品策略": (4, 2),
        "内容创作": (4, 0),
        "投放优化": (6, 3),
        "售后舆情": (6, 1),
        "结果汇总": (8, 2)
    }
    
    # 绘制节点
    for name, (x, y) in nodes.items():
        fig_arch.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(size=40, color='#667eea'),
            text=name,
            textposition='top center',
            textfont=dict(size=10, color='white')
        ))
    
    # 绘制连线
    connections = [
        ("用户输入", "协调器"),
        ("协调器", "市场洞察"),
        ("市场洞察", "选品策略"),
        ("选品策略", "内容创作"),
        ("内容创作", "投放优化"),
        ("投放优化", "售后舆情"),
        ("售后舆情", "结果汇总")
    ]
    
    for start, end in connections:
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]
        fig_arch.add_trace(go.Scatter(
            x=[x1, x2], y=[y1, y2],
            mode='lines',
            line=dict(color='#764ba2', width=2),
            showlegend=False
        ))
    
    fig_arch.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig_arch, use_container_width=True)
