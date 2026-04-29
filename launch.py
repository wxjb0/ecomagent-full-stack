#!/usr/bin/env python3
"""
启动脚本 - 快速启动电商Agent系统
支持：基础版、增强版、API服务
"""

import argparse
import subprocess
import sys
import os

def print_banner():
    """打印启动横幅"""
    print("""
=================================================================

      电商全链路多Agent智能体系统 - 启动器

              Ecommerce Multi-Agent System Launcher

=================================================================
    """)

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import plotly
        import fastapi
        print("[OK] 依赖检查通过")
        return True
    except ImportError as e:
        print(f"[ERROR] 缺少依赖: {e}")
        print("[TIP] 请运行: pip install -r requirements.txt")
        return False

def run_basic_ui():
    """运行基础版Streamlit界面"""
    print("[LAUNCH] 启动基础版界面...")
    print("[URL] 访问地址: http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def run_enhanced_ui():
    """运行增强版Streamlit界面"""
    print("[LAUNCH] 启动增强版界面...")
    print("[FEATURE] 特性: 实时可视化、Agent监控、流程动画")
    print("[URL] 访问地址: http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app_enhanced.py"])

def run_api():
    """运行基础版API服务"""
    print("[LAUNCH] 启动基础版API服务...")
    print("[URL] API文档: http://localhost:8000/docs")
    subprocess.run([sys.executable, "run_api.py"])

def run_enhanced_api():
    """运行增强版API服务"""
    print("[LAUNCH] 启动增强版API服务...")
    print("[FEATURE] 特性: WebSocket、智能缓存、性能分析")
    print("[URL] API文档: http://localhost:8000/docs")
    print("[URL] WebSocket: ws://localhost:8000/ws/{client_id}")
    subprocess.run([sys.executable, "run_api_enhanced.py"])

def run_cli():
    """运行命令行工具"""
    print("[LAUNCH] 启动命令行工具...")
    subprocess.run([sys.executable, "main.py", "--help"])

def init_database():
    """初始化数据库"""
    print("[INIT] 初始化数据库...")
    try:
        from data.database import db_manager
        # 创建表
        db_manager.engine.execute("SELECT 1")
        print("[OK] 数据库初始化完成")
        
        # 清理过期缓存
        count = db_manager.clear_expired_cache()
        print(f"[CLEAN] 清理了 {count} 条过期缓存")
        
    except Exception as e:
        print(f"[ERROR] 数据库初始化失败: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="电商Agent系统启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python launch.py --ui           # 启动基础版界面
  python launch.py --ui-enhanced  # 启动增强版界面（推荐）
  python launch.py --api          # 启动基础版API
  python launch.py --api-enhanced # 启动增强版API（推荐）
  python launch.py --cli          # 命令行工具
  python launch.py --init       # 初始化数据库
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ui", action="store_true", help="启动基础版Streamlit界面")
    group.add_argument("--ui-enhanced", action="store_true", help="启动增强版界面（推荐）")
    group.add_argument("--api", action="store_true", help="启动基础版API服务")
    group.add_argument("--api-enhanced", action="store_true", help="启动增强版API（推荐）")
    group.add_argument("--cli", action="store_true", help="命令行工具")
    group.add_argument("--init", action="store_true", help="初始化数据库")
    
    args = parser.parse_args()
    
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 执行对应功能
    if args.ui:
        run_basic_ui()
    elif args.ui_enhanced:
        run_enhanced_ui()
    elif args.api:
        run_api()
    elif args.api_enhanced:
        run_enhanced_api()
    elif args.cli:
        run_cli()
    elif args.init:
        init_database()

if __name__ == "__main__":
    main()
