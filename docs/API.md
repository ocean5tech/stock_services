# Stock Services API 完整文档

## 📖 概览 / Overview

本API文档描述了三个独立的股票服务API系统，提供全面的金融数据和分析服务。系统部署在服务器IP `35.77.54.203` 上，包含中国股票、美国股票和中国期货三个专业服务。

### 服务架构 / Service Architecture

| 服务名称 | 端口 | Base URL | 描述 |
|---------|------|----------|------|
| 中国股票分析服务 | 3003 | `http://35.77.54.203:3003` | 提供中国A股的完整分析服务 |
| 美国股票服务 | 3004 | `http://35.77.54.203:3004` | 美股实时数据和基本信息 |
| 中国期货服务 | 3005 | `http://35.77.54.203:3005` | 期货合约数据和实时行情 |

---

## 1. 中国股票分析服务API (端口 3003)

### 基础信息
- **Base URL**: `http://35.77.54.203:3003`
- **用途**: 中国A股数据分析和n8n工作流集成
- **特色**: AI驱动的三维分析（基本面+技术面+消息面）

### 1.1 健康检查端点

#### GET `/` - 服务状态
获取服务状态和可用端点列表

**响应示例:**
```json
{
  "message": "股票分析API服务正常运行",
  "service": "comprehensive_stock_api", 
  "version": "1.0.0",
  "endpoints": {
    "fundamental": "/stocks/{stock_code}/analysis/fundamental",
    "technical": "/stocks/{stock_code}/analysis/technical",
    "announcements": "/stocks/{stock_code}/news/announcements",
    "shareholders": "/stocks/{stock_code}/news/shareholders",
    "dragon_tiger": "/stocks/{stock_code}/news/dragon-tiger",
    "industry": "/stocks/{stock_code}/news/industry"
  },
  "status": "running",
  "timestamp": "2025-09-07T12:00:00.000Z"
}
```

#### GET `/health` - 健康检查
检查服务健康状况，包含数据库连接测试

**响应示例:**
```json
{
  "status": "healthy",
  "database": "connected",
  "akshare_status": "available",
  "timestamp": "2025-09-07T12:00:00.000Z"
}
```

### 1.2 分析类API

#### GET `/stocks/{stock_code}/analysis/fundamental` - 基本面分析

获取指定股票的完整基本面分析数据，包含80+财务指标和公司基本信息。专为n8n工作流和AI分析优化。

**Parameters:**
- `stock_code` (string, required): 股票代码，支持6位数字格式 (如: 000001, 600036)

**Response Schema:**
```json
{
  "stock_code": "string",
  "stock_name": "string", 
  "analysis_type": "fundamental",
  "data_source": "akshare_comprehensive",
  "update_time": "ISO-8601 timestamp",
  "basic_info": {
    "股票简称": "string",
    "总股本": "string",
    "流通股": "string",
    "最新": "number"
  },
  "financial_indicators": [
    {
      "选项": "string",
      "指标": "string", 
      "2023": "number|string",
      "2022": "number|string",
      "2021": "number|string"
    }
  ],
  "analysis_data": {
    "company_overview": {
      "stock_code": "string",
      "stock_name": "string",
      "total_shares": "number",
      "circulating_shares": "number",
      "current_price": "number"
    },
    "financial_metrics": {
      "revenue": "number",
      "net_profit": "number", 
      "total_assets": "number",
      "net_assets": "number",
      "eps": "number"
    }
  }
}
```

**Example Request:**
```bash
curl "http://35.77.54.203:3003/stocks/000001/analysis/fundamental"
```

**Example Response:**
```json
{
  "stock_code": "000001",
  "stock_name": "平安银行",
  "analysis_type": "fundamental",
  "data_source": "akshare_comprehensive",
  "update_time": "2025-09-03T10:30:00.000Z",
  "basic_info": {
    "股票简称": "平安银行",
    "总股本": "19405918198",
    "流通股": "19405918198"
  },
  "financial_indicators": [
    {
      "选项": "盈利能力",
      "指标": "营业总收入",
      "2023": "176543000000",
      "2022": "164521000000",
      "2021": "151234000000"
    }
  ],
  "analysis_data": {
    "company_overview": {
      "stock_code": "000001",
      "stock_name": "平安银行", 
      "total_shares": 19405918198,
      "current_price": 12.85
    },
    "financial_metrics": {
      "revenue": 176543000000,
      "net_profit": 37252000000,
      "total_assets": 4891234000000,
      "net_assets": 512431000000,
      "eps": 1.92
    }
  }
}
```

### 3. 技术面分析 / Technical Analysis

#### GET `/stocks/{stock_code}/analysis/technical`

获取指定股票的技术面分析数据，包含K线数据、实时行情和技术指标。

**Parameters:**
- `stock_code` (string, required): 股票代码

