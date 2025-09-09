# -*- coding: utf-8 -*-
"""
AI分析API端点
AI Analysis API Endpoints
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import os

# 导入服务模块
from .services.cache_manager import analysis_cache
from .services.data_aggregator import stock_data_aggregator
from .agents.technical_agent import TechnicalAnalysisAgent
from .agents.comprehensive_agent import ComprehensiveAnalysisAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建AI分析专用的FastAPI应用
ai_analysis_app = FastAPI(
    title="AI股票分析API",
    description="基于Claude AI的智能股票分析服务",
    version="1.0.0"
)

ai_analysis_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化AI Agents
technical_agent = None
comprehensive_agent = None

def initialize_agents():
    """初始化AI Agents"""
    global technical_agent, comprehensive_agent
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.error("ANTHROPIC_API_KEY环境变量未设置")
            return False
        
        technical_agent = TechnicalAnalysisAgent(api_key)
        comprehensive_agent = ComprehensiveAnalysisAgent(api_key)
        logger.info("AI Agents初始化成功")
        return True
    except Exception as e:
        logger.error(f"AI Agents初始化失败: {e}")
        return False

# 请求/响应模型
class TradingSignalRequest(BaseModel):
    force_refresh: Optional[bool] = False

class ComprehensiveEvalRequest(BaseModel):
    force_refresh: Optional[bool] = False

class CacheStatusResponse(BaseModel):
    stock_code: str
    trading_signal: Dict[str, Any]
    comprehensive_eval: Dict[str, Any]

@ai_analysis_app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("启动AI分析服务...")
    
    # 初始化AI Agents
    if not initialize_agents():
        logger.error("AI Agents初始化失败，某些功能可能不可用")
    
    # 测试Redis连接
    try:
        await analysis_cache.connect()
        logger.info("Redis连接测试成功")
    except Exception as e:
        logger.error(f"Redis连接失败: {e}")

@ai_analysis_app.get("/")
async def root():
    """健康检查"""
    return {
        "service": "AI股票分析API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@ai_analysis_app.get("/health")
async def health_check():
    """完整健康检查"""
    health_status = {
        "service": "AI股票分析API",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # 检查Redis缓存
    try:
        cache_health = await analysis_cache.health_check()
        health_status["components"]["cache"] = cache_health
    except Exception as e:
        health_status["components"]["cache"] = {"status": "unhealthy", "error": str(e)}
    
    # 检查数据聚合器
    try:
        aggregator_health = await stock_data_aggregator.health_check()
        health_status["components"]["data_aggregator"] = aggregator_health
    except Exception as e:
        health_status["components"]["data_aggregator"] = {"status": "unhealthy", "error": str(e)}
    
    # 检查AI Agents
    health_status["components"]["ai_agents"] = {
        "technical_agent": bool(technical_agent),
        "comprehensive_agent": bool(comprehensive_agent),
        "anthropic_api_key": bool(os.getenv('ANTHROPIC_API_KEY'))
    }
    
    # 计算整体状态
    all_healthy = all(
        component.get("status") == "healthy" 
        for component in health_status["components"].values()
        if isinstance(component, dict) and "status" in component
    )
    health_status["status"] = "healthy" if all_healthy else "degraded"
    
    return health_status

@ai_analysis_app.post("/ai/trading-signal/{stock_code}")
async def get_trading_signal(
    stock_code: str, 
    request: TradingSignalRequest = TradingSignalRequest()
):
    """
    获取即时技术面交易信号API
    
    - 30分钟缓存策略
    - 基于日线级别技术分析
    - 返回具体买卖信号和操作建议
    """
    try:
        logger.info(f"处理技术面交易信号请求: {stock_code}")
        
        # 验证股票代码
        if not stock_code or len(stock_code) != 6 or not stock_code.isdigit():
            raise HTTPException(
                status_code=400,
                detail="股票代码必须是6位数字"
            )
        
        # 检查缓存（除非强制刷新）
        cached_result = None
        if not request.force_refresh:
            cached_result = await analysis_cache.get_trading_signal_cache(stock_code)
            if cached_result:
                logger.info(f"返回技术面交易信号缓存: {stock_code}")
                return {
                    "analysis_type": "daily_technical_trading",
                    "stock_code": stock_code,
                    **cached_result
                }
        
        # 检查AI Agent是否可用
        if not technical_agent:
            raise HTTPException(
                status_code=503,
                detail="技术面分析AI Agent未初始化"
            )
        
        # 收集技术面数据
        logger.info(f"收集技术面数据: {stock_code}")
        technical_data = await stock_data_aggregator.collect_technical_data(stock_code)
        
        if not technical_data or technical_data.get("success_count", 0) == 0:
            raise HTTPException(
                status_code=503,
                detail="无法获取技术分析所需的数据"
            )
        
        # 格式化数据为AI可读格式
        formatted_data = stock_data_aggregator.format_data_for_ai(technical_data)
        
        # 执行AI分析
        logger.info(f"执行技术面AI分析: {stock_code}")
        ai_result = await technical_agent.analyze_trading_signal(formatted_data, stock_code)
        
        if not ai_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"AI技术分析失败: {ai_result.get('error', 'Unknown error')}"
            )
        
        # 构建响应
        response_data = {
            "analysis_type": "daily_technical_trading",
            "stock_code": stock_code,
            "cached": False,
            "cache_expires_at": None,
            "immediate_trading_signal": ai_result["analysis"].get("immediate_trading_signal", {}),
            "technical_summary": ai_result["analysis"].get("technical_summary", {}),
            "risk_warning": ai_result["analysis"].get("risk_warning", "请注意投资风险"),
            "ai_analysis": ai_result["analysis"].get("raw_content", ""),
            "data_completeness": technical_data.get("data_completeness", 0),
            "api_usage": ai_result.get("api_usage", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存到缓存
        await analysis_cache.set_trading_signal_cache(stock_code, response_data)
        
        logger.info(f"技术面交易信号分析完成: {stock_code}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"技术面交易信号处理异常 {stock_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"处理技术面交易信号时发生错误: {str(e)}"
        )

@ai_analysis_app.post("/ai/comprehensive-evaluation/{stock_code}")
async def get_comprehensive_evaluation(
    stock_code: str,
    request: ComprehensiveEvalRequest = ComprehensiveEvalRequest()
):
    """
    获取综合股票评估报告API
    
    - 24小时缓存策略
    - 多维度综合分析
    - 返回完整的投资价值评估
    """
    try:
        logger.info(f"处理综合评估请求: {stock_code}")
        
        # 验证股票代码
        if not stock_code or len(stock_code) != 6 or not stock_code.isdigit():
            raise HTTPException(
                status_code=400,
                detail="股票代码必须是6位数字"
            )
        
        # 检查缓存（除非强制刷新）
        cached_result = None
        if not request.force_refresh:
            cached_result = await analysis_cache.get_comprehensive_cache(stock_code)
            if cached_result:
                logger.info(f"返回综合评估缓存: {stock_code}")
                return {
                    "analysis_type": "comprehensive_stock_evaluation",
                    "stock_code": stock_code,
                    **cached_result
                }
        
        # 检查AI Agent是否可用
        if not comprehensive_agent:
            raise HTTPException(
                status_code=503,
                detail="综合评估AI Agent未初始化"
            )
        
        # 收集综合数据
        logger.info(f"收集综合数据: {stock_code}")
        comprehensive_data = await stock_data_aggregator.collect_comprehensive_data(stock_code)
        
        if not comprehensive_data or comprehensive_data.get("success_count", 0) < 3:  # 至少需要3个数据源
            raise HTTPException(
                status_code=503,
                detail=f"数据不足，无法进行综合评估。成功获取: {comprehensive_data.get('success_count', 0)}/8"
            )
        
        # 格式化数据为AI可读格式
        formatted_data = stock_data_aggregator.format_data_for_ai(comprehensive_data)
        
        # 执行AI分析
        logger.info(f"执行综合评估AI分析: {stock_code}")
        ai_result = await comprehensive_agent.analyze_comprehensive_evaluation(formatted_data, stock_code)
        
        if not ai_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"AI综合评估失败: {ai_result.get('error', 'Unknown error')}"
            )
        
        # 构建响应
        response_data = {
            "analysis_type": "comprehensive_stock_evaluation",
            "stock_code": stock_code,
            "cached": False,
            "cache_expires_at": None,
            "comprehensive_evaluation": ai_result["analysis"].get("comprehensive_evaluation", {}),
            "evidence_and_reasoning": ai_result["analysis"].get("evidence_and_reasoning", {}),
            "detailed_analysis": ai_result["analysis"].get("detailed_analysis", {}),
            "sector_comparison": ai_result["analysis"].get("sector_comparison", {}),
            "raw_data_sources": {
                "fundamental_data": stock_data_aggregator._trim_large_datasets(
                    comprehensive_data.get("data_sources", {}).get("fundamental_analysis", {}), max_items=8
                ),
                "technical_data": stock_data_aggregator._trim_large_datasets(
                    comprehensive_data.get("data_sources", {}).get("technical_analysis", {}), max_items=8
                ),
                "news_data": {
                    "announcements": stock_data_aggregator._trim_large_datasets(
                        comprehensive_data.get("data_sources", {}).get("announcements", {}), max_items=8
                    ),
                    "dragon_tiger": stock_data_aggregator._trim_large_datasets(
                        comprehensive_data.get("data_sources", {}).get("dragon_tiger", {}), max_items=8
                    )
                },
                "financial_history": stock_data_aggregator._trim_large_datasets(
                    comprehensive_data.get("data_sources", {}).get("financial_history", {}), max_items=8
                )
            },
            "ai_analysis": ai_result["analysis"].get("raw_content", ""),
            "data_completeness": comprehensive_data.get("data_completeness", 0),
            "api_usage": ai_result.get("api_usage", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存到缓存
        await analysis_cache.set_comprehensive_cache(stock_code, response_data)
        
        logger.info(f"综合评估分析完成: {stock_code}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"综合评估处理异常 {stock_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"处理综合评估时发生错误: {str(e)}"
        )

@ai_analysis_app.get("/ai/cache/status/{stock_code}")
async def get_cache_status(stock_code: str) -> CacheStatusResponse:
    """获取指定股票的缓存状态"""
    try:
        status = await analysis_cache.get_cache_status(stock_code)
        return CacheStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@ai_analysis_app.delete("/ai/cache/{stock_code}")
async def clear_cache(stock_code: str, cache_type: str = "all"):
    """清除指定股票的缓存"""
    try:
        result = await analysis_cache.clear_cache(stock_code, cache_type)
        return {
            "success": result,
            "stock_code": stock_code,
            "cache_type": cache_type,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(ai_analysis_app, host="0.0.0.0", port=3005)  # 使用端口3005