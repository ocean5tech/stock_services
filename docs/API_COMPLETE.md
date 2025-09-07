# Stock Services API 完整文档

## 📖 概览 / Overview

本系统提供三个独立的股票服务API，部署在服务器IP `35.77.54.203` 上，为股票数据分析、投资决策和自动化工作流提供全面支持。

### 🏗️ 服务架构

| 服务名称 | 端口 | Base URL | 主要功能 | Swagger文档 |
|---------|------|----------|----------|------------|
| 中国股票分析服务 | 3003 | `http://35.77.54.203:3003` | A股完整分析+AI工作流 | `/docs` |
| 美国股票服务 | 3004 | `http://35.77.54.203:3004` | 美股实时数据 | `/docs` |
| 中国期货服务 | 3005 | `http://35.77.54.203:3005` | 期货合约数据 | `/docs` |

### 🎯 核心特性

- **🤖 AI集成**: 为n8n工作流优化的Claude AI分析
- **📊 多维分析**: 基本面+技术面+消息面三维股票分析
- **🔄 实时数据**: 基于AKShare的实时金融数据
- **💾 数据持久化**: PostgreSQL数据库存储
- **🚀 高性能**: FastAPI异步框架，支持高并发

---

## 1. 中国股票分析服务 (端口 3003)

### 1.1 服务概述

专为股票投资分析和AI工作流设计的核心服务，提供中国A股的全方位数据分析。

**特色功能:**
- 🎯 **专业投资分析**: 80+财务指标，全面基本面分析
- 🔍 **技术面分析**: K线数据、技术指标、实时行情
- 📰 **消息面整合**: 公司公告、股东变动、行业新闻
- 🤖 **AI工作流支持**: 为n8n工作流和Claude AI优化

### 1.2 健康检查端点

#### `GET /` - 服务状态检查
返回服务状态和所有可用端点

**示例请求:**
```bash
curl http://35.77.54.203:3003/
```

