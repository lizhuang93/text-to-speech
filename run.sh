#!/bin/bash

# 文本转语音项目启动脚本

echo "🎤 启动文本转语音项目..."
echo "=================================="

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查依赖是否安装
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 文件不存在"
    exit 1
fi

# 安装依赖（如果需要）
echo "📦 检查依赖..."
pip3 install -r requirements.txt --quiet

# 创建输出目录
mkdir -p output

# 启动服务器
echo "🚀 启动服务器..."
echo "🌐 访问地址: http://localhost:8080"
echo "📁 输出目录: $(pwd)/output"
echo "🔄 按 Ctrl+C 停止服务器"
echo "=================================="

# 运行服务器
python3 server.py