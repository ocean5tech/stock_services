# 股票服务API文档 / Stock Services API Documentation

## 项目概述 / Project Overview

本项目提供三个独立的股票服务API，运行在服务器IP `35.77.54.203` 上，使用PostgreSQL数据库存储数据，通过akshare库获取实时金融数据。

This project provides three independent stock service APIs, running on server IP `35.77.54.203`, using PostgreSQL database for data storage, and fetching real-time financial data through the akshare library.

### 服务架构 / Service Architecture

- **中国股票服务** / Chinese Stock Service: Port 3003
- **美国股票服务** / US Stock Service: Port 3004
- **中国期货服务** / Chinese Futures Service: Port 3005

## 基础信息 / Basic Information

### 服务器配置 / Server Configuration
- **服务器IP**: 35.77.54.203
- **数据库**: PostgreSQL
- **框架**: FastAPI with Python
- **数据源**: akshare库提供的实时金融数据

### 通用特性 / Common Features
- RESTful API设计
- 自动API文档 (Swagger UI)
- 数据库连接池
- 错误处理和日志记录
- 数据缓存机制
- 输入验证和安全性

---

## 中国股票服务 API / Chinese Stock Service API

**基础URL**: `http://35.77.54.203:3003`

### 核心端点 / Core Endpoints

#### 1. 服务状态检查 / Service Health Check
```
GET /
```
**响应示例 / Response Example**:
```json
{
    "service": "Chinese Stock Service",
    "status": "running",
    "version": "1.0.0",
    "server_ip": "35.77.54.203",
    "port": 3003,
    "timestamp": "2025-08-27T08:49:05.223662"
}
```

#### 2. 健康检查 / Health Check
```
GET /health
```
**响应示例 / Response Example**:
```json
{
    "status": "healthy",
    "database": "connected",
    "timestamp": "2025-08-27T08:49:26.016871"
}
```

#### 3. 获取指定股票详细信息 / Get Specific Stock Details
```
GET /stocks/{stock_code}
```

**参数 / Parameters**:
- `stock_code` (路径参数): 股票代码，如 000001, 600036
- `refresh` (查询参数): 是否强制刷新数据 (default: false)

**响应示例 / Response Example**:
```json
{
    "stock_code": "000001",
    "stock_name_cn": "平安银行",
    "stock_name_en": "Ping An Bank",
    "company_background": "中国平安银行股份有限公司...",
    "current_price": 12.50,
    "price_change": 0.15,
    "price_change_pct": 1.22,
    "open_price": 12.40,
    "close_price": 12.35,
    "high_price": 12.60,
    "low_price": 12.30,
    "volume": 15000000,
    "turnover": 187500000,
    "market_cap": 2500000000,
    "total_shares": 200000000,
    "pe_ratio": 8.5,
    "pb_ratio": 0.85,
    "is_active": true,
    "last_updated": "2025-08-27T08:49:05.223662",
    "created_at": "2025-08-27T08:49:05.223662"
}
```

#### 4. 获取股票列表 / Get Stock List
```
GET /stocks
```

**查询参数 / Query Parameters**:
- `page`: 页码 (default: 1)
- `limit`: 每页数量 (default: 20, max: 100)
- `search`: 搜索关键词（股票代码或名称）
- `sort_by`: 排序字段 (default: stock_code)
- `sort_order`: 排序顺序 asc/desc (default: asc)
- `active_only`: 只显示活跃股票 (default: true)

#### 5. 刷新股票数据 / Refresh Stock Data
```
POST /stocks/{stock_code}/refresh
```
强制从akshare刷新指定股票的最新数据

#### 6. 删除股票数据 / Delete Stock Data
```
DELETE /stocks/{stock_code}
```
软删除指定股票（设置为不活跃状态）

#### 7. 统计信息 / Statistics
```
GET /stats
```
获取服务统计信息，包括股票数量、API调用次数等

---

## 美国股票服务 API / US Stock Service API

**基础URL**: `http://35.77.54.203:3004`

### 核心端点 / Core Endpoints

#### 1. 获取指定美股详细信息 / Get US Stock Details
```
GET /stocks/{stock_symbol}
```

**参数 / Parameters**:
- `stock_symbol`: 股票代码，如 AAPL, MSFT, GOOGL
- `refresh`: 是否强制刷新数据

**响应示例 / Response Example**:
```json
{
    "stock_symbol": "AAPL",
    "stock_name_en": "Apple Inc.",
    "stock_name_cn": "苹果公司",
    "company_background": "Apple Inc. is an American multinational technology company...",
    "current_price": 185.50,
    "price_change": 2.30,
    "price_change_pct": 1.26,
    "open_price": 183.20,
    "close_price": 183.20,
    "high_price": 186.00,
    "low_price": 182.50,
    "volume": 45000000,
    "turnover": 8325000000,
    "market_cap": 2900000000000,
    "total_shares": 15640000000,
    "pe_ratio": 28.5,
    "pb_ratio": 42.8,
    "sector": "Technology",
    "exchange": "NASDAQ",
    "is_active": true,
    "last_updated": "2025-08-27T08:49:05.223662",
    "created_at": "2025-08-27T08:49:05.223662"
}
```

#### 2. 获取行业列表 / Get Sectors List
```
GET /sectors
```
返回所有可用行业列表

#### 3. 获取交易所列表 / Get Exchanges List
```
GET /exchanges
```
返回所有交易所列表（NYSE, NASDAQ等）

#### 4. 其他端点 / Other Endpoints
- `GET /stocks` - 股票列表（支持行业和交易所筛选）
- `POST /stocks/{stock_symbol}/refresh` - 刷新股票数据
- `DELETE /stocks/{stock_symbol}` - 删除股票数据
- `GET /stats` - 统计信息

