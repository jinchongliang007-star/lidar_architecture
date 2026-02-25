@echo off
chcp 65001 >nul
echo ========================================
echo   机械旋转式激光雷达教学演示系统
echo ========================================
echo.

cd /d %~dp0

REM 检查虚拟环境是否存在
if exist "venv\Scripts\activate.bat" (
    echo 正在激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo [提示] 虚拟环境不存在，使用系统 Python
)

REM 检查依赖是否安装
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo [警告] PyQt5 未安装，正在安装依赖...
    pip install PyQt5 PyOpenGL numpy
)

echo.
echo 正在启动程序...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行失败
    pause
)
