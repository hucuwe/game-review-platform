@echo off
chcp 65001 >nul
echo ========================================
echo   游戏评论平台 - 一键启动脚本
echo ========================================
echo.
echo 此脚本将同时启动后端和前端服务
echo.
echo 提示：
echo - 后端服务: http://127.0.0.1:5000
echo - 前端服务: http://localhost:5173
echo.
echo 按任意键开始启动...
pause >nul
echo.

echo [启动后端服务]
start "游戏评论平台-后端" cmd /k "%~dp0start-backend.bat"

echo 等待3秒后启动前端...
timeout /t 3 /nobreak >nul

echo [启动前端服务]
start "游戏评论平台-前端" cmd /k "%~dp0start-frontend.bat"

echo.
echo ========================================
echo   服务启动完成
echo ========================================
echo.
echo 两个服务窗口已打开：
echo 1. 后端服务窗口 (Flask)
echo 2. 前端服务窗口 (Vite)
echo.
echo 请保持这两个窗口运行
echo 关闭窗口或按 Ctrl+C 将停止对应服务
echo.
echo 按任意键关闭此窗口...
pause >nul
