# -*- coding: utf-8 -*-
"""
数据聚合服务
Data Aggregation Service
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class StockDataAggregator:
    """股票数据聚合器 - 整合现有的8个API接口"""
    
    def __init__(self, base_url: str = "http://35.77.54.203:3003"):
        self.base_url = base_url
        self.timeout = 10  # 减少超时时间到10秒
        self.max_concurrent = 3  # 限制并发请求数量
    
    async def _make_request(self, session: aiohttp.ClientSession, url: str, endpoint_name: str) -> Dict[str, Any]:
        """发起HTTP请求"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"成功获取 {endpoint_name} 数据")
                    return {"success": True, "data": data, "endpoint": endpoint_name}
                else:
                    error_msg = f"{endpoint_name} API返回错误状态码: {response.status}"
                    logger.warning(error_msg)
                    return {"success": False, "error": error_msg, "endpoint": endpoint_name}
        except asyncio.TimeoutError:
            error_msg = f"{endpoint_name} API请求超时"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "endpoint": endpoint_name}
        except Exception as e:
            error_msg = f"{endpoint_name} API请求失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "endpoint": endpoint_name}
    
    async def collect_technical_data(self, stock_code: str) -> Dict[str, Any]:
        """
        收集技术面分析所需的数据
        
        调用的API接口：
        - GET /stocks/{code}/live/quote           # 实时报价
        - GET /stocks/{code}/historical/prices?days=30  # K线数据
        - GET /stocks/{code}/analysis/technical    # 技术分析
        """
        try:
            async with aiohttp.ClientSession() as session:
                # 定义要调用的API端点
                endpoints = [
                    {
                        "name": "live_quote",
                        "url": f"{self.base_url}/stocks/{stock_code}/live/quote",
                        "description": "实时报价"
                    },
                    {
                        "name": "historical_prices",
                        "url": f"{self.base_url}/stocks/{stock_code}/historical/prices?days=30",
                        "description": "30天K线数据"
                    },
                    {
                        "name": "technical_analysis",
                        "url": f"{self.base_url}/stocks/{stock_code}/analysis/technical",
                        "description": "技术分析"
                    }
                ]
                
                # 分批并行发起请求，避免过多并发
                results = []
                for i in range(0, len(endpoints), self.max_concurrent):
                    batch = endpoints[i:i + self.max_concurrent]
                    tasks = [
                        self._make_request(session, endpoint["url"], endpoint["name"])
                        for endpoint in batch
                    ]
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    results.extend(batch_results)
                
                # 整理数据
                aggregated_data = {
                    "stock_code": stock_code,
                    "data_type": "technical_analysis",
                    "collected_at": datetime.now().isoformat(),
                    "data_sources": {},
                    "errors": [],
                    "success_count": 0,
                    "total_endpoints": len(endpoints)
                }
                
                for i, result in enumerate(results):
                    endpoint_name = endpoints[i]["name"]
                    
                    if isinstance(result, Exception):
                        error_msg = f"{endpoint_name}: {str(result)}"
                        aggregated_data["errors"].append(error_msg)
                        logger.error(error_msg)
                    elif result["success"]:
                        aggregated_data["data_sources"][endpoint_name] = result["data"]
                        aggregated_data["success_count"] += 1
                    else:
                        aggregated_data["errors"].append(f"{endpoint_name}: {result['error']}")
                
                # 数据完整性检查
                aggregated_data["data_completeness"] = (
                    aggregated_data["success_count"] / aggregated_data["total_endpoints"]
                )
                
                logger.info(f"技术面数据收集完成: {stock_code}, 成功率: {aggregated_data['data_completeness']:.2%}")
                return aggregated_data
                
        except Exception as e:
            logger.error(f"技术面数据聚合失败 {stock_code}: {e}")
            return {
                "stock_code": stock_code,
                "data_type": "technical_analysis",
                "error": str(e),
                "success": False,
                "collected_at": datetime.now().isoformat()
            }
    
    async def collect_comprehensive_data(self, stock_code: str) -> Dict[str, Any]:
        """
        收集综合评估所需的所有数据
        
        调用的API接口：
        - GET /stocks/{code}                      # 统一核心数据
        - GET /stocks/{code}/analysis/fundamental # 基本面分析
        - GET /stocks/{code}/analysis/technical   # 技术面分析  
        - GET /stocks/{code}/historical/financial # 历史财务
        - GET /stocks/{code}/news/announcements   # 公司公告
        - GET /stocks/{code}/news/dragon-tiger    # 龙虎榜
        - GET /stocks/{code}/historical/prices    # 历史价格
        - GET /stocks/{code}/live/flow            # 资金流向
        """
        try:
            async with aiohttp.ClientSession() as session:
                # 定义要调用的所有API端点
                endpoints = [
                    {
                        "name": "core_data",
                        "url": f"{self.base_url}/stocks/{stock_code}",
                        "description": "统一核心数据"
                    },
                    {
                        "name": "fundamental_analysis",
                        "url": f"{self.base_url}/stocks/{stock_code}/analysis/fundamental",
                        "description": "基本面分析"
                    },
                    {
                        "name": "technical_analysis",
                        "url": f"{self.base_url}/stocks/{stock_code}/analysis/technical",
                        "description": "技术面分析"
                    },
                    {
                        "name": "financial_history",
                        "url": f"{self.base_url}/stocks/{stock_code}/historical/financial",
                        "description": "历史财务数据"
                    },
                    {
                        "name": "announcements",
                        "url": f"{self.base_url}/stocks/{stock_code}/news/announcements",
                        "description": "公司公告"
                    },
                    {
                        "name": "dragon_tiger",
                        "url": f"{self.base_url}/stocks/{stock_code}/news/dragon-tiger",
                        "description": "龙虎榜数据"
                    },
                    {
                        "name": "historical_prices",
                        "url": f"{self.base_url}/stocks/{stock_code}/historical/prices",
                        "description": "历史价格"
                    },
                    {
                        "name": "money_flow",
                        "url": f"{self.base_url}/stocks/{stock_code}/live/flow",
                        "description": "资金流向"
                    }
                ]
                
                # 分批并行发起请求，避免过多并发
                results = []
                for i in range(0, len(endpoints), self.max_concurrent):
                    batch = endpoints[i:i + self.max_concurrent]
                    tasks = [
                        self._make_request(session, endpoint["url"], endpoint["name"])
                        for endpoint in batch
                    ]
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    results.extend(batch_results)
                
                # 整理数据
                aggregated_data = {
                    "stock_code": stock_code,
                    "data_type": "comprehensive_evaluation",
                    "collected_at": datetime.now().isoformat(),
                    "data_sources": {},
                    "errors": [],
                    "success_count": 0,
                    "total_endpoints": len(endpoints)
                }
                
                for i, result in enumerate(results):
                    endpoint_name = endpoints[i]["name"]
                    
                    if isinstance(result, Exception):
                        error_msg = f"{endpoint_name}: {str(result)}"
                        aggregated_data["errors"].append(error_msg)
                        logger.error(error_msg)
                    elif result["success"]:
                        aggregated_data["data_sources"][endpoint_name] = result["data"]
                        aggregated_data["success_count"] += 1
                    else:
                        aggregated_data["errors"].append(f"{endpoint_name}: {result['error']}")
                
                # 数据完整性检查
                aggregated_data["data_completeness"] = (
                    aggregated_data["success_count"] / aggregated_data["total_endpoints"]
                )
                
                logger.info(f"综合数据收集完成: {stock_code}, 成功率: {aggregated_data['data_completeness']:.2%}")
                return aggregated_data
                
        except Exception as e:
            logger.error(f"综合数据聚合失败 {stock_code}: {e}")
            return {
                "stock_code": stock_code,
                "data_type": "comprehensive_evaluation", 
                "error": str(e),
                "success": False,
                "collected_at": datetime.now().isoformat()
            }
    
    def _trim_large_datasets(self, data: Dict[str, Any], max_items: int = 8) -> Dict[str, Any]:
        """裁剪大数据集，只保留最新的指定条目数量"""
        if not isinstance(data, dict):
            return data
        
        trimmed_data = data.copy()
        
        # 处理季度数据 (quarterly_data)
        if "quarterly_data" in trimmed_data and isinstance(trimmed_data["quarterly_data"], dict):
            quarterly_items = list(trimmed_data["quarterly_data"].items())
            # 按键名排序，获取最新的8个季度（键名格式如 "2025Q2", "2025Q1"）
            quarterly_items.sort(key=lambda x: x[0], reverse=True)
            trimmed_data["quarterly_data"] = dict(quarterly_items[:max_items])
        
        # 处理趋势分析数据 (trend_analysis)
        if "trend_analysis" in trimmed_data and isinstance(trimmed_data["trend_analysis"], dict):
            for indicator, trend_data in trimmed_data["trend_analysis"].items():
                if isinstance(trend_data, dict) and "historical_values" in trend_data:
                    if isinstance(trend_data["historical_values"], list):
                        # 保留最新的8条历史数据
                        trend_data["historical_values"] = trend_data["historical_values"][:max_items]
        
        # 处理历史价格数据 (如果是包含日期的数组)
        if "data" in trimmed_data and isinstance(trimmed_data["data"], list):
            # 如果是价格数据数组，保留最新的8条
            if len(trimmed_data["data"]) > max_items:
                trimmed_data["data"] = trimmed_data["data"][:max_items]
        
        # 处理公告数据 (announcements)
        if "announcements" in trimmed_data and isinstance(trimmed_data["announcements"], list):
            trimmed_data["announcements"] = trimmed_data["announcements"][:max_items]
        
        # 处理龙虎榜数据 (dragon_tiger_list)
        if "dragon_tiger_list" in trimmed_data and isinstance(trimmed_data["dragon_tiger_list"], list):
            trimmed_data["dragon_tiger_list"] = trimmed_data["dragon_tiger_list"][:max_items]
        
        # 处理其他可能的大数组字段
        for key, value in trimmed_data.items():
            if isinstance(value, list) and len(value) > max_items:
                # 检查是否是时间序列数据（包含日期字段）
                if value and isinstance(value[0], dict) and any(
                    date_field in str(value[0]).lower() 
                    for date_field in ['date', 'time', 'period', '日期', '时间']
                ):
                    trimmed_data[key] = value[:max_items]
        
        return trimmed_data

    def format_data_for_ai(self, aggregated_data: Dict[str, Any]) -> str:
        """将聚合数据格式化为AI分析可用的文本格式"""
        try:
            if not aggregated_data.get("data_sources"):
                return "数据收集失败，无法进行分析。"
            
            formatted_sections = []
            
            # 数据概览
            formatted_sections.append(f"""
=== 股票数据概览 ===
股票代码: {aggregated_data['stock_code']}
数据类型: {aggregated_data['data_type']}
数据收集时间: {aggregated_data['collected_at']}
数据完整性: {aggregated_data.get('data_completeness', 0):.2%}
""")
            
            # 逐个处理数据源，并裁剪大数据集
            for source_name, source_data in aggregated_data["data_sources"].items():
                # 裁剪数据，只保留最新8条
                trimmed_data = self._trim_large_datasets(source_data, max_items=8)
                
                formatted_sections.append(f"""
=== {source_name.upper()} ===
{json.dumps(trimmed_data, ensure_ascii=False, indent=2)}
""")
            
            # 错误信息（如果有）
            if aggregated_data.get("errors"):
                formatted_sections.append(f"""
=== 数据收集错误 ===
{chr(10).join(aggregated_data['errors'])}
""")
            
            return "\n".join(formatted_sections)
            
        except Exception as e:
            logger.error(f"数据格式化失败: {e}")
            return f"数据格式化失败: {str(e)}"
    
    async def health_check(self) -> Dict[str, Any]:
        """数据聚合服务健康检查"""
        try:
            # 测试基础连接
            async with aiohttp.ClientSession() as session:
                test_url = f"{self.base_url}/health"  # 假设有健康检查端点
                result = await self._make_request(session, test_url, "health_check")
                
                return {
                    "service": "StockDataAggregator",
                    "status": "healthy" if result["success"] else "unhealthy",
                    "base_url": self.base_url,
                    "timeout": self.timeout,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "service": "StockDataAggregator",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 全局数据聚合器实例
stock_data_aggregator = StockDataAggregator()