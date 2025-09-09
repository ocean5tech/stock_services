# 股票分析API - 完整测试用例清单

**最后更新**: 2025-09-09  
**用途**: API发布前必须完成的完整测试清单  
**测试股票代码**: 603993（洛阳钼业）

## 🎯 测试目标

确保所有API端点的每个数据项都有有效值，发现并修复数据缺失、格式错误、功能异常等问题。

## ✅ 测试清单

### 1. 核心数据API测试

#### 1.1 统一股票信息 `GET /stocks/{stock_code}`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993" | jq '.' | head -50
```
**必须验证的数据项**:
- [ ] `stock_code`: 股票代码正确
- [ ] `stock_name`: 股票名称有值
- [ ] `data_source`: 数据来源标识
- [ ] `cache_info.cached`: 缓存状态
- [ ] `cache_info.cache_time`: 缓存时间
- [ ] `data.basic_info.*`: 所有基本信息字段有值
- [ ] `data.current_price.*`: 所有价格字段有值且格式正确
- [ ] `data.key_metrics.*`: 所有关键指标有值
- [ ] `data.trading_status.*`: 交易状态信息完整

**预期结果**: 所有字段都有有效值，数值类型正确

#### 1.2 公司概况 `GET /stocks/{stock_code}/profile`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/profile" | jq '.' | head -30
```
**必须验证的数据项**:
- [ ] `company_info.*`: 公司基本信息完整
- [ ] `business_info.*`: 业务信息（可能为空但结构正确）
- [ ] `financial_summary.*`: 财务摘要数据
- [ ] `raw_profile_data`: 原始数据存在

**预期结果**: 基础公司信息完整，业务信息允许部分为空

#### 1.3 基本面分析 `GET /stocks/{stock_code}/analysis/fundamental`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/analysis/fundamental" | jq '.' | head -30
```
**必须验证的数据项**:
- [ ] `analysis_type`: "fundamental"
- [ ] `basic_info.*`: 基本信息完整
- [ ] `financial_indicators`: 数组存在且有数据
- [ ] 每个指标项包含多个季度数据
- [ ] 数值类型正确（数字字段为数值型）

**预期结果**: 财务指标数据丰富，多季度数据完整

#### 1.4 技术面分析 `GET /stocks/{stock_code}/analysis/technical`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/analysis/technical" | jq '.' | head -30
```
**必须验证的数据项**:
- [ ] `analysis_type`: "technical"
- [ ] `k_line_data`: 数组存在且有数据
- [ ] K线数据包含: 日期、开盘、收盘、最高、最低、成交量
- [ ] 日期格式正确
- [ ] 数值类型正确

**预期结果**: K线数据完整，技术指标计算正确

#### 1.5 历史价格 `GET /stocks/{stock_code}/historical/prices`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/historical/prices" | jq '.' | head -30
```
**必须验证的数据项**:
- [ ] `period_info.days_requested`: 请求天数
- [ ] `period_info.actual_records`: 实际返回记录数
- [ ] `statistics.*`: 统计信息完整
- [ ] `historical_data`: 历史数据数组
- [ ] 每条记录包含完整的OHLCV数据

**预期结果**: 历史价格数据完整，统计信息准确

#### 1.6 历史财务 `GET /stocks/{stock_code}/historical/financial`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/historical/financial" | jq '.' | head -30
```
**必须验证的数据项**:
- [ ] `analysis_info.periods_analyzed`: 分析期数（应为8）
- [ ] `quarterly_data`: 季度数据（应有8个季度）
- [ ] `trend_analysis`: 趋势分析数据
- [ ] 每个季度包含完整的财务指标
- [ ] 趋势分析中历史值数量合理（最多8条）

**预期结果**: 财务数据完整，数据量已优化（最新8个季度）

#### 1.7 实时报价 `GET /stocks/{stock_code}/live/quote`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/live/quote" | jq '.' | head -30
```
**必须验证的数据项**:
- [ ] `quote_data.*`: 实时报价数据完整
- [ ] `bid_ask_data.bid_prices`: 买入价格数组（5档）
- [ ] `bid_ask_data.bid_volumes`: 买入量数组（5档）
- [ ] `bid_ask_data.ask_prices`: 卖出价格数组（5档）
- [ ] `bid_ask_data.ask_volumes`: 卖出量数组（5档）

**预期结果**: 实时报价和买卖盘数据完整

#### 1.8 资金流向 `GET /stocks/{stock_code}/live/flow`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/live/flow" | jq '.' | head -40
```
**必须验证的数据项**:
- [ ] `fund_flow_summary.*`: 资金流向汇总数据有值
- [ ] `detailed_flow_data`: 详细流向数据数组（应有约30条）
- [ ] `flow_statistics.*`: 流向统计信息
- [ ] 每条流向记录包含完整的资金数据

