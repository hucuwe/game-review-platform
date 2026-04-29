@echo off
chcp 65001 >nul
echo ========================================
echo   游戏评论平台 - 后端服务启动脚本
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

echo [2/4] 检查虚拟环境...
if not exist "venv" (
    echo 虚拟环境不存在，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
) else (
    echo 虚拟环境已存在
)
echo.

echo [3/4] 激活虚拟环境并检查依赖...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败
    pause
    exit /b 1
)

echo 检查依赖包...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 依赖包未安装，正在安装...
    echo 这可能需要几分钟时间，请耐心等待...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [警告] 使用清华镜像安装失败，尝试使用默认源...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [错误] 安装依赖失败
            pause
            exit /b 1
        )
    )
    echo 依赖安装完成
) else (
    echo 依赖包已安装
)
echo.

echo [4/4] 检查配置文件...
if not exist ".env" (
    echo [警告] .env 配置文件不存在
    if exist ".env.example" (
        echo 正在从 .env.example 复制配置文件...
        copy .env.example .env >nul
        echo [提示] 请检查 backend\.env 文件中的数据库配置
        echo.
    ) else (
        echo [错误] .env.example 文件也不存在
        pause
        exit /b 1
    )
)
echo.

echo ========================================
echo   启动后端服务
echo ========================================
echo 服务地址: http://127.0.0.1:5000
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python run.py

if errorlevel 1 (
    echo.
    echo [错误] 后端服务启动失败
    echo 可能的原因:
    echo 1. 数据库连接失败 - 请检查MySQL是否运行
    echo 2. 端口5000被占用 - 请关闭占用该端口的程序
    echo 3. 配置文件错误 - 请检查 backend\.env 文件
    echo.
    pause
)
