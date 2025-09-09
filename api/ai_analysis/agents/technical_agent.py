# -*- coding: utf-8 -*-
"""
技术面分析AI Agent
Technical Analysis AI Agent
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .base_agent import BaseAIAgent

logger = logging.getLogger(__name__)

class TechnicalAnalysisAgent(BaseAIAgent):
    """技术面分析AI Agent - 提供即时交易信号"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("technical_trading_agent", api_key)
    
    def parse_response(self, response_content: str) -> Dict[str, Any]:
        """解析技术面分析AI响应"""
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
                        "immediate_trading_signal": {
                            "action": "观望",
                            "entry_condition": "AI分析未能提供结构化信号",
                            "stop_loss": {"price": None, "basis": "无法确定"},
                            "take_profit": []
                        }
                    }
            
            # 解析JSON内容
            parsed_data = json.loads(json_content)
            
            # 确保包含必需的字段
            if "immediate_trading_signal" not in parsed_data:
                parsed_data["immediate_trading_signal"] = {
                    "action": "观望",
                    "entry_condition": "分析不完整",
                    "stop_loss": {"price": None, "basis": "无法确定"},
                    "take_profit": []
                }
            
            parsed_data.update({
                "parsed": True,
                "format": "json",
                "raw_content": response_content
            })
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"技术面分析JSON解析失败: {e}")
            return {
                "parsed": False,
                "format": "text",
                "raw_content": response_content,
                "parse_error": str(e),
                "immediate_trading_signal": {
                    "action": "观望",
                    "entry_condition": "AI分析格式解析失败",
                    "stop_loss": {"price": None, "basis": "无法确定"},
                    "take_profit": []
                }
            }
        except Exception as e:
            logger.error(f"技术面分析响应解析失败: {e}")
            return {
                "parsed": False,
                "format": "error",
                "error": str(e),
                "raw_content": response_content,
                "immediate_trading_signal": {
                    "action": "观望",
                    "entry_condition": "分析处理错误",
                    "stop_loss": {"price": None, "basis": "无法确定"},
                    "take_profit": []
                }
            }
    
    async def analyze_trading_signal(self, stock_data: str, stock_code: str) -> Dict[str, Any]:
        """分析股票技术面并提供交易信号"""
        
        # 系统提示词 - 专注于日线级别的技术分析和交易信号
        system_prompt = """你是一位专业的股票技术分析师，专门提供基于技术分析的即时交易信号。

你的任务：
1. 分析提供的股票技术数据（实时报价、K线数据、技术指标）
2. 基于日线级别的技术分析给出具体的买卖信号
3. 提供明确的进场条件、止损位和目标价位
4. 以JSON格式返回结构化的交易建议

分析重点：
- 技术指标信号（移动平均线、RSI、MACD、布林带等）
- K线形态和价格行为
- 支撑位和阻力位
- 成交量分析
- 短期趋势判断

返回格式要求：
```json
{
  "immediate_trading_signal": {
    "action": "买入/卖出/观望/减仓",
    "entry_condition": "具体的入场条件描述",
    "confidence_level": "高/中/低",
    "stop_loss": {
      "price": 具体价格,
      "basis": "技术依据说明"
    },
    "take_profit": [
      {
        "price": 目标价格1,
        "basis": "目标位技术依据"
      }
    ]
  },
  "technical_summary": {
    "trend": "上涨/下跌/震荡",
    "key_levels": {
      "support": [支撑位数组],
      "resistance": [阻力位数组]
    },
    "indicators_status": "主要指标状态总结"
  },
  "risk_warning": "主要风险提示"
}
```

重要提醒：
- 必须基于实际技术数据给出建议，不能凭空推测
- 价格建议要合理，与当前价格相关联
- 止损位必须有明确的技术依据
- 如果数据不足或信号不明确，建议"观望"
"""
        
        # 用户提示词模板
        user_prompt = f"""请分析以下股票的技术面数据，并提供即时交易信号：

股票代码：{stock_code}
分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== 股票技术数据 ===
{stock_data}

请基于以上数据进行技术分析，并按照要求的JSON格式返回交易信号。
特别注意：
1. 交易信号必须有明确的技术依据
2. 止损和目标价位要结合当前价格水平
3. 如果技术信号不明确，请建议"观望"
4. 考虑当前市场环境和风险控制
"""
        
        # 执行分析
        return await self.analyze(system_prompt, user_prompt, stock_code=stock_code)