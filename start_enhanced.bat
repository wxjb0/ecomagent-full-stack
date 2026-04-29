@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    电商Agent智能体系统 - 增强版启动器
echo ========================================
echo.

REM 设置环境变量
set STREAMLIT_TELEMETRY_OPT_OUT=1
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set PYTHONIOENCODING=utf-8

cd /d "d:\ecomagent full-stack"

echo [1/2] 正在启动增强版Streamlit服务...
echo [FEATURE] 特性: 实时可视化、Agent监控、流程动画
echo [URL] 访问地址: http://localhost:8501
echo.

REM 启动增强版Streamlit
python -m streamlit run "d:\ecomagent full-stack\app_enhanced.py" --server.port 8501 --server.address 127.0.0.1 --server.headless true

pause
