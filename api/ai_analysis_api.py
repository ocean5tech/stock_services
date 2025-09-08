# -*- coding: utf-8 -*-
"""
AI分析API端点
AI Analysis API Endpoints
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime

# 导入AI Agent
from ai_agent.stock_agents import stock_analyzer
from ai_agent.prompt_manager import prompt_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建AI分析专用的FastAPI应用（或者可以集成到现有的app中）
ai_app = FastAPI(
    title="Stock AI Analysis API",
    description="AI-powered stock analysis using Claude agents",
    version="1.0.0"
)

ai_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求/响应模型
class AnalysisRequest(BaseModel):
    stock_code: str
    analysis_styles: Optional[List[str]] = ['professional', 'insight']
    force_refresh: Optional[bool] = False

class AgentStatusResponse(BaseModel):
    available_agents: List[str]
    agent_info: dict

@ai_app.get("/")
async def root():
    """健康检查"""
    return {
        "service": "Stock AI Analysis API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@ai_app.get("/agents/status")
async def get_agents_status() -> AgentStatusResponse:
    """获取所有AI Agent的状态信息"""
    try:
        available_agents = prompt_manager.list_available_agents()
        agent_info = {}
        
        # 获取每个Agent的配置信息
        for agent_name in available_agents:
            try:
                validation_result = prompt_manager.validate_config(agent_name)
                agent_info[agent_name] = validation_result
            except Exception as e:
                agent_info[agent_name] = {
                    'valid': False,
                    'error': str(e)
                }
        
        return AgentStatusResponse(
            available_agents=available_agents,
            agent_info=agent_info
        )
    
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_app.post("/agents/reload")
async def reload_agent_configs():
    """重新加载所有Agent配置"""
    try:
        prompt_manager.reload_all_configs()
        return {
            "message": "All agent configurations reloaded successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error reloading agent configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_app.get("/stocks/{stock_code}/ai-analysis")
async def get_comprehensive_ai_analysis(
    stock_code: str,
    analysis_styles: Optional[str] = Query(default="professional,insight", description="分析风格，用逗号分隔"),
    force_refresh: Optional[bool] = Query(default=False, description="强制刷新缓存")
):
    """
    获取股票的AI综合分析
    
    这个端点将替代原来的n8n workflow，提供：
    - 基本面分析
    - 技术面分析  
    - 综合分析文章生成
    - 多种分析风格
    """
    try:
        logger.info(f"Starting AI analysis for stock {stock_code}")
        
        # 解析分析风格参数
        if analysis_styles:
            styles_list = [style.strip() for style in analysis_styles.split(',')]
        else:
            styles_list = ['professional', 'insight']
        
        # 验证股票代码格式
        if not stock_code or len(stock_code) != 6 or not stock_code.isdigit():
            raise HTTPException(
                status_code=400, 
                detail="股票代码必须是6位数字"
            )
        
        # 如果强制刷新，可以在这里清除缓存
        if force_refresh:
            logger.info(f"Force refresh requested for {stock_code}")
        
        # 执行AI分析
        result = await stock_analyzer.comprehensive_analysis(
            stock_code=stock_code,
            analysis_styles=styles_list
        )
        
        # 检查结果
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=f"AI分析失败: {result.get('error', 'Unknown error')}"
            )
        
        logger.info(f"AI analysis completed for stock {stock_code}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in AI analysis for {stock_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI分析过程中出现错误: {str(e)}"
        )

@ai_app.get("/stocks/{stock_code}/fundamental")
async def get_fundamental_analysis(stock_code: str):
    """仅执行基本面分析"""
    try:
        # 获取股票数据
        stock_data = await stock_analyzer.get_stock_data(stock_code)
        
        # 执行基本面分析
        result = await stock_analyzer.fundamental_agent.analyze(**stock_data)
        
        return {
            'stock_code': stock_code,
            'analysis_type': 'fundamental',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Fundamental analysis failed for {stock_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_app.get("/stocks/{stock_code}/technical")  
async def get_technical_analysis(stock_code: str):
    """仅执行技术面分析"""
    try:
        # 获取股票数据
        stock_data = await stock_analyzer.get_stock_data(stock_code)
        
        # 执行技术面分析
        result = await stock_analyzer.technical_agent.analyze(**stock_data)
        
        return {
            'stock_code': stock_code,
            'analysis_type': 'technical',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Technical analysis failed for {stock_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_app.get("/prompts/{agent_name}")
async def get_agent_prompts(agent_name: str):
    """获取指定Agent的提示词（用于调试）"""
    try:
        config = prompt_manager.load_prompt_config(agent_name)
        
        # 不返回完整的提示词内容，只返回摘要信息
        return {
            'agent_name': config.get('agent_name'),
            'version': config.get('version'),
            'system_prompt_length': len(config.get('system_prompt', '')),
            'user_template_length': len(config.get('user_prompt_template', '')),
            'parameters': config.get('parameters', {}),
            'cache_config': config.get('cache_config', {})
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(ai_app, host="0.0.0.0", port=3004)  # 使用不同端口避免冲突