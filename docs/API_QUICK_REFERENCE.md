# Stock Analysis API - 快速参考

服务地址: http://35.77.54.203:3003
生成时间: 2025-09-08 07:57:42

## 主要API端点

### 基础数据API
- `GET /api/financial-abstract/{stock_code}` - Get Financial Abstract
- `GET /api/stock-info/{stock_code}` - Get Stock Info
- `GET /api/k-line/{stock_code}` - Get K Line Data
- `GET /api/technical-indicators/{stock_code}` - Get Technical Indicators
- `GET /http%3A//35.77.54.203%3A3003/openapi.json` - Openapi Encoded

### 分析类API
- `GET /stocks/{stock_code}/analysis/fundamental` - Get Fundamental Analysis
- `GET /stocks/{stock_code}/analysis/technical` - Get Technical Analysis

### 消息面API
- `GET /stocks/{stock_code}/news/announcements` - Get Company Announcements
- `GET /stocks/{stock_code}/news/shareholders` - Get Shareholder Changes
- `GET /stocks/{stock_code}/news/dragon-tiger` - Get Dragon Tiger List
- `GET /stocks/{stock_code}/news/industry` - Get Industry News

### 高级分析API
- `GET /api/comprehensive-financial/{stock_code}` - Get Comprehensive Financial Indicators
- `GET /api/financial-comparison/{stock_code}` - Get Financial Comparison
- `GET /api/fund-flow/{stock_code}` - Get Fund Flow Analysis

### 系统API
- `GET /` - Root

