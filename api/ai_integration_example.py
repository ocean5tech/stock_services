# -*- coding: utf-8 -*-
"""
将AI Agent集成到现有stock_analysis_api.py的示例
Example of integrating AI Agent into existing stock_analysis_api.py
"""

# 在stock_analysis_api.py中添加以下代码:

# ============ 1. 在文件顶部添加导入 ============
"""
from ai_agent.stock_agents import stock_analyzer
from ai_agent.prompt_manager import prompt_manager
import logging
import asyncio

logger = logging.getLogger(__name__)
"""

# ============ 2. 创建数据获取助手函数 ============

async def get_comprehensive_stock_data(stock_code: str):
    """
    获取全面的股票数据 - 供AI Agent使用
    整合现有的API端点数据
    """
    try:
        # 调用现有的API函数获取数据
        # 基本面数据
        fundamental_response = await get_fundamental_analysis(stock_code)
        
        # 技术面数据  
        technical_response = await get_technical_analysis(stock_code)
        
        # 消息面数据
        announcements = await get_company_announcements(stock_code)
        dragon_tiger = await get_dragon_tiger_list(stock_code)
        
        return {
            'stock_code': stock_code,
            'stock_name': fundamental_response.get('stock_name', ''),
            'fundamental_data': fundamental_response,
            'technical_data': technical_response,
            'news_data': {
                'announcements': announcements,
                'dragon_tiger': dragon_tiger
            }
        }
    except Exception as e:
        logger.error(f"Error getting comprehensive stock data for {stock_code}: {e}")
        raise

# ============ 3. 添加新的AI分析端点 ============

@app.get("/stocks/{stock_code}/ai-analysis")
async def get_ai_comprehensive_analysis(stock_code: str, analysis_styles: str = "professional,insight"):
    """
    AI综合分析端点 - 替代n8n workflow
    
    这个端点将：
    1. 获取股票的三维度数据
    2. 使用AI Agent进行智能分析
    3. 生成多种风格的分析文章
    4. 返回结构化的分析结果
    """
    try:
        logger.info(f"Starting AI analysis for stock {stock_code}")
        
        # 解析分析风格
        styles_list = [style.strip() for style in analysis_styles.split(',')]
        
        # 验证股票代码
        if not stock_code or len(stock_code) != 6 or not stock_code.isdigit():
            return {"error": "股票代码必须是6位数字"}
        
        # 执行AI分析
        result = await stock_analyzer.comprehensive_analysis(
            stock_code=stock_code,
            analysis_styles=styles_list
        )
        
        # 返回与前端兼容的格式
        return {
            "stock_code": stock_code,
            "data_source": "ai_agent_analysis", 
            "timestamp": datetime.now().isoformat(),
            "status": "completed" if result.get('success') else "failed",
            "analysis": result.get('analysis', {}),
            "error": result.get('error') if not result.get('success') else None
        }
        
    except Exception as e:
        logger.error(f"AI analysis failed for {stock_code}: {e}")
        return {
            "stock_code": stock_code,
            "data_source": "ai_agent_analysis",
            "timestamp": datetime.now().isoformat(), 
            "status": "failed",
            "error": str(e)
        }

@app.get("/ai/agents/status")
async def get_ai_agents_status():
    """获取AI Agent状态信息"""
    try:
        available_agents = prompt_manager.list_available_agents()
        agent_info = {}
        
        for agent_name in available_agents:
            validation_result = prompt_manager.validate_config(agent_name)
            agent_info[agent_name] = validation_result
            
        return {
            "service": "AI Agents",
            "status": "running",
            "available_agents": available_agents,
            "agent_details": agent_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/ai/prompts/reload")
async def reload_ai_prompts():
    """重新加载AI提示词配置"""
    try:
        prompt_manager.reload_all_configs()
        return {
            "message": "AI提示词配置已重新加载",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

# ============ 4. 修改现有的数据获取函数为async（如果需要） ============

# 将现有的同步函数包装为异步函数，供AI Agent使用
async def get_fundamental_analysis_async(stock_code: str):
    """异步版本的基本面分析"""
    return await asyncio.to_thread(get_fundamental_analysis, stock_code)

async def get_technical_analysis_async(stock_code: str):
    """异步版本的技术面分析"""  
    return await asyncio.to_thread(get_technical_analysis, stock_code)

# ============ 5. 在stock_analyzer中集成现有API ============

# 修改 ai_agent/stock_agents.py 中的 get_stock_data 方法
"""
async def get_stock_data(self, stock_code: str) -> Dict[str, Any]:
    '''获取股票基础数据 - 调用现有API'''
    try:
        # 导入现有的API函数
        from ..stock_analysis_api import get_fundamental_analysis, get_technical_analysis
        from ..stock_analysis_api import get_company_announcements, get_dragon_tiger_list
        
        # 并行获取数据
        tasks = [
            asyncio.to_thread(get_fundamental_analysis, stock_code),
            asyncio.to_thread(get_technical_analysis, stock_code),
            asyncio.to_thread(get_company_announcements, stock_code),
            asyncio.to_thread(get_dragon_tiger_list, stock_code)
        ]
        
        fundamental, technical, announcements, dragon_tiger = await asyncio.gather(*tasks)
        
        return {
            'stock_code': stock_code,
            'stock_name': fundamental.get('stock_name', ''),
            'fundamental_data': fundamental,
            'technical_data': technical,
            'news_data': {
                'announcements': announcements,
                'dragon_tiger': dragon_tiger
            }
        }
    except Exception as e:
        logger.error(f"Failed to get stock data for {stock_code}: {e}")
        raise
"""