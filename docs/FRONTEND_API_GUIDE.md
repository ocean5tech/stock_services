# 股票分析API - 前端开发者指南

**最后更新**: 2025-09-09  
**服务地址**: http://35.77.54.203:3003  
**Swagger文档**: http://35.77.54.203:3003/docs

## 📋 API概览

本API提供完整的股票分析服务，包括基础数据、技术分析、基本面分析、新闻消息面和AI智能分析功能。

## 🔗 API端点分类

### 1. 核心数据API（推荐使用）

#### 统一股票信息
```http
GET /stocks/{stock_code}
```
**用途**: 获取股票的核心统一数据，包括基本信息、当前价格、关键指标  
**使用场景**: 股票详情页、股票列表、仪表板  
**数据包含**: 基本信息、实时价格、市值、PE/PB、财务指标概要

#### 公司概况
```http
GET /stocks/{stock_code}/profile
```
**用途**: 获取公司基本资料和业务信息  
**使用场景**: 公司介绍页面、基本资料展示  
**数据包含**: 公司名称、行业分类、上市日期、股本结构

#### 基本面分析
```http
GET /stocks/{stock_code}/analysis/fundamental
```
**用途**: 获取详细的基本面分析数据  
**使用场景**: 基本面分析页面、财务指标对比  
**数据包含**: 完整财务指标、多季度数据、行业对比

#### 技术面分析
```http
GET /stocks/{stock_code}/analysis/technical
```
**用途**: 获取技术分析数据和K线图数据  
**使用场景**: K线图、技术指标图表  
**数据包含**: K线数据、技术指标、图表绘制数据

#### 历史价格
```http
GET /stocks/{stock_code}/historical/prices?days=30
```
**用途**: 获取历史价格数据  
**使用场景**: 价格走势图、历史数据分析  
**参数**: `days` - 获取天数（默认30天）  
**数据包含**: 开高低收、成交量、涨跌幅

#### 历史财务
```http
GET /stocks/{stock_code}/historical/financial
```
**用途**: 获取历史财务数据（最新8个季度）  
**使用场景**: 财务趋势分析、财务图表  
**数据包含**: 季度财务数据、趋势分析、财务指标

#### 实时报价
```http
GET /stocks/{stock_code}/live/quote
```
**用途**: 获取实时报价和买卖盘数据  
**使用场景**: 实时报价显示、买卖盘展示  
**数据包含**: 实时价格、买卖五档、成交量

#### 资金流向
```http
GET /stocks/{stock_code}/live/flow
```
**用途**: 获取资金流向数据  
**使用场景**: 资金流向分析、主力资金监控  
**数据包含**: 30天资金流向、主力净流入、资金统计

### 2. 新闻消息面API

#### 公司公告
```http
GET /stocks/{stock_code}/news/announcements
```
**用途**: 获取公司公告信息  
**使用场景**: 公告列表、重要消息提醒  
**数据包含**: 财务报告公告、重要事项公告

#### 股东变动（开发中）
```http
GET /stocks/{stock_code}/news/shareholders
```
**用途**: 获取股东变动信息  
**状态**: 接口开发中  
**使用场景**: 股东变化跟踪

#### 龙虎榜
```http
GET /stocks/{stock_code}/news/dragon-tiger
```
**用途**: 获取龙虎榜数据  
**使用场景**: 大单交易分析、机构动向  
**数据包含**: 90天内龙虎榜记录

#### 行业新闻（开发中）
```http
GET /stocks/{stock_code}/news/industry
```
**用途**: 获取行业相关新闻  
**状态**: 接口开发中  
**使用场景**: 行业动态、相关新闻

### 3. AI智能分析API ⭐

#### AI即时交易信号
```http
POST /ai/trading-signal/{stock_code}
Content-Type: application/json
{"force_refresh": false}
```
**用途**: 获取AI生成的即时交易建议  
**使用场景**: 交易决策辅助、智能投顾功能  
**缓存**: 30分钟智能缓存  
**数据包含**:
- 交易建议（买入/卖出/观望）
- 止损止盈位
- 技术分析摘要
- 风险警告
- 置信度评估

#### AI综合评估
```http
POST /ai/comprehensive-evaluation/{stock_code}
Content-Type: application/json
{"force_refresh": false}
```
**用途**: 获取AI生成的综合投资评估  
**使用场景**: 投资价值分析、详细研究报告  
**缓存**: 24小时智能缓存  
**数据包含**:
- 投资评级（推荐/中性/减持）
- 目标价位和上涨空间
- 详细投资逻辑
- 支撑数据和推理链条
- 不确定性因素
- 完整原始数据（已优化为最新8条）

### 4. AI缓存管理API

#### 查看缓存状态
```http
GET /ai/cache/status/{stock_code}
```
**用途**: 查看指定股票的AI分析缓存状态  
**数据包含**: 缓存是否存在、过期时间

#### 清除缓存
```http
DELETE /ai/cache/{stock_code}?cache_type=all
```
**用途**: 清除指定股票的缓存  
**参数**: `cache_type` - all/trading_signal/comprehensive

#### AI服务健康检查
```http
GET /ai/health
```
**用途**: 检查AI服务运行状态  
**数据包含**: Redis连接状态、AI Agent状态

## 📱 前端使用建议

### 股票详情页面
```javascript
// 获取核心数据
const stockData = await fetch(`/stocks/${stockCode}`);

// 获取实时报价
const liveQuote = await fetch(`/stocks/${stockCode}/live/quote`);

// 获取资金流向
const fundFlow = await fetch(`/stocks/${stockCode}/live/flow`);
```

### K线图页面
```javascript
// 获取技术分析数据
const technicalData = await fetch(`/stocks/${stockCode}/analysis/technical`);

// 获取历史价格
const priceData = await fetch(`/stocks/${stockCode}/historical/prices?days=60`);
```

### AI分析页面
```javascript
// 获取AI交易信号（自动缓存30分钟）
const tradingSignal = await fetch(`/ai/trading-signal/${stockCode}`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({force_refresh: false})
});

// 获取AI综合评估（自动缓存24小时）
const comprehensiveEval = await fetch(`/ai/comprehensive-evaluation/${stockCode}`, {
  method: 'POST', 
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({force_refresh: false})
});
```

### 性能优化建议

1. **使用核心API**: 优先使用 `/stocks/{stock_code}` 获取基础数据
2. **AI缓存机制**: AI分析会自动缓存，重复调用会直接返回缓存结果
3. **数据量控制**: 历史数据已优化为最新8条，减少传输量
4. **并行请求**: 不同类型的数据可以并行请求
5. **错误处理**: 所有API都包含完整的错误信息

## ⚠️ 重要说明

1. **股票代码格式**: 6位数字（如：000001, 603993）
2. **服务器地址**: 所有URL使用 `35.77.54.203:3003`，不要使用localhost
3. **AI功能**: 需要有效的Anthropic API密钥才能使用
4. **数据更新频率**: 实时数据约5分钟更新，财务数据按财报周期更新
5. **缓存策略**: AI分析有智能缓存，可大幅提升响应速度和降低成本

## 🚀 版本信息

- **API版本**: 2.0.0
- **最后更新**: 2025-09-09
- **重大更新**: 
  - 新增AI智能分析功能
  - 优化数据返回量（历史数据限制为最新8条）
  - 完善缓存机制
  - 修复资金流向API数据映射问题