**响应示例:**
```json
{
  "message": "股票分析API服务正常运行",
  "service": "comprehensive_stock_api",
  "version": "2.0.0",
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

#### `GET /health` - 健康检查
检查服务和依赖系统健康状况

**响应示例:**
```json
{
  "status": "healthy",
  "database": "connected",
  "akshare_status": "available",
  "timestamp": "2025-09-07T12:00:00.000Z"
}
```

### 1.3 分析类API

#### `GET /stocks/{stock_code}/analysis/fundamental` - 基本面分析 ⭐

获取股票的完整基本面分析数据，包含80+财务指标。

**参数:**
- `stock_code` (string, required): 6位股票代码 (如: 000001, 600036)

**示例请求:**
```bash
curl "http://35.77.54.203:3003/stocks/000001/analysis/fundamental"
```

**响应数据结构:**
```json
{
  "stock_code": "000001",
  "stock_name": "平安银行", 
  "analysis_type": "fundamental",
  "data_source": "akshare_comprehensive",
  "update_time": "2025-09-07T12:00:00.000Z",
  "basic_info": {
    "股票简称": "平安银行",
    "总股本": "19405918198",
    "流通股": "19405918198",
    "最新": "12.50"
  },
  "financial_indicators": [
    {
      "选项": "盈利能力",
      "指标": "营业总收入",
      "2023": "176543000000.0",
      "2022": "164521000000.0",
      "2021": "151234000000.0"
    }
    // ... 80+ 财务指标
  ],
  "analysis_data": {
    "company_overview": {
      "stock_code": "000001",
      "stock_name": "平安银行",
      "total_shares": 19405918198,
      "current_price": 12.50
    },
    "financial_metrics": {
      "revenue": 176543000000,
      "net_profit": 37252000000,
      "total_assets": 4891234000000,
      "net_assets": 512431000000,
      "eps": 1.92,
      "roe": 15.2,
      "roa": 1.8
    }
  }
}
```

#### `GET /stocks/{stock_code}/analysis/technical` - 技术面分析 ⭐

获取股票的技术面分析数据，包含K线数据和实时技术指标。

**参数:**
- `stock_code` (string, required): 股票代码

**示例请求:**
```bash
curl "http://35.77.54.203:3003/stocks/000001/analysis/technical"
```

**响应数据结构:**
```json
{
  "stock_code": "000001",
  "stock_name": "平安银行",
  "analysis_type": "technical",
  "data_source": "akshare_technical",
  "update_time": "2025-09-07T12:00:00.000Z",
  "k_line_data": [
    {
      "日期": "2025-09-07",
      "开盘": 12.45,
      "收盘": 12.50,
      "最高": 12.62,
      "最低": 12.38,
      "成交量": 8500000,
      "成交额": 106250000.0,
      "涨跌幅": 0.40,
      "涨跌额": 0.05,
      "换手率": 0.44
    }
    // ... 最近60天K线数据
  ],
  "real_time_data": {
    "最新": 12.50,
    "涨跌": 0.05,
    "涨幅": 0.40,
    "总手": 850000,
    "现手": 120,
    "买一": 12.49,
    "卖一": 12.50
  },
  "technical_indicators": {
    "涨跌幅": 0.40,
    "换手率": 0.44,
    "量比": 0.85,
    "市盈率": 8.5,
    "市净率": 0.95
  },
  "analysis_data": {
    "current_price": 12.50,
    "price_change": 0.05,
    "price_change_pct": 0.40,
    "volume": 8500000,
    "turnover_rate": 0.44,
    "pe_ratio": 8.5,
    "pb_ratio": 0.95,
    "recent_high": 12.95,
    "recent_low": 11.85
  }
}
```

### 1.4 消息面API

#### `GET /stocks/{stock_code}/news/announcements` - 公司公告

**注意**: 当前为占位符实现，AKShare相关接口暂不稳定

**响应示例:**
```json
{
  "stock_code": "000001",
  "data_source": "placeholder", 
  "update_time": "2025-09-07T12:00:00.000Z",
  "announcements": [],
  "note": "公司公告数据接口开发中，akshare相关接口暂不可用"
}
```

#### `GET /stocks/{stock_code}/news/shareholders` - 股东变动
#### `GET /stocks/{stock_code}/news/dragon-tiger` - 龙虎榜数据  
#### `GET /stocks/{stock_code}/news/industry` - 行业新闻

以上端点目前均为占位符实现，返回类似结构的空数据。

---

## 2. 美国股票服务 (端口 3004)

### 2.1 服务概述

提供美国股票市场的实时数据和基本信息查询服务。

**核心功能:**
- 📈 **美股实时行情**: NASDAQ, NYSE, AMEX股票数据
- 🏢 **公司信息**: 财务指标、行业分类、交易所信息
- 🔍 **多维筛选**: 按行业、交易所、市值等筛选
- 📊 **统计分析**: 市场统计和数据概览

### 2.2 主要端点

#### `GET /` - 服务状态
```json
{
  "service": "US Stock Service",
  "status": "running",
  "version": "1.0.0",
  "server_ip": "35.77.54.203",
  "port": 3004
}
```

#### `GET /stocks/{stock_symbol}` - 获取美股详情

**参数:**
- `stock_symbol`: 美股代码 (如: AAPL, MSFT, GOOGL)
- `refresh`: 是否强制刷新 (可选)

**示例请求:**
```bash
curl "http://35.77.54.203:3004/stocks/AAPL"
```

**响应示例:**
```json
{
  "stock_symbol": "AAPL",
  "stock_name_en": "Apple Inc.",
  "stock_name_cn": "苹果公司", 
  "current_price": 175.25,
  "price_change": 2.50,
  "price_change_pct": 1.45,
  "open_price": 173.50,
  "close_price": 172.75,
  "high_price": 176.00,
  "low_price": 172.50,
  "volume": 52000000,
  "market_cap": 2700000000000,
  "pe_ratio": 28.5,
  "sector": "Technology",
  "exchange": "NASDAQ",
  "last_updated": "2025-09-07T12:00:00.000Z"
}
```

#### `GET /stocks` - 美股列表

支持分页和多维度筛选：
- `sector`: 行业筛选 
- `exchange`: 交易所筛选
- `page`, `limit`: 分页参数

#### `GET /sectors` - 行业列表
#### `GET /exchanges` - 交易所列表
#### `GET /stats` - 美股统计信息

---

## 3. 中国期货服务 (端口 3005)

### 3.1 服务概述

提供中国期货市场的全面数据服务，覆盖上海期货交易所、大连商品交易所、郑州商品交易所等主要期货市场。

**核心功能:**
- 📊 **期货实时行情**: 实时价格、成交量、持仓量
- 📋 **合约信息**: 合约规格、交割月份、交易单位
- 🏢 **交易所数据**: SHFE, DCE, CZCE, CFFEX, INE
- 🔍 **标的资产分类**: 金属、农产品、能源、金融等

### 3.2 主要端点

#### `GET /` - 服务状态
```json
{
  "service": "Chinese Futures Service", 
  "status": "running",
  "version": "1.0.0",
  "server_ip": "35.77.54.203",
  "port": 3005
}
```

#### `GET /futures/{futures_code}` - 获取期货详情

**参数:**
- `futures_code`: 期货代码 (如: cu2410, al2410, IF2410)
- `refresh`: 是否强制刷新

**示例请求:**
```bash
curl "http://35.77.54.203:3005/futures/cu2410"
```

**响应示例:**
```json
{
  "futures_code": "cu2410",
  "futures_name": "沪铜2410",
  "contract_month": "2024-10",
  "underlying_asset": "铜",
  "current_price": 72500,
  "price_change": 300,
  "price_change_pct": 0.42,
  "open_price": 72200,
  "high_price": 72800, 
  "low_price": 72000,
  "settlement_price": 72450,
  "volume": 125000,
  "open_interest": 89000,
  "contract_size": 5,
  "tick_size": 10,
  "exchange": "SHFE",
  "trading_unit": "5吨/手",
  "delivery_month": "2024-10",
  "last_updated": "2025-09-07T12:00:00.000Z"
}
```

#### `GET /futures` - 期货列表

支持多维度筛选：
- `exchange`: 交易所筛选
- `underlying_asset`: 标的资产筛选  
- `active_only`: 只显示活跃合约

#### `GET /exchanges` - 期货交易所列表

**响应示例:**
```json
{
  "exchanges": [
    {
      "code": "SHFE",
      "name_cn": "上海期货交易所",
      "name_en": "Shanghai Futures Exchange"
    },
    {
      "code": "DCE", 
      "name_cn": "大连商品交易所",
      "name_en": "Dalian Commodity Exchange"
    },
    {
      "code": "CZCE",
      "name_cn": "郑州商品交易所",
      "name_en": "Zhengzhou Commodity Exchange" 
    },
    {
      "code": "CFFEX",
      "name_cn": "中国金融期货交易所",
      "name_en": "China Financial Futures Exchange"
    },
    {
      "code": "INE",
      "name_cn": "上海国际能源交易中心",
      "name_en": "Shanghai International Energy Exchange"
    }
  ],
  "total_count": 5
}
```

#### `GET /assets` - 标的资产列表
#### `GET /contracts/{underlying_asset}` - 按标的资产获取合约
#### `GET /stats` - 期货统计信息

---

## 🚨 错误处理

### 标准错误格式

所有服务的错误都返回统一格式：

```json
{
  "error": "错误描述信息",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-09-07T12:00:00.000Z"
}
```

### 常见HTTP状态码

| 状态码 | 含义 | 常见原因 | 解决方法 |
|-------|------|---------|---------|
| 200 | 成功但有业务错误 | 股票代码不存在 | 检查股票代码格式 |
| 404 | 资源未找到 | API路径错误 | 检查API端点路径 |
| 422 | 参数验证失败 | 参数格式不正确 | 检查参数类型和格式 |
| 500 | 服务器内部错误 | 数据源异常 | 重试或联系管理员 |

### 错误示例

**无效股票代码:**
```json
{
  "error": "Stock 999999 not found",
  "error_code": "STOCK_NOT_FOUND"
}
```

**数据获取超时:**
```json
{
  "error": "AKShare数据获取超时，请稍后重试",
  "error_code": "DATA_SOURCE_TIMEOUT"
}
```

---

## 🔧 使用指南

### 1. n8n工作流集成

**推荐配置:**
- **超时时间**: 30秒 (技术面分析可能需要较长时间)
- **重试次数**: 3次
- **重试间隔**: 5秒

**工作流示例:**
```json
{
  "nodes": [
    {
      "name": "基本面分析",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://35.77.54.203:3003/stocks/{{$json['stock_code']}}/analysis/fundamental",
        "timeout": 30000,
        "options": {
          "retry": {
            "count": 3,
            "interval": 5000
          }
        }
      }
    }
  ]
}
```

### 2. 数据缓存策略

| 数据类型 | 缓存时间 | 更新建议 |
|---------|---------|----------|
| 基本面数据 | 30分钟 | 交易日每日更新 |
| 实时行情 | 1分钟 | 实时刷新 |
| 财务指标 | 1小时 | 财报发布后更新 |
| 期货数据 | 3分钟 | 实时刷新 |

### 3. 最佳实践

#### API调用优化
```bash
# 并行获取多维度分析数据
curl "http://35.77.54.203:3003/stocks/000001/analysis/fundamental" &
curl "http://35.77.54.203:3003/stocks/000001/analysis/technical" &
wait
```

#### 批量处理
```bash
# 批量获取多只股票数据
stocks=("000001" "600036" "000002")
for stock in "${stocks[@]}"; do
  curl "http://35.77.54.203:3003/stocks/$stock/analysis/fundamental" &
