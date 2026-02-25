#!/bin/bash

echo "========================================"
echo "  机械旋转式激光雷达教学演示系统"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# 检查虚拟环境是否存在
if [ -d "venv" ]; then
    echo "正在激活虚拟环境..."
    source venv/bin/activate
else
    echo "[提示] 虚拟环境不存在，使用系统 Python"
fi

# 检查依赖是否安装
python3 -c "import PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[警告] PyQt5 未安装，正在安装依赖..."
    pip3 install PyQt5 PyOpenGL numpy
fi

echo ""
echo "正在启动程序..."
echo ""
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 程序运行失败"
    read -p "按回车键退出..."
fi
