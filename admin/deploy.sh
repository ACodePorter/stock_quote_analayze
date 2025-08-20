#!/bin/bash

# 生产环境部署脚本

echo "开始部署..."

# 1. 安装依赖
echo "安装依赖..."
npm install

# 2. 构建生产版本
echo "构建生产版本..."
npm run build

# 3. 检查构建结果
echo "检查构建结果..."
if [ -d "dist" ]; then
    echo "✅ 构建成功"
    echo "📁 dist目录内容："
    ls -la dist/
    echo ""
    echo "📄 index.html内容预览："
    head -10 dist/index.html
else
    echo "❌ 构建失败"
    exit 1
fi

# 4. 检查资源路径
echo "检查资源路径..."
if grep -q "\./assets/" dist/index.html; then
    echo "✅ 资源路径配置正确（相对路径）"
else
    echo "❌ 资源路径配置错误"
    exit 1
fi

echo "部署完成！"
echo "请将 dist 目录的内容上传到您的服务器。"
