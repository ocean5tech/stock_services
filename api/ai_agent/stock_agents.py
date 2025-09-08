# -*- coding: utf-8 -*-
"""
股票分析专用AI Agent
Stock Analysis AI Agents
"""
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .base_agent import BaseAIAgent

logger = logging.getLogger(__name__)

class FundamentalAnalysisAgent(BaseAIAgent):
    """基本面分析AI Agent"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("fundamental", api_key)
    
    async def process_input_data(self, **kwargs) -> Dict[str, Any]:
        """处理基本面分析的输入数据"""
        stock_code = kwargs.get('stock_code')
        if not stock_code:
            raise ValueError("stock_code is required for fundamental analysis")
        
        # 这里可以调用现有的API获取基本面数据
        # 假设我们有一个函数可以获取基本面数据
        fundamental_data = kwargs.get('fundamental_data', {})
        
        return {
            'stock_code': stock_code,
            'stock_name': kwargs.get('stock_name', ''),
            'fundamental_data': json.dumps(fundamental_data, ensure_ascii=False, indent=2)
        }
    
    def parse_ai_response(self, response: str) -> Dict[str, Any]:
        """解析AI响应为结构化数据"""
        try:
            # 尝试提取JSON内容
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_content = response[json_start:json_end].strip()
            else:
                # 查找第一个{到最后一个}
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_content = response[json_start:json_end]
                else:
                    # 如果没有找到JSON，返回原始文本
                    return {
                        'analysis_type': 'fundamental',
                        'success': True,
                        'content': response,
                        'format': 'text'
                    }
            
            # 解析JSON
            parsed_data = json.loads(json_content)
            parsed_data['success'] = True
            parsed_data['format'] = 'json'
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return {
                'analysis_type': 'fundamental',
                'success': True,
                'content': response,
                'format': 'text',
                'parse_error': str(e)
            }

class TechnicalAnalysisAgent(BaseAIAgent):
    """技术面分析AI Agent"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("technical", api_key)
    
    async def process_input_data(self, **kwargs) -> Dict[str, Any]:
        """处理技术面分析的输入数据"""
        stock_code = kwargs.get('stock_code')
        if not stock_code:
            raise ValueError("stock_code is required for technical analysis")
        
        technical_data = kwargs.get('technical_data', {})
        
        return {
            'stock_code': stock_code,
            'stock_name': kwargs.get('stock_name', ''),
            'technical_data': json.dumps(technical_data, ensure_ascii=False, indent=2)
        }
    
    def parse_ai_response(self, response: str) -> Dict[str, Any]:
        """解析AI响应为结构化数据"""
        # 与基本面分析类似的解析逻辑
        try:
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_content = response[json_start:json_end].strip()
                parsed_data = json.loads(json_content)
            else:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_content = response[json_start:json_end]
                    parsed_data = json.loads(json_content)
                else:
                    return {
                        'analysis_type': 'technical',
                        'success': True,
                        'content': response,
                        'format': 'text'
                    }
            
            parsed_data['success'] = True
            parsed_data['format'] = 'json'
            return parsed_data
            
        except json.JSONDecodeError:
            return {
                'analysis_type': 'technical',
                'success': True,
                'content': response,
                'format': 'text'
            }

