# 股票分析服务 (Stock Analysis Services)

> AI驱动的股票投资分析后端API服务，为n8n工作流提供全面的股票数据分析支持

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![AKShare](https://img.shields.io/badge/AKShare-1.17.42-orange.svg)](https://akshare.akfamily.xyz/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-blue.svg)](https://www.postgresql.org/)
[![n8n](https://img.shields.io/badge/n8n-AI%20Workflow-purple.svg)](https://n8n.io/)
[![akshare](https://img.shields.io/badge/akshare-1.17.42-red.svg)](https://akshare.akfamily.xyz/)

## 项目简介 / Project Overview

这是一个基于FastAPI和PostgreSQL的综合股票服务后端API系统，集成AI驱动的新闻分析工作流，部署在服务器IP `35.77.54.203` 上。系统包含三个独立的股票API服务和完整的AI新闻分析系统。

This is a comprehensive stock services backend API system based on FastAPI and PostgreSQL, integrated with AI-driven news analysis workflows, deployed on server IP `35.77.54.203`. The system includes three independent stock API services and a complete AI news analysis system.

## 🚀 核心功能 / Core Features

### 📊 股票数据服务
- **多市场支持**：中国A股、美股、期货数据
- **实时API**：高性能REST API接口
- **智能缓存**：自动数据刷新和缓存管理
- **PostgreSQL存储**：完整的数据持久化

### 🤖 AI新闻分析
- **智能分析**：集成Claude 4 AI的专业投资建议
- **自动化工作流**：n8n驱动的全自动新闻处理
- **实时股票验证**：通过API验证股票信息
- **HTML邮件报告**：专业格式的投资分析报告

## 🛠 服务架构 / Service Architecture

| 服务 / Service | 端口 / Port | 描述 / Description | API文档 / API Docs |
|---------------|------------|-------------------|-------------------|
| 中国股票服务 / Chinese Stocks | 3003 | 中国A股实时数据 | http://35.77.54.203:3003/docs |
| 美国股票服务 / US Stocks | 3004 | 美股实时数据 | http://35.77.54.203:3004/docs |
| 中国期货服务 / Chinese Futures | 3005 | 中国期货实时数据 | http://35.77.54.203:3005/docs |

## 🎯 n8n工作流集成 / n8n Workflow Integration

### 多维度分析工作流
系统设计了4个核心工作流，提供全面的股票投资分析：

1. **主协调工作流 (workflows/main.json)**
   - 统一股票输入接口
   - 并行调用3个子分析工作流
   - 结果整合和报告生成

2. **基本面分析工作流 (workflows/fund.json)**
   - HTTP请求: `http://35.77.54.203:3003/stocks/{stock_code}/analysis/fundamental`
   - 获取80+财务指标数据
   - Claude AI智能基本面分析

3. **技术面分析工作流 (workflows/tech.json)**
   - HTTP请求: `http://35.77.54.203:3003/stocks/{stock_code}/analysis/technical`
   - K线数据和技术指标分析
   - Claude AI智能技术面分析

4. **消息面分析工作流 (workflows/news.json)**
   - 4个HTTP请求获取不同维度新闻数据
   - 公司公告、股东变动、龙虎榜、行业新闻
   - Claude AI智能消息面分析

### AI分析特性
- 🤖 **Claude 4 Sonnet模型**：专业投资建议生成
- 📊 **多维度分析**：基本面+技术面+消息面
- 🎯 **投资建议**：买入/卖出/持有建议
- 💰 **价格预测**：目标价格和风险评估
- 📧 **HTML报告**：专业格式邮件通知

## 💾 数据库配置 / Database Configuration

### 数据库结构
```
stock_services (股票数据库)
├── chinese_stocks     # 中国股票数据
├── us_stocks         # 美股数据
├── chinese_futures   # 期货数据
└── api_logs          # API调用日志

newsanalysis (新闻分析数据库)
├── processed_news    # 处理后的新闻分析
└── chat_memory      # AI对话记录
```

### 快速设置
```bash
# 执行数据库初始化
sudo -u postgres psql < postgresql_setup.sql
```

## 🚀 快速开始 / Quick Start

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/ocean5tech/stock_services.git
cd stock_services

# 复制环境配置
cp .env.example .env
# 编辑 .env 文件填入实际配置
```

### 2. 数据库初始化
```bash
# 初始化PostgreSQL数据库
sudo -u postgres psql < postgresql_setup.sql
```

### 3. 一键部署
```bash
# 生产环境一键部署
./setup_production.sh
```

### 4. 启动股票分析API
```bash
# 启动中国股票分析服务 (端口3003)
cd /home/ubuntu/stock_services
python3 -m uvicorn api.stock_analysis_api:app --host 0.0.0.0 --port 3003

# 后台运行
nohup python3 -m uvicorn api.stock_analysis_api:app --host 0.0.0.0 --port 3003 > logs/stock_api.log 2>&1 &
```

### 5. 验证API服务
```bash
# 检查API健康状态
curl http://35.77.54.203:3003/

# 测试基本面分析API
curl "http://35.77.54.203:3003/stocks/000001/analysis/fundamental"

# 测试技术面分析API  
curl "http://35.77.54.203:3003/stocks/000001/analysis/technical"

# 测试消息面分析API
curl "http://35.77.54.203:3003/stocks/000001/news/announcements"
```

## 📖 API使用示例 / API Usage Examples

### 📊 股票分析API端点 (端口3003)

#### 基本面分析
```bash
# 获取平安银行基本面分析
curl "http://35.77.54.203:3003/stocks/000001/analysis/fundamental"

# 获取招商银行基本面分析  
curl "http://35.77.54.203:3003/stocks/600036/analysis/fundamental"

# 返回数据包含：
# - 股票基本信息（股票代码、名称、总股本等）
# - 80+财务指标（营收、净利润、总资产、净资产等）
# - AI分析所需的结构化数据
```

#### 技术面分析
```bash
# 获取平安银行技术面分析
curl "http://35.77.54.203:3003/stocks/000001/analysis/technical"

# 获取招商银行技术面分析
curl "http://35.77.54.203:3003/stocks/600036/analysis/technical"

# 返回数据包含：
# - K线数据（最近60天日线数据）
# - 实时行情（最新价、涨跌幅、成交量）
# - 技术指标（换手率、市盈率、市净率等）
```

#### 消息面分析
```bash
# 公司公告
curl "http://35.77.54.203:3003/stocks/000001/news/announcements"

# 股东变动
curl "http://35.77.54.203:3003/stocks/000001/news/shareholders"

# 龙虎榜数据
curl "http://35.77.54.203:3003/stocks/000001/news/dragon-tiger"

# 行业新闻
curl "http://35.77.54.203:3003/stocks/000001/news/industry"

# 注意：消息面API当前为占位符，AKShare相关接口暂不稳定
```

### 📈 API响应示例

#### 基本面分析响应
```json
{
  "stock_code": "000001",
  "stock_name": "平安银行",
  "analysis_type": "fundamental",
  "data_source": "akshare_comprehensive",
  "update_time": "2025-09-03T10:30:00",
  "basic_info": {
    "股票简称": "平安银行",
    "总股本": "19405918198",
    "流通股": "19405918198"
  },
  "financial_indicators": [
    // 80+财务指标数据
  ],
  "analysis_data": {
    "company_overview": {
      "stock_code": "000001",
      "stock_name": "平安银行",
      "total_shares": "19405918198"
    },
    "financial_metrics": {
      "revenue": 176543000000,
      "net_profit": 37252000000
    }
  }
}
```

## 🤖 n8n工作流配置 / n8n Workflow Setup

### 1. 导入工作流文件
```bash
# 在n8n管理界面中导入以下工作流文件：
workflows/main.json          # 主协调工作流
workflows/fund.json          # 基本面分析工作流  
workflows/tech.json          # 技术面分析工作流
workflows/news.json          # 消息面分析工作流
```

### 2. 配置API连接
确保以下服务正确配置：

- **股票API服务**: http://35.77.54.203:3003 (确保API服务运行中)
- **Anthropic API**: Claude 4 Sonnet模型 (需要有效API密钥)
- **PostgreSQL**: newsanalysis数据库 (用于存储分析结果)
- **Gmail SMTP**: 邮件发送配置 (用于HTML报告发送)

### 3. 工作流执行流程

1. **股票代码输入** → 在主工作流中输入股票代码 (如: 000001)

2. **并行数据获取** → 3个子工作流并行执行：
   - 基本面分析：调用 `/stocks/{code}/analysis/fundamental`
   - 技术面分析：调用 `/stocks/{code}/analysis/technical`  
   - 消息面分析：调用 4个消息面API端点

3. **AI智能分析** → Claude 4对获取的数据进行专业投资分析

4. **结果整合** → 生成综合投资建议和风险评估

5. **报告发送** → HTML格式邮件报告自动发送

### 4. 工作流特性
- ✅ **多维度分析**: 基本面+技术面+消息面
- ✅ **并行处理**: 3个分析维度同时执行，提升效率
- ✅ **AI驱动**: Claude 4专业投资建议生成
- ✅ **数据持久化**: PostgreSQL存储完整分析结果
- ✅ **邮件通知**: HTML格式专业投资报告
- ✅ **错误处理**: 完整的异常处理和重试机制

## 🛠 管理工具 / Management Tools

### 服务管理
```bash
# 停止所有服务
./stop_services.sh

# 监控服务状态
./monitor.sh

# 持续监控
./monitor.sh --watch

# 自动重启异常服务
./monitor.sh --auto-restart
```

### 日志管理
```bash
# 查看服务日志
tail -f logs/*.log

# 查看数据库日志
sudo tail -f /var/log/postgresql/postgresql-*.log
```

## 📊 性能特性 / Performance Features

- **连接池管理**: PostgreSQL连接池优化
- **智能缓存**: 股票数据5分钟缓存，期货3分钟缓存
- **异步处理**: FastAPI异步I/O支持
- **并发控制**: 支持高并发API调用
- **负载均衡**: 支持多实例部署

## 🔒 安全特性 / Security Features

- **SQL注入防护**: 参数化查询
- **输入验证**: 严格数据类型检查
- **访问日志**: 完整API调用记录
- **错误处理**: 防止敏感信息泄露
- **数据库权限**: 最小权限原则

## 🚨 故障排除 / Troubleshooting

### 常见问题
1. **端口占用**: `./stop_services.sh && ./deploy.sh`
2. **数据库连接失败**: `sudo systemctl restart postgresql`
3. **AI分析失败**: 检查Anthropic API密钥和余额
4. **邮件发送失败**: 验证Gmail应用密码设置

### 健康检查
```bash
# API服务健康检查
curl http://35.77.54.203:3003/health
curl http://35.77.54.203:3004/health  
curl http://35.77.54.203:3005/health

# 数据库连接测试
sudo -u postgres psql -c "SELECT version();"
```

## 📈 项目路线图 / Roadmap

- [x] 基础股票API服务
- [x] AI新闻分析集成
- [x] PostgreSQL数据持久化
- [x] HTML邮件报告系统
- [ ] Web管理界面
- [ ] 移动端API
- [ ] 实时WebSocket推送
- [ ] 多语言支持

## 🤝 贡献指南 / Contributing

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📝 更新日志 / Changelog

### v2.0.0 (2025-08-28)
- ✅ 新增AI新闻分析工作流
- ✅ 集成Claude 4 AI智能投资建议
- ✅ HTML格式邮件报告系统
- ✅ PostgreSQL数据库完整配置
- ✅ n8n工作流自动化处理

### v1.0.0 (2025-08-27)
- ✅ 基础股票API服务
- ✅ 三个独立服务端口(3003/3004/3005)
- ✅ PostgreSQL数据持久化
- ✅ 部署和监控脚本

## 📞 联系方式 / Contact

- **项目地址**: https://github.com/ocean5tech/stock_services
- **问题反馈**: GitHub Issues
- **服务器**: 35.77.54.203

## 📄 许可证 / License

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**⭐ 如果这个项目对您有帮助，请给我们一个Star！**

**🤖 AI-Powered Stock Analysis - Making Smart Investment Decisions**