# Stock Services 项目概览

## 📋 项目信息

- **项目名称**: Stock Services Backend API
- **版本**: v2.1.0
- **部署服务器**: 35.77.54.203
- **开发语言**: Python 3.12+
- **主要框架**: FastAPI, PostgreSQL, n8n
- **GitHub仓库**: https://github.com/ocean5tech/stock_services

## 🏗 系统架构

### 核心服务
1. **中国股票API服务** (端口 3003) - 基于AKShare的A股数据服务
2. **美国股票API服务** (端口 3004) - 美股实时数据服务
3. **中国期货API服务** (端口 3005) - 国内期货合约数据服务

### AI分析系统
- **新闻分析工作流** - 基于n8n的自动化新闻处理
- **智能投资建议** - 集成Claude 4 AI的专业分析
- **邮件报告系统** - HTML格式的投资分析报告

### 数据存储
- **stock_services** 数据库 - 存储股票、期货数据和API日志
- **newsanalysis** 数据库 - 存储AI分析结果和聊天记录

## 📁 项目文件结构说明

### `/api/` - API服务核心文件
- `akshare_service.py` - AKShare数据获取服务，提供统一的数据接口
- `chinese_stock_api.py` - 中国股票API主服务，端口3003
- `us_stock_api.py` - 美股API主服务，端口3004
- `futures_api.py` - 期货API主服务，端口3005
- `database.py` - PostgreSQL数据库连接和操作类
- `config.py` - 服务配置管理
- `.env.example` - 环境变量模板

### `/config/` - 配置文件
- `postgresql_setup.sql` - PostgreSQL数据库初始化脚本

### `/scripts/` - 部署和管理脚本
- `deploy.sh` - 完整的服务部署脚本
- `setup_production.sh` - 生产环境快速部署
- `monitor.sh` - 服务监控和健康检查
- `stop_services.sh` - 停止所有服务
- `upload_to_github.sh` - GitHub上传助手

### `/workflows/` - n8n工作流配置
- `n8n_workflow_final.json` - 主要的新闻分析工作流

### `/docs/` - 项目文档
- `PROJECT_OVERVIEW.md` - 项目概览（本文档）

### 根目录文件
- `README.md` - 项目主文档和使用指南
- `API_DOCUMENTATION.md` - 详细的API接口文档
- `CLAUDE.md` - Claude Code项目指令
- `requirements.txt` - Python依赖包列表
- `.gitignore` - Git忽略规则

## 🚀 快速开始

### 1. 环境准备
```bash
git clone https://github.com/ocean5tech/stock_services.git
cd stock_services
cp api/.env.example api/.env
# 编辑api/.env文件配置必要参数
```

### 2. 数据库初始化
```bash
sudo -u postgres psql < config/postgresql_setup.sql
```

### 3. 服务部署
```bash
./scripts/setup_production.sh
```

### 4. 验证服务
```bash
./scripts/monitor.sh
curl http://35.77.54.203:3003/health
curl http://35.77.54.203:3004/health
curl http://35.77.54.203:3005/health
```

## 🔧 主要功能模块

### 股票数据服务
- **实时数据获取** - 通过AKShare获取最新股票数据
- **智能缓存机制** - 避免过度API调用，提高响应速度
- **数据库持久化** - 所有数据自动存储到PostgreSQL
- **RESTful API** - 标准化的API接口设计

### AI新闻分析
- **RSS新闻监控** - 自动抓取Bloomberg等金融新闻源
- **Claude 4分析** - 专业投资建议和风险评估
- **股票关联** - 自动识别新闻中的相关股票
- **邮件通知** - 生成HTML格式的投资分析报告

### 工作流自动化
- **n8n驱动** - 可视化工作流配置
- **模块化设计** - 独立的分析模块，易于维护
- **错误处理** - 完善的异常处理和重试机制
- **日志记录** - 详细的操作日志和监控

## 📊 技术特性

### 性能优化
- **连接池管理** - PostgreSQL连接池优化
- **异步处理** - FastAPI异步I/O支持  
- **智能缓存** - 股票数据缓存机制
- **并发支持** - 支持高并发API调用

### 安全特性
- **SQL注入防护** - 参数化查询
- **输入验证** - 严格的数据类型检查
- **访问日志** - 完整的API调用记录
- **敏感信息保护** - 环境变量管理

### 部署特性
- **一键部署** - 自动化部署脚本
- **健康检查** - 服务状态监控
- **日志管理** - 结构化日志记录
- **错误恢复** - 自动重启机制

## 🔄 开发工作流

### 本地开发
1. 克隆项目并配置环境变量
2. 启动PostgreSQL服务
3. 运行数据库初始化脚本
4. 启动各个API服务进行测试

### 生产部署
1. 使用`scripts/setup_production.sh`一键部署
2. 使用`scripts/monitor.sh`监控服务状态
3. 配置n8n工作流进行AI分析
4. 设置定期备份和监控

### 代码贡献
1. Fork项目并创建功能分支
2. 按照项目规范编写代码和文档
3. 提交Pull Request并等待review
4. 合并后自动部署到生产环境

## 📈 未来规划

### 短期目标
- [ ] Web管理界面开发
- [ ] 移动端API适配
- [ ] 实时WebSocket推送
- [ ] 更多数据源集成

### 中期目标
- [ ] 机器学习预测模型
- [ ] 多语言支持
- [ ] 云原生架构迁移
- [ ] 微服务架构重构

### 长期目标
- [ ] 全球市场数据支持
- [ ] 高级量化分析工具
- [ ] 社区版本开源
- [ ] 商业化产品路线

## 📞 联系信息

- **GitHub**: https://github.com/ocean5tech/stock_services
- **Issues**: 通过GitHub Issues反馈问题
- **服务器**: 35.77.54.203
- **API文档**: http://35.77.54.203:3003/docs

---

*最后更新: 2025-09-03*
*版本: v2.1.0*