# 🚀 快速开始 - Vercel部署

## 📋 3步完成部署

### 第1步：上传到GitHub
```bash
# 初始化Git仓库（如果还没有）
git init
git add .
git commit -m "添加Vercel部署配置"

# 推送到GitHub
git remote add origin https://github.com/你的用户名/stock_services.git
git push -u origin main
```

### 第2步：连接Vercel
1. 访问 [vercel.com](https://vercel.com)
2. 使用GitHub账号登录
3. 点击 "New Project"
4. 选择 `stock_services` 仓库
5. 点击 "Deploy" 

### 第3步：测试部署
部署完成后，你将获得：
- **网站地址**: `https://your-project-name.vercel.app`
- **API地址**: `https://your-project-name.vercel.app/api/vercel/stock-analysis`

## 🎯 立即测试

### 前端测试
访问你的Vercel域名：
1. 在搜索框输入 `000001`
2. 点击"查询股票"
3. 查看平安银行的模拟数据

### API测试
直接访问API端点：
```
https://your-project-name.vercel.app/api/vercel/stock-analysis?code=000001
```

## ⚡ 本地开发（可选）

### 运行前端
```bash
cd public
npm install
npm run dev
# 访问 http://localhost:8080
```

### 测试无服务器函数
```bash
# 安装Vercel CLI
npm i -g vercel

# 本地运行
vercel dev
# 访问 http://localhost:3000
```

## 🎉 完成！

现在你的股票服务系统已经：
- ✅ 部署到Vercel (完全免费)
- ✅ 具备响应式前端界面
- ✅ 提供无服务器API
- ✅ 支持暗色/亮色主题
- ✅ 自动更新部署

每次推送代码到GitHub，Vercel都会自动重新部署！

---

需要帮助？查看 [完整部署指南](./VERCEL_DEPLOYMENT_GUIDE.md)