done
wait
```

### 4. 性能监控

**健康检查脚本:**
```bash
#!/bin/bash
services=("3003" "3004" "3005")
for port in "${services[@]}"; do
  response=$(curl -s "http://35.77.54.203:$port/health")
  echo "Port $port: $response"
done
```

---

## 📊 数据质量

### 数据来源
- **AKShare**: 主要金融数据提供商
- **实时性**: 延迟1-5分钟
- **准确性**: 依赖上游数据源质量
- **覆盖范围**: 中国A股、美股、期货全覆盖

### 数据验证
- ✅ **自动校验**: 数据格式和范围检查
- ✅ **异常处理**: 异常数据自动过滤
- ✅ **时间戳**: 所有数据包含更新时间
- ✅ **数据源标识**: 明确标识数据来源

---

## 🔒 安全和合规

### 访问控制
- 服务器IP限制: 35.77.54.203
- 无需身份认证 (内网服务)
- 请求日志记录

### 数据安全
- SQL注入防护
- 参数验证
- 敏感信息过滤
- HTTPS支持 (生产环境)

### 使用限制
- 单IP请求频率限制
- 数据使用遵循相关法规
- 仅用于投资分析和研究

---

## 🚀 更新日志

### v2.0.0 (2025-09-07)
- ✅ 完善API文档结构
- ✅ 增强错误处理机制
- ✅ 优化数据返回格式
- ✅ 添加更多技术指标

### v1.0.0 (2025-08-27)
- ✅ 基础三服务架构
- ✅ PostgreSQL数据存储  
- ✅ AKShare数据集成
- ✅ n8n工作流支持

---

## 📞 技术支持

**服务监控**: http://35.77.54.203:3003/health
**问题反馈**: GitHub Issues  
**API文档**: http://35.77.54.203:3003/docs

**紧急联系**: 如服务异常，请检查服务状态或重启相关服务。