# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a stock services backend API project intended for deployment on server IP `35.77.54.203`. The repository is designed for backend API development using Python (Flask/FastAPI/Django) or Node.js (Express/NestJS) frameworks with PostgreSQL database integration.

## Server Configuration

- **Server IP**: 35.77.54.203 (NEVER use localhost or 127.0.0.1 in any configuration or documentation)
- **Available Ports**: 3003, 3004, 3005
- **Database**: PostgreSQL (pre-installed on server)
- **GitHub Repository**: https://github.com/ocean5tech/stock_services

## Development Standards

### Code Quality
- Write clean, maintainable code with Chinese comments for explanations
- Use English for variable and function names following standard conventions
- Implement comprehensive error handling and input validation throughout

### Database Operations
- Always use PostgreSQL with connection pooling
- Use parameterized queries to prevent SQL injection
- Implement proper transaction management
- Query database directly to verify INSERT, UPDATE, and DELETE operations

### Security Requirements
- Implement authentication and authorization
- Use input validation for all endpoints
- Configure HTTPS in production
- Implement rate limiting
- Never expose sensitive credentials

### Performance Optimization
- Optimize database queries with proper indexing
- Implement caching strategies where appropriate
- Use connection pooling for database connections

## Testing Protocol

**CRITICAL**: Never rely solely on HTTP status codes for validation.

- **INSERT operations**: Query PostgreSQL database to verify data actually exists
- **UPDATE operations**: Confirm actual data changes in database  
- **DELETE operations**: Verify data removal from database
- Test all endpoints with real database state verification
- Include security, performance, and edge case testing

## Deployment Requirements

### Port Management
- Kill existing processes on target ports before deployment
- Use assigned ports (3003, 3004, 3005) - do not change port numbers

### Database Setup
- Check PostgreSQL service status before startup
- Run database migrations automatically during deployment
- Verify database connection before starting API services

### Documentation
- Create deployment scripts for easy setup
- Implement one-click recovery procedures
- Generate comprehensive API documentation in Markdown

## API Design Standards

- Follow RESTful principles
- Always use server IP (35.77.54.203) in all URLs and documentation examples
- Include request/response schemas and examples
- Document error handling and security considerations
- Provide performance optimization guidance

## Code Management

- Upload to GitHub after completing major version testing
- Use meaningful commit messages with proper versioning
- Update documentation and changelog with each release
- Tag releases appropriately

## Workflow Approach

1. Analyze requirements and design API architecture
2. Implement code with proper PostgreSQL integration
3. Create comprehensive tests that verify actual database operations
4. Deploy with automatic conflict resolution and service verification
5. Generate documentation and upload to GitHub
6. Provide monitoring and maintenance guidance

## Agent Configuration

This repository includes a specialized `backend-api-developer` agent for handling complex API development tasks. Use this agent for:
- Designing and implementing new API endpoints
- Database integration and optimization
- Server infrastructure setup
- Performance debugging and optimization
- Production deployment procedures

## AI Agent APIs Development Plan

### 🎯 项目目标
基于改进的提示词创建两个AI Agent API，提供智能股票分析服务：
1. **即时技术面交易信号API** - 30分钟缓存
2. **综合股票评估报告API** - 24小时缓存

### 📋 开发计划

#### Phase 1: 基础设施准备 (30分钟)
1. **Redis缓存配置**
   - 配置Redis连接和缓存策略
   - 实现缓存键生成和TTL管理
   - 添加缓存健康检查

2. **AI Agent基础框架**
   - 扩展现有AI Agent基础类
   - 集成Anthropic Claude API调用
   - 实现错误处理和重试机制

3. **数据聚合服务**
   - 创建数据收集服务，整合8个API接口
   - 实现并行数据获取和异常处理
   - 数据格式标准化和验证

#### Phase 2: 即时技术面交易信号API (1小时)
**接口**: `POST /ai/trading-signal/{stock_code}`

**功能特性**:
- 30分钟内重复查询返回Redis缓存
- 调用日线级别技术分析提示词
- 返回具体买卖信号和操作建议

**数据源整合**:
```python
# 需要调用的API接口
apis_required = [
    "GET /stocks/{code}/live/quote",           # 实时报价
    "GET /stocks/{code}/historical/prices?days=30", # K线数据
    "GET /stocks/{code}/analysis/technical"    # 技术分析
]
```

**缓存策略**:
```python
cache_key = f"trading_signal:{stock_code}"
cache_ttl = 1800  # 30分钟
```

**响应格式**:
```json
{
  "analysis_type": "daily_technical_trading",
  "cached": true/false,
  "cache_expires_at": "timestamp",
  "immediate_trading_signal": {
    "action": "买入/卖出/观望/减仓",
    "entry_condition": "具体入场条件",
    "stop_loss": {"price": 11.20, "basis": "技术依据"},
    "take_profit": [{"price": 35.00, "basis": "目标位依据"}]
  },
  "ai_analysis": "完整的AI分析结果"
}
```

#### Phase 3: 综合股票评估报告API (1.5小时)
**接口**: `POST /ai/comprehensive-evaluation/{stock_code}`