**预期结果**: 资金流向数据完整，30天历史数据存在

### 2. 新闻消息面API测试

#### 2.1 公司公告 `GET /stocks/{stock_code}/news/announcements`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/news/announcements" | jq '.' | head -30
```
**必须验证的数据项**:
- [ ] `total_announcements`: 公告总数
- [ ] `announcements`: 公告数组
- [ ] 每条公告包含: 日期、类型、标题、摘要、状态

**预期结果**: 公告数据存在，格式正确

#### 2.2 股东变动 `GET /stocks/{stock_code}/news/shareholders`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/news/shareholders" | jq '.' | head -30
```
**必须验证的数据项**:
- [ ] `shareholder_changes`: 数组存在（可能为空）
- [ ] `note`: 开发状态说明
- [ ] 接口响应正常（200状态码）

**预期结果**: 接口正常响应，显示开发中状态

#### 2.3 龙虎榜 `GET /stocks/{stock_code}/news/dragon-tiger`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/news/dragon-tiger" | jq '.' | head -30
```
**必须验证的数据项**:
- [ ] `query_period_days`: 查询天数（90天）
- [ ] `total_records`: 记录总数
- [ ] `dragon_tiger_records`: 龙虎榜记录数组
- [ ] `summary.*`: 汇总统计信息

**预期结果**: 接口正常，可能无数据但结构完整

#### 2.4 行业新闻 `GET /stocks/{stock_code}/news/industry`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/603993/news/industry" | jq '.' | head -30
```
**必须验证的数据项**:
- [ ] `industry_news`: 数组存在（可能为空）
- [ ] `note`: 开发状态说明
- [ ] 接口响应正常

**预期结果**: 接口正常响应，显示开发中状态

### 3. AI智能分析API测试

#### 3.1 AI服务健康检查 `GET /ai/health`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/ai/health" | jq '.'
```
**必须验证的数据项**:
- [ ] `service`: 服务名称
- [ ] `components.cache.status`: "healthy"
- [ ] `components.ai_agents.technical_agent`: true
- [ ] `components.ai_agents.comprehensive_agent`: true
- [ ] `components.ai_agents.anthropic_api_key`: true

**预期结果**: 所有组件状态健康

#### 3.2 AI即时交易信号 `POST /ai/trading-signal/{stock_code}`
**测试命令**:
```bash
curl -X POST "http://35.77.54.203:3003/ai/trading-signal/603993" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh": false}' | jq '.'
```
**必须验证的数据项**:
- [ ] `analysis_type`: "daily_technical_trading"
- [ ] `cached`: 缓存状态（true/false）
- [ ] `cache_expires_at`: 缓存过期时间
- [ ] `immediate_trading_signal.action`: 交易动作
- [ ] `immediate_trading_signal.entry_condition`: 入场条件
- [ ] `immediate_trading_signal.stop_loss`: 止损信息
- [ ] `immediate_trading_signal.take_profit`: 止盈目标
- [ ] `technical_summary.*`: 技术分析摘要
- [ ] `risk_warning`: 风险警告
- [ ] `ai_analysis`: 完整AI分析内容
- [ ] `api_usage.input_tokens`: Token使用统计
- [ ] `api_usage.output_tokens`: Token使用统计

**性能要求**:
- [ ] 首次调用: < 2分钟
- [ ] 缓存命中: < 1秒

**预期结果**: AI分析结果完整，缓存机制正常

#### 3.3 AI综合评估 `POST /ai/comprehensive-evaluation/{stock_code}`
**测试命令**:
```bash
curl -X POST "http://35.77.54.203:3003/ai/comprehensive-evaluation/603993" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh": false}' | jq '.'
```
**必须验证的数据项**:
- [ ] `analysis_type`: "comprehensive_stock_evaluation"
- [ ] `cached`: 缓存状态
- [ ] `comprehensive_evaluation.investment_rating`: 投资评级
- [ ] `comprehensive_evaluation.target_price`: 目标价
- [ ] `comprehensive_evaluation.upside_potential`: 上涨空间
- [ ] `evidence_and_reasoning.key_supporting_data`: 支撑数据数组
- [ ] `evidence_and_reasoning.reasoning_chain`: 推理链数组
- [ ] `evidence_and_reasoning.uncertainty_factors`: 不确定性因素
- [ ] `detailed_analysis.*`: 详细分析各项
- [ ] `raw_data_sources.*`: 原始数据源
- [ ] `ai_analysis`: 完整AI分析
- [ ] `api_usage.*`: Token使用统计

**数据量验证**:
- [ ] `raw_data_sources.financial_history.quarterly_data`: 最多8个季度
- [ ] 趋势分析历史值: 最多8条记录

**性能要求**:
- [ ] 首次调用: < 3分钟
- [ ] 缓存命中: < 1秒

**预期结果**: AI综合评估完整，数据量已优化，缓存正常

### 4. AI缓存管理API测试

#### 4.1 缓存状态查询 `GET /ai/cache/status/{stock_code}`
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/ai/cache/status/603993" | jq '.'
```
**必须验证的数据项**:
- [ ] `stock_code`: 股票代码
- [ ] `trading_signal.exists`: 交易信号缓存状态
- [ ] `comprehensive_eval.exists`: 综合评估缓存状态
- [ ] TTL信息正确

