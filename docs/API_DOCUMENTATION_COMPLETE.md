# Stock Analysis API 文档

生成时间: 2025-09-08 07:57:42  
服务地址: http://35.77.54.203:3003  
文档地址: http://35.77.54.203:3003/docs

## 服务概览
- **标题**: Stock Analysis API
- **版本**: 2.0.0  
- **描述**: Complete stock analysis API service for n8n workflows

## API 端点列表

### 基础数据API

#### `GET /api/financial-abstract/{stock_code}`

**功能**: Get Financial Abstract

**参数**:
- `stock_code` (string, 必需): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

#### `GET /api/stock-info/{stock_code}`

**功能**: Get Stock Info

**参数**:
- `stock_code` (string, 必需): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

#### `GET /api/k-line/{stock_code}`

**功能**: Get K Line Data

**参数**:
- `stock_code` (string, 必需): 无描述
- `period` (string, 可选): 无描述
- `days` (integer, 可选): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

#### `GET /api/technical-indicators/{stock_code}`

**功能**: Get Technical Indicators

**参数**:
- `stock_code` (string, 必需): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

#### `GET /http%3A//35.77.54.203%3A3003/openapi.json`

**功能**: Openapi Encoded

**描述**: 处理浏览器URL编码的openapi.json请求

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

### 分析类API

#### `GET /stocks/{stock_code}/analysis/fundamental`

**功能**: Get Fundamental Analysis

**描述**: 基本面分析API端点 / Fundamental analysis API endpoint
对应workflow中的基本面分析HTTP请求

**参数**:
- `stock_code` (string, 必需): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

#### `GET /stocks/{stock_code}/analysis/technical`

**功能**: Get Technical Analysis

**描述**: 技术面分析API端点 / Technical analysis API endpoint
对应workflow中的技术面分析HTTP请求

**参数**:
- `stock_code` (string, 必需): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

### 消息面API

#### `GET /stocks/{stock_code}/news/announcements`

**功能**: Get Company Announcements

**描述**: 公司公告API端点 / Company Announcements API
由于akshare公告接口限制，提供基于财务报表的报告期信息

**参数**:
- `stock_code` (string, 必需): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

#### `GET /stocks/{stock_code}/news/shareholders`

**功能**: Get Shareholder Changes

**描述**: 股东变动API端点

**参数**:
- `stock_code` (string, 必需): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

#### `GET /stocks/{stock_code}/news/dragon-tiger`

**功能**: Get Dragon Tiger List

**描述**: 龙虎榜API端点 / Dragon Tiger List API
获取指定股票在指定天数内的龙虎榜记录

**参数**:
- `stock_code` (string, 必需): 无描述
- `days` (integer, 可选): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

#### `GET /stocks/{stock_code}/news/industry`

**功能**: Get Industry News

**描述**: 行业新闻API端点

**参数**:
- `stock_code` (string, 必需): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

### 高级分析API

#### `GET /api/comprehensive-financial/{stock_code}`

**功能**: Get Comprehensive Financial Indicators

**描述**: 获取全面财务指标数据 - 包含更多财务报表指标
Get comprehensive financial indicators with enhanced metrics

**参数**:
- `stock_code` (string, 必需): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

#### `GET /api/financial-comparison/{stock_code}`

**功能**: Get Financial Comparison

**描述**: 财务指标趋势对比分析
Financial indicators trend comparison analysis

**参数**:
- `stock_code` (string, 必需): 无描述
- `periods` (integer, 可选): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

#### `GET /api/fund-flow/{stock_code}`

**功能**: Get Fund Flow Analysis

**描述**: 获取资金流向数据 / Get fund flow data
包含主力资金、大单、中单、小单的净流入数据和统计分析

**参数**:
- `stock_code` (string, 必需): 无描述

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

### 系统API

#### `GET /`

**功能**: Root

**示例**:
```bash
curl "http://35.77.54.203:3003/"
```

---

## 使用说明

### 1. 股票代码格式
使用6位数字股票代码，如：
- `000001` - 平安银行
- `600519` - 贵州茅台  
- `000858` - 五粮液

### 2. 响应格式
所有API都返回JSON格式数据，基本结构：
```json
{
  "stock_code": "000001",
  "data_source": "akshare_comprehensive", 
  "update_time": "2025-09-08T07:03:28.201924",
  "data": { ... }
}
```

### 3. 错误处理
错误时返回包含 `error` 字段的JSON：
```json
{
  "error": "错误描述信息"
}
```

### 4. 数据源说明
- **akshare**: 主要数据提供商，提供A股实时和历史数据
- **更新频率**: 大部分数据实时更新，部分财务数据按季度更新

## 错误码说明

| 状态码 | 说明 |
|-------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |

## 开发示例

### Python调用示例
```python
import requests
import json

# 获取股票基本面分析
response = requests.get('http://35.77.54.203:3003/stocks/000001/analysis/fundamental')
if response.status_code == 200:
    data = response.json()
    print(f"股票名称: {data.get('stock_name')}")
    print(f"更新时间: {data.get('update_time')}")
else:
    print(f"请求失败: {response.status_code}")
```

### JavaScript调用示例
```javascript
// 获取技术面分析
fetch('http://35.77.54.203:3003/stocks/000001/analysis/technical')
  .then(response => response.json())
  .then(data => {
    console.log('股票代码:', data.stock_code);
    console.log('分析数据:', data.analysis_data);
  })
  .catch(error => {
    console.error('请求失败:', error);
  });
```

## 性能说明

- **响应时间**: 大部分API响应时间在1-3秒
- **并发限制**: 建议单个IP每分钟不超过60次请求
- **数据缓存**: 部分数据有短期缓存，避免频繁重复请求

## 联系信息

- **项目地址**: https://github.com/ocean5tech/stock_services
- **服务器**: 35.77.54.203:3003
- **技术支持**: 请通过GitHub Issues联系

---
*此文档由API自动生成，最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
