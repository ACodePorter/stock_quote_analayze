#!/bin/bash

# 环境部署脚本
# 用于在不同环境中配置正确的API地址

echo "🚀 股票分析系统管理后台 - 环境配置脚本"
echo "=========================================="

# 检测当前环境
if [ "$1" = "production" ]; then
    ENV="production"
    API_URL="https://www.icemaplecity.com/api/admin"
    echo "📦 配置生产环境"
elif [ "$1" = "development" ]; then
    ENV="development"
    API_URL="http://localhost:5000/api/admin"
    echo "🔧 配置开发环境"
else
    echo "❌ 请指定环境: production 或 development"
    echo "用法: ./deploy-env.sh [production|development]"
    exit 1
fi

echo "🔗 API地址: $API_URL"
echo "🌍 环境: $ENV"

# 创建环境配置文件
cat > .env.local << EOF
# 自动生成的环境配置文件
# 环境: $ENV
VITE_API_BASE_URL=$API_URL
VITE_ENVIRONMENT=$ENV
EOF

echo "✅ 环境配置文件已创建: .env.local"
echo "📝 内容:"
cat .env.local

echo ""
echo "🔄 请重新构建项目以应用新配置:"
echo "   npm run build"
echo ""
echo "🌐 或者启动开发服务器:"
echo "   npm run dev"
