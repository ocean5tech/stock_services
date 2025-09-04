# 📦 Vercel部署指南 - 股票服务系统

## 🚀 快速部署到Vercel

### 前提条件
- ✅ 已有Vercel账号 (https://vercel.com)
- ✅ GitHub账号
- ✅ 项目已上传到GitHub

### 🔧 部署步骤

#### 1. 准备项目文件
项目已包含以下Vercel配置文件：
```
stock_services/
├── vercel.json              # Vercel配置文件
├── requirements-vercel.txt  # 轻量级Python依赖
├── api/
│   └── vercel/
│       └── stock-analysis.py  # 无服务器函数
└── public/                  # 前端静态文件
    ├── index.html          # 主页面
    ├── package.json        # Node.js依赖
    ├── tailwind.config.js  # TailwindCSS配置
    └── js/app.js          # 前端应用逻辑
```

#### 2. 部署到Vercel

**方法一：通过GitHub自动部署 (推荐)**
1. 访问 https://vercel.com/dashboard
2. 点击 "New Project"
3. 选择你的GitHub仓库 `stock_services`
4. Vercel会自动检测配置并部署

**方法二：通过Vercel CLI**
```bash
# 安装Vercel CLI
npm i -g vercel

# 在项目目录运行
cd /home/ubuntu/stock_services
vercel

# 按提示完成部署配置
```

#### 3. 配置域名和环境变量
1. 在Vercel Dashboard中找到你的项目
2. 进入 Settings > Domains 配置自定义域名（可选）
3. 进入 Settings > Environment Variables 添加环境变量（如需要）

### 📋 部署后的功能

#### 🌐 访问地址
- **主页**: `https://your-project.vercel.app/`
- **API端点**: `https://your-project.vercel.app/api/vercel/stock-analysis`

#### 🔧 可用API端点

**1. 股票信息查询**
```
GET /api/vercel/stock-analysis?code=000001
```
响应示例：
```json
{
  "stock_code": "000001",
  "stock_info": {
    "name": "平安银行",
    "price": 11.75,
    "change": -0.23,
    "change_percent": -1.92,
    "market_cap": "2280亿",
    "industry": "银行"
  },
  "data_source": "vercel_serverless",
  "timestamp": "2025-09-03T23:52:00.000Z"
}
```

**2. 股票分析**
```
GET /api/vercel/stock-analysis/000001?type=basic
```

### 🎨 前端功能

#### 功能特性
- ✅ 响应式设计 (TailwindCSS)
- ✅ 股票搜索和信息展示
- ✅ 暗色/亮色主题切换
- ✅ Handlebars.js模板系统
- ✅ API状态监控
- ✅ 实时数据更新

#### 使用方法
1. 在搜索框输入股票代码 (如: 000001)
2. 点击"查询股票"或按回车
3. 系统自动显示股票信息
4. 可切换主题模式

### 🔄 本地开发

#### 安装依赖
```bash
# 进入前端目录
cd public
npm install

# 构建TailwindCSS
npm run build-css

# 启动本地服务器
npm run dev
```

#### 测试无服务器函数
```bash
# 安装Vercel CLI并在本地运行
vercel dev
```

### 📊 监控和维护

#### 性能监控
- Vercel自动提供性能分析
- 函数执行时间监控
- 带宽使用统计

#### 日志查看
1. 进入Vercel Dashboard
2. 选择项目 > Functions
3. 查看函数执行日志

### 🔧 自定义配置

#### 修改API逻辑
编辑文件: `api/vercel/stock-analysis.py`
```python
# 在handler类中添加新的路由和处理逻辑
def handle_custom_endpoint(self, query_params):
    # 你的自定义逻辑
    return {"custom": "data"}
```

#### 修改前端样式
编辑文件: `public/src/input.css`
```css
/* 添加自定义样式 */
.custom-component {
    @apply bg-blue-500 text-white p-4;
}
```

#### 添加新的页面
1. 在 `public/` 目录创建新HTML文件
2. 更新 `public/js/app.js` 添加路由逻辑

### ⚠️ 注意事项

#### Vercel限制
- 函数执行时间限制: 10秒 (Hobby), 60秒 (Pro)
- 函数大小限制: 50MB
- 请求超时: 10秒
- 并发限制: 1000个并发请求

#### 数据源配置
当前使用模拟数据。生产环境中需要：
1. 接入真实股票数据API
2. 配置数据库连接
3. 设置缓存策略

#### 安全考虑
- 添加API密钥验证
- 实施请求频率限制
- 配置CORS策略

### 🔗 相关链接
- [Vercel文档](https://vercel.com/docs)
- [TailwindCSS文档](https://tailwindcss.com/docs)
- [Handlebars.js文档](https://handlebarsjs.com/)

---

## 💡 部署成功后的使用流程

### 第一次部署
1. ✅ 上传代码到GitHub
2. ✅ 连接Vercel账号
3. ✅ 自动部署完成
4. ✅ 获得 `.vercel.app` 域名

### 日常使用
1. 访问你的Vercel域名
2. 使用前端界面查询股票
3. 或直接调用API端点
4. 查看Vercel Dashboard监控数据

### 更新部署
只需要push代码到GitHub，Vercel会自动重新部署！

🎉 **恭喜！你的股票服务系统现已部署到Vercel并可以免费使用！**