# -*- coding: utf-8 -*-
"""
综合评估AI Agent
Comprehensive Evaluation AI Agent
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .base_agent import BaseAIAgent

logger = logging.getLogger(__name__)

class ComprehensiveAnalysisAgent(BaseAIAgent):
    """综合股票评估AI Agent - 提供完整的多维度分析"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("comprehensive_evaluation_agent", api_key)
    
    def parse_response(self, response_content: str) -> Dict[str, Any]:
        """解析综合评估AI响应"""
        try:
            # 尝试从响应中提取JSON结构
            if '```json' in response_content:
                json_start = response_content.find('```json') + 7
                json_end = response_content.find('```', json_start)
                json_content = response_content[json_start:json_end].strip()
            else:
                # 查找第一个{到最后一个}
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_content = response_content[json_start:json_end]
                else:
                    # 没有找到JSON，返回原始文本
                    return {
                        "parsed": False,
                        "format": "text",
                        "raw_content": response_content,
                        "comprehensive_evaluation": {
                            "investment_rating": "中性",
                            "target_price": None,
                            "upside_potential": "无法评估"
                        },
                        "evidence_and_reasoning": {
                            "key_supporting_data": [],
                            "reasoning_chain": ["AI分析未能提供结构化评估"],
                            "uncertainty_factors": ["分析格式不完整"]
                        }
                    }
            
            # 解析JSON内容
            parsed_data = json.loads(json_content)
            
            # 确保包含必需的字段
            if "comprehensive_evaluation" not in parsed_data:
                parsed_data["comprehensive_evaluation"] = {
                    "investment_rating": "中性",
                    "target_price": None,
                    "upside_potential": "无法评估"
                }
            
            if "evidence_and_reasoning" not in parsed_data:
                parsed_data["evidence_and_reasoning"] = {
                    "key_supporting_data": [],
                    "reasoning_chain": [],
                    "uncertainty_factors": []
                }
            
            parsed_data.update({
                "parsed": True,
                "format": "json",
                "raw_content": response_content
            })
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"综合评估JSON解析失败: {e}")
            return {
                "parsed": False,
                "format": "text", 
                "raw_content": response_content,
                "parse_error": str(e),
                "comprehensive_evaluation": {
                    "investment_rating": "中性",
                    "target_price": None,
                    "upside_potential": "无法评估"
                },
                "evidence_and_reasoning": {
                    "key_supporting_data": [],
                    "reasoning_chain": ["AI分析格式解析失败"],
                    "uncertainty_factors": ["响应格式问题"]
                }
            }
        except Exception as e:
            logger.error(f"综合评估响应解析失败: {e}")
            return {
                "parsed": False,
                "format": "error",
                "error": str(e),
                "raw_content": response_content,
                "comprehensive_evaluation": {
                    "investment_rating": "中性",
                    "target_price": None,
                    "upside_potential": "无法评估"
                },
                "evidence_and_reasoning": {
                    "key_supporting_data": [],
                    "reasoning_chain": ["分析处理错误"],
                    "uncertainty_factors": ["系统处理异常"]
                }
            }
    
    async def analyze_comprehensive_evaluation(self, stock_data: str, stock_code: str) -> Dict[str, Any]:
        """综合评估股票投资价值"""
        
        # 系统提示词 - 专注于全面的股票投资价值分析
        system_prompt = """你是一位资深的股票投资分析师，具有丰富的基本面分析和投资评估经验。

你的任务：
1. 综合分析提供的所有股票数据（基本面、技术面、财务、消息面）
2. 基于多维度分析给出投资评级和目标价位
3. 提供详细的投资推理过程和支撑数据
4. 识别关键的不确定性因素和风险
5. 以JSON格式返回结构化的综合评估

分析维度：
- 基本面分析（财务指标、盈利能力、成长性）
- 技术面分析（趋势、支撑阻力、技术指标）
- 估值分析（PE、PB、PS等估值指标）
- 行业对比和竞争地位
- 消息面影响（公告、龙虎榜、资金流向）
- 宏观经济和政策环境

返回格式要求：
```json
{
  "comprehensive_evaluation": {
    "investment_rating": "推荐/中性/减持",
    "target_price": 具体目标价,
    "upside_potential": "涨幅空间百分比",
    "time_horizon": "预期达到时间",
    "confidence_level": "高/中/低"
  },
  "evidence_and_reasoning": {
    "key_supporting_data": [
      "支撑投资观点的关键数据点"
    ],
    "reasoning_chain": [
      "推理步骤1",
      "推理步骤2",
      "推理步骤3"
    ],
    "uncertainty_factors": [
      "主要不确定性因素和风险"
    ]
  },
  "detailed_analysis": {
    "fundamental_strength": "基本面强度评估",
    "technical_outlook": "技术面前景",
    "valuation_assessment": "估值水平评估",
    "risk_factors": ["主要风险因素"],
    "catalysts": ["正面催化因素"]
  },
  "sector_comparison": {
    "industry_position": "行业地位评估",
    "relative_valuation": "相对估值情况",
    "competitive_advantages": ["竞争优势"]
  }
}
```

重要原则：
- 必须基于提供的实际数据进行分析
- 投资建议要有充分的数据支撑
- 承认分析的局限性和不确定性
- 提供清晰的投资逻辑和风险提示
- 目标价要有合理的计算依据
"""
        
        # 用户提示词模板
        user_prompt = f"""请对以下股票进行全面的投资价值评估：

股票代码：{stock_code}
分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== 综合股票数据 ===
{stock_data}

请基于以上所有数据进行综合分析，并按照要求的JSON格式返回投资评估。
特别要求：
1. 投资评级必须有充分的数据支撑和推理过程
2. 目标价要结合估值方法和行业水平
3. 明确指出分析依据的关键数据点
4. 识别影响投资决策的不确定性因素
5. 提供完整的投资逻辑链条
6. 考虑当前市场环境和行业趋势
"""
        
        # 执行分析
        return await self.analyze(system_prompt, user_prompt, stock_code=stock_code)