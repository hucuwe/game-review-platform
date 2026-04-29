@echo off
chcp 65001 >nul
echo ========================================
echo   游戏评论平台 - 前端服务启动脚本
echo ========================================
echo.

cd /d "%~dp0frontend"

echo [1/3] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Node.js，请先安装Node.js 16+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
node --version
npm --version
echo.

echo [2/3] 检查依赖包...
if not exist "node_modules" (
    echo node_modules 不存在，正在安装依赖...
    echo 这可能需要几分钟时间，请耐心等待...
    echo.
    call npm install
    if errorlevel 1 (
        echo [错误] 安装依赖失败
        echo 尝试清理缓存后重新安装...
        call npm cache clean --force
        call npm install
        if errorlevel 1 (
            echo [错误] 依赖安装失败，请检查网络连接
            pause
            exit /b 1
        )
    )
    echo 依赖安装完成
) else (
    echo 依赖包已存在，检查是否需要更新...
    call npm install >nul 2>&1
    echo 依赖检查完成
)
echo.

echo [3/3] 启动开发服务器...
echo.
echo ========================================
echo   启动前端服务
echo ========================================
echo 服务将在浏览器中自动打开
echo 默认地址: http://localhost:5173
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

call npm run dev

if errorlevel 1 (
    echo.
    echo [错误] 前端服务启动失败
    echo 可能的原因:
    echo 1. 端口被占用 - 请关闭占用端口的程序
    echo 2. 依赖包损坏 - 请删除 node_modules 文件夹后重试
    echo 3. 配置文件错误 - 请检查 vite.config.js
    echo.
    pause
)