#### 4.2 缓存清除 `DELETE /ai/cache/{stock_code}`
**测试命令**:
```bash
curl -X DELETE "http://35.77.54.203:3003/ai/cache/603993?cache_type=all" | jq '.'
```
**必须验证的数据项**:
- [ ] `success`: true
- [ ] 清除后缓存状态确实改变

### 5. 缓存机制专项测试

#### 5.1 AI交易信号缓存测试
**测试步骤**:
1. [ ] 清除缓存: `DELETE /ai/cache/603993?cache_type=trading_signal`
2. [ ] 第一次调用: 记录Token消耗和响应时间
3. [ ] 第二次调用: 验证缓存命中，响应时间 < 1秒
4. [ ] 强制刷新: `{"force_refresh": true}` 验证重新生成

#### 5.2 AI综合评估缓存测试
**测试步骤**:
1. [ ] 清除缓存: `DELETE /ai/cache/603993?cache_type=comprehensive`
2. [ ] 第一次调用: 记录Token消耗和响应时间
3. [ ] 第二次调用: 验证24小时缓存命中
4. [ ] 强制刷新: 验证重新生成和Token消耗

### 6. 数据完整性验证

#### 6.1 数据裁剪验证
**检查项目**:
- [ ] 财务历史数据季度数量 ≤ 8
- [ ] 趋势分析历史值数量 ≤ 8  
- [ ] 其他历史数据数组长度合理
- [ ] 数据为最新时间段

#### 6.2 数值类型验证
**检查项目**:
- [ ] 价格字段为数值类型
- [ ] 百分比字段格式正确
- [ ] 日期字段格式标准
- [ ] 布尔字段值正确

### 7. 错误处理测试

#### 7.1 无效股票代码测试
**测试命令**:
```bash
curl -s "http://35.77.54.203:3003/stocks/999999" | jq '.'
```
**预期结果**: 返回明确的错误信息

#### 7.2 AI服务异常测试
- [ ] 无Anthropic API密钥时的错误处理
- [ ] Redis连接失败时的降级策略
- [ ] 数据获取失败时的错误响应

## 📊 测试报告格式

每次测试完成后，需要记录：

```markdown
## 测试报告 - [日期]
**测试人**: [姓名]
**测试股票**: 603993

### 通过的测试项 (X/Y)
- [x] 核心数据API: 8/8
- [x] 新闻消息面API: 4/4  
- [x] AI分析API: 3/3
- [x] 缓存管理API: 2/2

### 发现的问题
1. [问题描述] - [状态: 已修复/待修复]

### 性能指标
- AI交易信号首次调用: XXs
- AI综合评估首次调用: XXs
- 缓存命中响应时间: XXs

### 总结
[整体测试结果和建议]
```

## ⚠️ 关键注意事项

1. **测试环境**: 确保使用 `35.77.54.203:3003`
2. **测试股票**: 统一使用 `603993` 以确保结果可对比
3. **缓存测试**: 必须测试缓存的生成、命中、刷新全流程
4. **数据验证**: 不能只检查HTTP状态码，必须验证数据内容
5. **性能要求**: AI功能的响应时间要求必须满足
6. **Token统计**: 验证AI功能的Token消耗统计准确

## 🔄 维护说明

- 新增API端点时，必须在此清单中添加相应测试用例
- API修改时，必须更新对应的测试验证项
- 每次发布前必须完整执行此测试清单
- 发现问题时必须更新测试用例以防止回归