class ComprehensiveAnalysisAgent(BaseAIAgent):
    """综合分析AI Agent"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("comprehensive", api_key)
    
    async def process_input_data(self, **kwargs) -> Dict[str, Any]:
        """处理综合分析的输入数据"""
        stock_code = kwargs.get('stock_code')
        if not stock_code:
            raise ValueError("stock_code is required for comprehensive analysis")
        
        # 获取三个维度的数据
        fundamental_data = kwargs.get('fundamental_data', {})
        technical_data = kwargs.get('technical_data', {})
        news_data = kwargs.get('news_data', {})
        
        # 分析风格：professional（专业） 或 insight（深度洞察）
        analysis_style = kwargs.get('analysis_style', 'professional')
        
        return {
            'stock_code': stock_code,
            'analysis_style': analysis_style,
            'fundamental_data': json.dumps(fundamental_data, ensure_ascii=False, indent=2),
            'technical_data': json.dumps(technical_data, ensure_ascii=False, indent=2),
            'news_data': json.dumps(news_data, ensure_ascii=False, indent=2)
        }
    
    def parse_ai_response(self, response: str) -> Dict[str, Any]:
        """解析AI响应为文章内容"""
        return {
            'analysis_type': 'comprehensive',
            'success': True,
            'article_content': response,
            'format': 'article',
            'length': len(response)
        }

class StockAnalysisOrchestrator:
    """股票分析协调器 - 管理多个AI Agent的协同工作"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        
        # 初始化各个Agent
        self.fundamental_agent = FundamentalAnalysisAgent(api_key)
        self.technical_agent = TechnicalAnalysisAgent(api_key)
        self.comprehensive_agent = ComprehensiveAnalysisAgent(api_key)
    
    async def get_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """获取股票基础数据 - 这里可以调用现有的API"""
        # TODO: 集成现有的stock_analysis_api.py中的数据获取逻辑
        # 这是一个占位符实现，实际应该调用现有的API端点
        
        try:
            # 这里应该调用现有的API获取数据
            # fundamental_data = await call_existing_api(f"/stocks/{stock_code}/analysis/fundamental")
            # technical_data = await call_existing_api(f"/stocks/{stock_code}/analysis/technical") 
            # news_data = await call_existing_api(f"/stocks/{stock_code}/news/announcements")
            
            # 暂时返回示例数据结构
            return {
                'stock_code': stock_code,
                'fundamental_data': {'placeholder': 'fundamental data would be here'},
                'technical_data': {'placeholder': 'technical data would be here'},
                'news_data': {'placeholder': 'news data would be here'},
                'stock_name': f'股票{stock_code}'
            }
        except Exception as e:
            logger.error(f"Failed to get stock data for {stock_code}: {e}")
            raise
    
    async def comprehensive_analysis(self, stock_code: str, analysis_styles: Optional[list] = None) -> Dict[str, Any]:
        """
        执行综合股票分析
        
        Args:
            stock_code: 股票代码
            analysis_styles: 分析风格列表，默认为 ['professional', 'insight']
            
        Returns:
            Dict: 包含多篇分析文章的结果
        """
        if analysis_styles is None:
            analysis_styles = ['professional', 'insight']
        
        try:
            logger.info(f"Starting comprehensive analysis for stock {stock_code}")
            
            # 1. 获取基础数据
            stock_data = await self.get_stock_data(stock_code)
            
            # 2. 并行执行基本面和技术面分析
            fundamental_task = self.fundamental_agent.analyze(**stock_data)
            technical_task = self.technical_agent.analyze(**stock_data)
            
            fundamental_result, technical_result = await asyncio.gather(
                fundamental_task, technical_task, return_exceptions=True
            )
            
            # 检查分析结果
            if isinstance(fundamental_result, Exception):
                logger.error(f"Fundamental analysis failed: {fundamental_result}")
                fundamental_result = {'error': str(fundamental_result)}
            
            if isinstance(technical_result, Exception):
                logger.error(f"Technical analysis failed: {technical_result}")
                technical_result = {'error': str(technical_result)}
            
            # 3. 并行生成不同风格的综合分析文章
            article_tasks = []
            for style in analysis_styles:
                task_data = {
                    **stock_data,
                    'analysis_style': style,
                    'fundamental_data': fundamental_result.get('data', {}),
                    'technical_data': technical_result.get('data', {}),
                }
                article_tasks.append(self.comprehensive_agent.analyze(**task_data))
            
            article_results = await asyncio.gather(*article_tasks, return_exceptions=True)
            
            # 4. 整理最终结果
            articles = []
            style_names = {'professional': '专业分析师', 'insight': '深度洞察'}
            
            for i, (style, result) in enumerate(zip(analysis_styles, article_results)):
                if isinstance(result, Exception):
                    logger.error(f"Article generation failed for style {style}: {result}")
                    articles.append({
                        'title': f'{style_names.get(style, style)} - 分析失败',
                        'content': f'生成分析文章时出现错误: {str(result)}',
                        'style': style,
                        'success': False
                    })
                else:
                    articles.append({
                        'title': f'{style_names.get(style, style)} - 专业分析报告',
                        'content': result.get('data', {}).get('article_content', ''),
                        'style': style,
                        'success': result.get('data', {}).get('success', False)
                    })
            
            final_result = {
                'stock_code': stock_code,
                'stock_name': stock_data.get('stock_name', ''),
                'analysis_timestamp': datetime.now().isoformat(),
                'status': 'completed',
                'analysis': {
                    'articles': articles
                },
                'data_sources': {
                    'fundamental': fundamental_result,
                    'technical': technical_result
                },
                'success': True
            }
            
            logger.info(f"Comprehensive analysis completed for stock {stock_code}")
            return final_result
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed for stock {stock_code}: {e}")
            return {
                'stock_code': stock_code,
                'analysis_timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e),
                'success': False
            }

# 创建全局协调器实例
stock_analyzer = StockAnalysisOrchestrator()