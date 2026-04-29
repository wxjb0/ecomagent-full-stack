"""
数据分析仪表盘 - Agent性能监控与统计
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from data.database import db_manager
from config.settings import get_settings

st.set_page_config(
    page_title="📊 Agent数据分析仪表盘",
    page_icon="📈",
    layout="wide"
)

st.title("📊 电商Agent智能体数据分析仪表盘")
st.markdown("---")

# 侧边栏控制
with st.sidebar:
    st.header("🔧 筛选条件")
    
    # 时间范围
    time_range = st.selectbox(
        "⏱️ 时间范围",
        ["最近7天", "最近30天", "最近90天", "全部"],
        index=1
    )
    
    days_map = {
        "最近7天": 7,
        "最近30天": 30,
        "最近90天": 90,
        "全部": 365
    }
    days = days_map[time_range]
    
    # 平台筛选
    platform = st.multiselect(
        "🎯 平台筛选",
        ["抖音", "淘宝", "拼多多", "小红书"],
        default=["抖音", "淘宝"]
    )
    
    st.markdown("---")
    
    # 刷新按钮
    if st.button("🔄 刷新数据", use_container_width=True):
        st.rerun()
    
    # 导出按钮
    if st.button("📥 导出报表", use_container_width=True):
        st.info("📄 导出功能开发中...")

# 获取数据
runs = db_manager.get_recent_runs(limit=100)

if not runs:
    st.info("💡 暂无数据，请先运行一些工作流分析")
    st.stop()

# 转换为DataFrame
df = pd.DataFrame([
    {
        "id": run.id,
        "platform": run.platform,
        "status": run.status,
        "start_time": run.start_time,
        "execution_time": run.execution_time_seconds,
        "summary": run.result_summary
    }
    for run in runs
])

# 时间筛选
if days < 365:
    cutoff_date = datetime.now() - timedelta(days=days)
    df = df[df['start_time'] >= cutoff_date]

# 平台筛选
if platform:
    df = df[df['platform'].isin(platform)]

# 统计指标
st.header("📈 核心指标")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🔄 总运行次数", len(df))

with col2:
    success_rate = (df['status'] == 'completed').mean() * 100
    st.metric("✅ 成功率", f"{success_rate:.1f}%")

with col3:
    avg_time = df['execution_time'].mean()
    st.metric("⏱️ 平均耗时", f"{avg_time:.1f}秒")

with col4:
    total_platforms = df['platform'].nunique()
    st.metric("🎯 覆盖平台", f"{total_platforms}个")

with col5:
    if len(df) > 0 and df['summary'].iloc[0]:
        summary = df['summary'].iloc[0]
        if 'performance_improvement' in summary:
            roi = summary['performance_improvement'].get('estimated_roi_improvement', 'N/A')
            st.metric("📈 预期ROI提升", roi)

st.markdown("---")

# 图表区域
st.header("📊 可视化分析")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎯 平台分布")
    platform_counts = df['platform'].value_counts()
    fig_pie = px.pie(
        values=platform_counts.values,
        names=platform_counts.index,
        title="各平台分析占比",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig_pie.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("⏱️ 执行时间趋势")
    df_sorted = df.sort_values('start_time')
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(
        x=df_sorted['start_time'],
        y=df_sorted['execution_time'],
        mode='lines+markers',
        name='执行时间',
        line=dict(color='#667eea', width=2),
        marker=dict(size=8)
    ))
    fig_time.update_layout(
        title="工作流执行时间趋势",
        xaxis_title="时间",
        yaxis_title="执行时间 (秒)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_time, use_container_width=True)

# 平台对比分析
st.subheader("📊 平台对比分析")

platform_stats = df.groupby('platform').agg({
    'execution_time': ['mean', 'min', 'max', 'count']
}).round(2)
platform_stats.columns = ['平均耗时', '最短耗时', '最长耗时', '运行次数']
platform_stats = platform_stats.reset_index()

st.dataframe(platform_stats, use_container_width=True)

# Agent性能分析
st.header("🤖 Agent性能分析")

agent_stats = db_manager.get_agent_performance_stats(days=days)
if agent_stats:
    col_agent1, col_agent2, col_agent3 = st.columns(3)
    
    with col_agent1:
        st.metric("🔄 Agent总运行", agent_stats['total_runs'])
    
    with col_agent2:
        st.metric("✅ Agent成功率", f"{agent_stats['success_rate']*100:.1f}%")
    
    with col_agent3:
        st.metric("⏱️ Agent平均耗时", f"{agent_stats['avg_execution_time_ms']:.0f}ms")
else:
    st.info("💡 暂无Agent性能数据")

# 缓存分析
st.header("💾 缓存分析")

# 这里可以添加缓存统计
st.info("💡 缓存统计功能将在后续版本添加")

# 最近工作流详情
st.header("📜 最近工作流详情")

for idx, row in df.head(5).iterrows():
    with st.expander(f"🔄 工作流 #{row['id']} - {row['platform']} - {row['start_time'].strftime('%Y-%m-%d %H:%M')}"):
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.write(f"**平台**: {row['platform']}")
            st.write(f"**状态**: {row['status']}")
        
        with col_info2:
            st.write(f"**执行时间**: {row['execution_time']:.2f}秒")
            st.write(f"**运行时间**: {row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col_info3:
            if row['summary'] and 'performance_improvement' in row['summary']:
                perf = row['summary']['performance_improvement']
                st.write(f"**预期ROI**: {perf.get('estimated_roi_improvement', 'N/A')}")
                st.write(f"**成本降低**: {perf.get('estimated_cost_reduction', 'N/A')}")

# 页脚
st.markdown("---")
st.caption(f"📊 数据最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🤖 电商Agent智能体系统 v2.0")
