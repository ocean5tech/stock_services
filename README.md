# 股票服务后端API / Stock Services Backend API

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
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

## 🎯 AI新闻分析工作流 / AI News Analysis Workflow

### 工作流程
1. **RSS新闻获取** → Bloomberg金融新闻实时抓取
2. **AI分析处理** → Claude 4智能投资建议生成  
3. **股票API验证** → 实时股票数据验证和价格更新
4. **PostgreSQL存储** → 完整分析结果持久化存储
5. **HTML邮件发送** → 专业投资分析报告邮件通知

### 分析内容
- 🎯 **核心事件分析**：识别市场影响因素
- 📈 **股票推荐**：具体股票投资建议
- 💰 **价格预测**：目标价格和评级建议
- ⚠️ **风险评估**：专业风险提示
- 📊 **执行摘要**：API调用和置信度评估

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

### 4. 验证部署
```bash
# 检查服务状态
./monitor.sh

# 检查API健康
curl http://35.77.54.203:3003/health
curl http://35.77.54.203:3004/health  
curl http://35.77.54.203:3005/health
```

## 📖 API使用示例 / API Usage Examples

### 中国股票服务
```bash
# 获取平安银行股票信息
curl "http://35.77.54.203:3003/stocks/000001"

# 获取股票列表（支持分页）
curl "http://35.77.54.203:3003/stocks?limit=10&offset=0"

# 强制刷新最新数据
curl "http://35.77.54.203:3003/stocks/000001?refresh=true"
```

### 美国股票服务
```bash
# 获取苹果股票信息
curl "http://35.77.54.203:3004/stocks/AAPL"

# 按行业筛选股票
curl "http://35.77.54.203:3004/stocks?sector=Technology"
```

### 中国期货服务
```bash
# 获取沪铜期货信息
curl "http://35.77.54.203:3005/futures/cu2410"

# 搜索相关合约
curl "http://35.77.54.203:3005/contracts/铜"
```

## 🤖 n8n工作流配置 / n8n Workflow Setup

### 1. 导入工作流
```bash
# 在n8n界面中导入以下文件
n8n_workflow_final.json
```

### 2. 配置连接
- **Anthropic API**: Claude 4 Sonnet模型
- **PostgreSQL**: 使用newsanalysis数据库
- **Gmail**: 配置邮件发送账号
- **HTTP Request**: 验证股票API连接

### 3. 工作流特性
- ✅ HTML格式邮件报告
- ✅ 基于content_hash的去重处理
- ✅ 并行数据库存储和邮件发送
- ✅ 完整的错误处理和日志记录

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