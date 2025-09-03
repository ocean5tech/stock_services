#!/bin/bash
# GitHub上传脚本

echo "🚀 Stock Services Backend API - GitHub上传脚本"
echo "================================================"

# 检查token
if [ -z "$1" ]; then
    echo "❌ 请提供GitHub Personal Access Token"
    echo "使用方法: ./upload_to_github.sh YOUR_GITHUB_TOKEN"
    exit 1
fi

GITHUB_TOKEN=$1
REPO_OWNER="ocean5tech"
REPO_NAME="stock_services"

echo "📋 准备上传到: https://github.com/${REPO_OWNER}/${REPO_NAME}"

# 设置Git配置
git config user.name "Ocean5Tech"
git config user.email "admin@ocean5tech.com"

# 检查是否已经是Git仓库
if [ ! -d ".git" ]; then
    echo "📂 初始化Git仓库..."
    git init
    git branch -m main
fi

# 添加所有文件
echo "📝 添加文件..."
git add .

# 提交（如果有更改）
if git diff --staged --quiet; then
    echo "ℹ️ 没有新的更改需要提交"
else
    echo "💾 提交更改..."
    git commit -m "🚀 Stock Services v2.0.0 - AI-Powered Investment Analysis

✨ Features:
- 🤖 AI news analysis with Claude 4 Sonnet
- 📧 HTML email investment reports
- 🔄 n8n workflow automation
- 💾 Dual PostgreSQL database setup
- 📊 Real-time stock APIs (3003/3004/3005)
- 🎯 Intelligent stock recommendations

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
fi

# 设置远程仓库
echo "🔗 设置GitHub远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin https://${GITHUB_TOKEN}@github.com/${REPO_OWNER}/${REPO_NAME}.git

# 推送到GitHub
echo "⬆️ 推送到GitHub..."
if git push -u origin main; then
    echo "✅ 成功上传到GitHub!"
    echo "🔗 仓库地址: https://github.com/${REPO_OWNER}/${REPO_NAME}"
    echo ""
    echo "📊 项目统计:"
    echo "   - $(find . -name "*.py" | wc -l) Python文件"
    echo "   - $(find . -name "*.md" | wc -l) Markdown文档"
    echo "   - $(find . -name "*.json" | wc -l) JSON配置文件"
    echo "   - $(find . -name "*.sh" | wc -l) Shell脚本"
else
    echo "❌ 上传失败，请检查:"
    echo "   1. GitHub token是否有效"
    echo "   2. 仓库 ${REPO_OWNER}/${REPO_NAME} 是否存在"
    echo "   3. Token是否有push权限"
    exit 1
fi