---

## 中国期货服务 API / Chinese Futures Service API

**基础URL**: `http://35.77.54.203:3005`

### 核心端点 / Core Endpoints

#### 1. 获取指定期货详细信息 / Get Futures Details
```
GET /futures/{futures_code}
```

**参数 / Parameters**:
- `futures_code`: 期货代码，如 cu2410, al2410, IF2410
- `refresh`: 是否强制刷新数据

**响应示例 / Response Example**:
```json
{
    "futures_code": "cu2410",
    "futures_name": "沪铜2410",
    "contract_month": "2024-10",
    "underlying_asset": "铜",
    "current_price": 72500,
    "price_change": 250,
    "price_change_pct": 0.35,
    "open_price": 72300,
    "close_price": 72250,
    "high_price": 72800,
    "low_price": 72100,
    "settlement_price": 72400,
    "volume": 125000,
    "open_interest": 85000,
    "contract_size": 5.0,
    "tick_size": 10.0,
    "exchange": "SHFE",
    "trading_unit": "5吨/手",
    "delivery_month": "2024年10月",
    "is_active": true,
    "last_updated": "2025-08-27T08:49:05.223662",
    "created_at": "2025-08-27T08:49:05.223662"
}
```

#### 2. 获取期货交易所列表 / Get Exchanges List
```
GET /exchanges
```

**响应示例 / Response Example**:
```json
{
    "exchanges": [
        {
            "code": "SHFE",
            "name_cn": "上海期货交易所",
            "name_en": "SHFE"
        },
        {
            "code": "DCE",
            "name_cn": "大连商品交易所",
            "name_en": "DCE"
        },
        {
            "code": "CZCE",
            "name_cn": "郑州商品交易所",
            "name_en": "CZCE"
        },
        {
            "code": "CFFEX",
            "name_cn": "中国金融期货交易所",
            "name_en": "CFFEX"
        }
    ],
    "total_count": 4
}
```

#### 3. 获取标的资产列表 / Get Underlying Assets
```
GET /assets
```
返回所有标的资产列表（铜、铝、黄金等）

#### 4. 获取指定标的资产的合约 / Get Contracts by Asset
```
GET /contracts/{underlying_asset}
```
获取指定标的资产的所有合约

#### 5. 其他端点 / Other Endpoints
- `GET /futures` - 期货列表（支持交易所和标的资产筛选）
- `POST /futures/{futures_code}/refresh` - 刷新期货数据
- `DELETE /futures/{futures_code}` - 删除期货数据
- `GET /stats` - 统计信息

---

## API文档访问 / API Documentation Access

每个服务都提供自动生成的Swagger UI文档：

Each service provides auto-generated Swagger UI documentation:

- **中国股票服务文档**: http://35.77.54.203:3003/docs
- **美国股票服务文档**: http://35.77.54.203:3004/docs
- **中国期货服务文档**: http://35.77.54.203:3005/docs

---

## 错误处理 / Error Handling

### 常见错误码 / Common Error Codes

- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 内部服务器错误
- `503 Service Unavailable`: 服务不可用

### 错误响应格式 / Error Response Format

```json
{
    "detail": "股票代码 000999 不存在或获取数据失败 / Stock code 000999 not found or failed to fetch data"
}
```

---

## 数据缓存策略 / Data Caching Strategy

- **股票数据缓存时间**: 5分钟
- **期货数据缓存时间**: 3分钟
- **强制刷新**: 使用 `refresh=true` 参数

## 安全性 / Security

- 输入验证和SQL注入防护
- 连接池管理
- 错误信息脱敏
- API调用日志记录

## 性能优化 / Performance Optimization

- 数据库连接池
- 数据缓存机制
- 异步处理
- 查询优化

---

## 部署和运维 / Deployment and Operations

### 启动服务 / Start Services
```bash
./deploy.sh
```

### 停止服务 / Stop Services
```bash
./stop_services.sh
```

### 监控服务 / Monitor Services
```bash
./monitor.sh                 # 一次性检查
./monitor.sh --watch         # 持续监控
./monitor.sh --auto-restart  # 自动重启异常服务
```

### 日志位置 / Log Locations
- 中国股票服务: `./logs/chinese_stock.log`
- 美国股票服务: `./logs/us_stock.log`
- 中国期货服务: `./logs/futures.log`

---

## 数据库表结构 / Database Schema

### 中国股票表 (chinese_stocks)
- `stock_code` (Primary Key): 股票代码
- `stock_name_cn`: 中文名称
- `stock_name_en`: 英文名称
- `current_price`: 当前价格
- `price_change`: 涨跌额
- `price_change_pct`: 涨跌幅百分比
- `volume`: 成交量
- `market_cap`: 市值
- 其他财务指标...

### 美国股票表 (us_stocks)
- `stock_symbol` (Primary Key): 股票代码
- `stock_name_en`: 英文名称
- `stock_name_cn`: 中文名称
- `sector`: 行业
- `exchange`: 交易所
- 价格和财务指标...

### 中国期货表 (chinese_futures)
- `futures_code` (Primary Key): 期货代码
- `futures_name`: 期货名称
- `underlying_asset`: 标的资产
- `contract_month`: 合约月份
- `exchange`: 交易所
- `contract_size`: 合约规模
- 价格和交易数据...

### API日志表 (api_logs)
- `id`: 自增主键
- `service_type`: 服务类型
- `endpoint`: API端点
- `response_time`: 响应时间
- `created_at`: 创建时间

---

## 联系信息 / Contact Information

如有问题或需要技术支持，请联系开发团队。

For questions or technical support, please contact the development team.

**项目GitHub地址**: https://github.com/ocean5tech/stock_services