**功能特性**:
- 24小时内重复查询返回Redis缓存  
- 调用综合评估提示词
- 返回完整的多维度分析和推理过程

**数据源整合**:
```python
# 需要调用的所有API接口
apis_required = [
    "GET /stocks/{code}",                      # 统一核心数据
    "GET /stocks/{code}/analysis/fundamental", # 基本面分析
    "GET /stocks/{code}/analysis/technical",   # 技术面分析  
    "GET /stocks/{code}/historical/financial", # 历史财务
    "GET /stocks/{code}/news/announcements",   # 公司公告
    "GET /stocks/{code}/news/dragon-tiger",    # 龙虎榜
    "GET /stocks/{code}/historical/prices",    # 历史价格
    "GET /stocks/{code}/live/flow"             # 资金流向
]
```

**缓存策略**:
```python
cache_key = f"comprehensive_eval:{stock_code}"
cache_ttl = 86400  # 24小时
```

**响应格式**:
```json
{
  "analysis_type": "comprehensive_stock_evaluation",
  "cached": true/false,
  "cache_expires_at": "timestamp",
  "comprehensive_evaluation": {
    "investment_rating": "推荐/中性/减持",
    "target_price": 35.00,
    "upside_potential": "15.2%"
  },
  "evidence_and_reasoning": {
    "key_supporting_data": [具体数据证据],
    "reasoning_chain": ["推理步骤1", "推理步骤2"],
    "uncertainty_factors": ["不确定性因素"]
  },
  "raw_data_sources": {
    "fundamental_data": {},  # 完整基本面数据
    "technical_data": {},    # 完整技术面数据
    "news_data": {},        # 完整消息面数据
    "financial_history": {} # 完整财务历史
  },
  "ai_analysis": "完整的AI分析结果"
}
```

#### Phase 4: 集成和测试 (1小时)
1. **API接口集成**
   - 添加到主FastAPI应用
   - 配置路由和中间件
   - 实现请求验证和限流

2. **缓存测试**
   - 验证30分钟和24小时缓存逻辑
   - 测试缓存失效和更新机制
   - 验证Redis连接和异常处理

3. **端到端测试**
   - 测试完整的AI分析流程
   - 验证数据聚合和格式化
   - 测试错误处理和边界情况

4. **性能优化**
   - 优化数据获取并发性
   - 减少AI API调用延迟
   - 监控内存和CPU使用

### 🏗️ 技术架构

#### 核心组件
```python
# 1. AI Agent服务
class TechnicalAnalysisAgent(BaseAgent):
    def analyze_trading_signal(stock_code: str) -> dict
    
class ComprehensiveAnalysisAgent(BaseAgent):
    def analyze_comprehensive_evaluation(stock_code: str) -> dict

# 2. 数据聚合服务  
class StockDataAggregator:
    def collect_technical_data(stock_code: str) -> dict
    def collect_comprehensive_data(stock_code: str) -> dict

# 3. 缓存管理服务
class AnalysisCache:
    def get_trading_signal_cache(stock_code: str) -> dict
    def set_trading_signal_cache(stock_code: str, data: dict) -> bool
    def get_comprehensive_cache(stock_code: str) -> dict
    def set_comprehensive_cache(stock_code: str, data: dict) -> bool
```

#### 文件结构
```
api/
├── ai_analysis/
│   ├── __init__.py
│   ├── agents/
│   │   ├── technical_agent.py      # 技术面分析Agent
│   │   ├── comprehensive_agent.py  # 综合分析Agent
│   │   └── base_agent.py          # 基础Agent类
│   ├── services/
│   │   ├── data_aggregator.py     # 数据聚合服务
│   │   ├── cache_manager.py       # 缓存管理
│   │   └── prompt_loader.py       # 提示词加载
│   ├── prompts/
│   │   ├── technical_trading.txt  # 技术面交易提示词
│   │   └── comprehensive_eval.txt # 综合评估提示词
│   └── api_endpoints.py           # API端点定义
└── stock_analysis_api.py          # 主应用集成
```

### ⏱️ 时间分配
- **Phase 1**: 基础设施 (30分钟)
- **Phase 2**: 技术面API (1小时)
- **Phase 3**: 综合评估API (1.5小时)  
- **Phase 4**: 集成测试 (1小时)
- **总计**: 4小时

### 🔧 关键技术要求
1. **缓存一致性**: Redis TTL精确控制
2. **数据完整性**: 确保所有8个API数据源可用
3. **错误恢复**: AI调用失败时的降级策略
4. **性能优化**: 并行数据获取，减少总响应时间
5. **监控日志**: 详细的调用日志和性能指标

### 📊 成功指标
- 技术面分析API响应时间 < 10秒
- 综合评估API响应时间 < 30秒  
- 缓存命中率 > 80%
- AI调用成功率 > 95%
- 数据完整性 > 99%

### 🚀 部署策略
1. 先部署到3003端口进行测试
2. 验证Redis连接和缓存功能
3. 测试AI Agent调用和响应格式
4. 监控性能指标和错误率
5. 完成后提交到GitHub并更新文档