**Response Schema:**
```json
{
  "stock_code": "string",
  "stock_name": "string",
  "analysis_type": "technical",
  "data_source": "akshare_technical",
  "update_time": "ISO-8601 timestamp",
  "k_line_data": [
    {
      "日期": "YYYY-MM-DD",
      "开盘": "number",
      "收盘": "number", 
      "最高": "number",
      "最低": "number",
      "成交量": "number"
    }
  ],
  "real_time_data": {
    "最新": "number",
    "涨跌": "number",
    "涨幅": "number",
    "总手": "number"
  },
  "technical_indicators": {
    "涨跌幅": "number",
    "换手率": "number", 
    "量比": "number",
    "市盈率": "number",
    "市净率": "number"
  },
  "analysis_data": {
    "current_price": "number",
    "price_change": "number",
    "price_change_pct": "number",
    "volume": "number", 
    "turnover_rate": "number",
    "pe_ratio": "number",
    "pb_ratio": "number",
    "recent_high": "number",
    "recent_low": "number"
  }
}
```

**Example Request:**
```bash
curl "http://35.77.54.203:3003/stocks/000001/analysis/technical"
```

---

## 📰 消息面API / News APIs

### 4. 公司公告 / Company Announcements

#### GET `/stocks/{stock_code}/news/announcements`

获取指定股票的公司公告信息。

**Parameters:**
- `stock_code` (string, required): 股票代码

**Response Schema:**
```json
{
  "stock_code": "string",
  "data_source": "placeholder",
  "update_time": "ISO-8601 timestamp",
  "announcements": [],
  "note": "公司公告数据接口开发中，akshare相关接口暂不可用"
}
```

### 5. 股东变动 / Shareholder Changes

#### GET `/stocks/{stock_code}/news/shareholders`

获取指定股票的股东变动信息。

**Response Schema:**
```json
{
  "stock_code": "string",
  "data_source": "placeholder",
  "update_time": "ISO-8601 timestamp", 
  "shareholder_changes": [],
  "note": "股东变动数据接口开发中，akshare相关接口响应缓慢"
}
```

### 6. 龙虎榜数据 / Dragon Tiger List

#### GET `/stocks/{stock_code}/news/dragon-tiger`

获取指定股票的龙虎榜数据。

**Response Schema:**
```json
{
  "stock_code": "string",
  "data_source": "placeholder",
  "update_time": "ISO-8601 timestamp",
  "dragon_tiger_data": [],
  "note": "龙虎榜数据接口开发中，akshare相关接口暂不可用"
}
```

### 7. 行业新闻 / Industry News

#### GET `/stocks/{stock_code}/news/industry`

获取指定股票相关的行业新闻。

**Response Schema:**
```json
{
  "stock_code": "string", 
  "data_source": "placeholder",
  "update_time": "ISO-8601 timestamp",
  "industry_news": [],
  "note": "行业新闻数据接口开发中"
}
```

---

## 🚨 错误处理 / Error Handling

### 错误响应格式 / Error Response Format

所有API错误都返回以下格式：

```json
{
  "error": "错误描述信息"
}
```

### 常见错误码 / Common Error Codes

| HTTP状态码 | 错误描述 | 解决方法 |
|----------|--------|--------|
| 200 | 请求成功但返回error字段 | 检查股票代码是否正确 |
| 404 | 接口未找到 | 检查API路径是否正确 |
| 500 | 服务器内部错误 | 检查AKShare数据源或联系管理员 |

### 错误示例 / Error Examples

**无效股票代码:**
```json
{
  "error": "Stock 999999 financial data not found"
}
```

**数据获取失败:**
```json
{
  "error": "基本面分析失败: connection timeout"
}
```

---

## 🔧 使用说明 / Usage Guidelines

### 1. 股票代码格式 / Stock Code Format

- **中国A股**: 6位数字格式
  - 深交所: 000001-399999
  - 上交所: 600000-699999

### 2. 数据更新频率 / Data Update Frequency

- **基本面数据**: 每日更新，缓存30分钟
- **技术面数据**: 实时更新，缓存1分钟
- **消息面数据**: 当前为占位符，未实现

### 3. 最佳实践 / Best Practices

- 在n8n工作流中使用这些API端点
- 实现适当的错误处理和重试机制
- 避免频繁调用同一股票数据（利用缓存）
- 监控API响应时间和错误率

### 4. 性能考虑 / Performance Considerations

- 技术面分析API可能需要5-10秒响应时间
- 建议设置30秒的请求超时时间
- 并行调用多个端点时注意服务器负载

---

## 🔒 安全和限制 / Security & Limitations

### 访问控制
- 当前无认证要求，仅限服务器IP访问
- 建议生产环境配置防火墙规则

### 使用限制
- 消息面API当前为占位符实现
- AKShare数据源可能存在访问限制
- 建议合理控制请求频率

### 数据准确性
- 数据来源于AKShare，准确性依赖数据源
- 建议在关键决策前验证数据准确性
- API返回时间戳标识数据更新时间