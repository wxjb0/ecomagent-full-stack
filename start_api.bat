@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    电商Agent智能体系统 - API服务
echo ========================================
echo.

set PYTHONIOENCODING=utf-8
cd /d "d:\ecomagent full-stack"

echo [1/2] 正在启动增强版API服务...
echo [FEATURE] 特性: WebSocket、智能缓存、性能分析
echo [URL] API文档: http://localhost:8000/docs
echo [URL] WebSocket: ws://localhost:8000/ws/{client_id}
echo.

python "d:\ecomagent full-stack\run_api_enhanced.py"

pause
