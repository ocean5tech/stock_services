# -*- coding: utf-8 -*-
"""
AI Agent基础类
Base AI Agent Class
"""
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)

class BaseAIAgent:
    """AI Agent基础类"""
    
    def __init__(self, agent_name: str, api_key: Optional[str] = None):
        self.agent_name = agent_name
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY环境变量未设置或未提供API密钥")
        
        # 初始化Anthropic客户端
        self.client = AsyncAnthropic(api_key=self.api_key)
        
        # 默认配置
        self.model = "claude-3-5-sonnet-20241022"  # 更新到最新的模型版本
        self.max_tokens = 4000
        self.temperature = 0.3
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def call_anthropic_api(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """调用Anthropic Claude API"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"调用Claude API (尝试 {attempt + 1}/{self.max_retries})")
                
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": user_prompt
                    }]
                )
                
                # 提取响应内容
                content = ""
                if response.content and len(response.content) > 0:
                    content = response.content[0].text
                
                logger.info(f"Claude API调用成功，响应长度: {len(content)}")
                
                return {
                    "success": True,
                    "content": content,
                    "model": response.model,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Claude API调用失败 (尝试 {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    # 如果不是最后一次尝试，等待后重试
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    # 所有尝试都失败了
                    return {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "timestamp": datetime.now().isoformat()
                    }
    
    def validate_input_data(self, **kwargs) -> Dict[str, Any]:
        """验证输入数据 - 子类可重写"""
        stock_code = kwargs.get('stock_code')
        if not stock_code:
            return {"valid": False, "error": "stock_code is required"}
        
        if not isinstance(stock_code, str) or len(stock_code) != 6 or not stock_code.isdigit():
            return {"valid": False, "error": "stock_code must be a 6-digit string"}
        
        return {"valid": True}
    
    def parse_response(self, response_content: str) -> Dict[str, Any]:
        """解析AI响应 - 子类应重写此方法"""
        return {
            "raw_content": response_content,
            "parsed": False,
            "timestamp": datetime.now().isoformat()
        }
    
    async def analyze(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """执行AI分析"""
        try:
            # 验证输入
            validation = self.validate_input_data(**kwargs)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"],
                    "agent": self.agent_name
                }
            
            # 调用AI API
            api_response = await self.call_anthropic_api(system_prompt, user_prompt)
            
            if not api_response["success"]:
                return {
                    "success": False,
                    "error": api_response["error"],
                    "agent": self.agent_name,
                    "api_response": api_response
                }
            
            # 解析响应
            parsed_response = self.parse_response(api_response["content"])
            
            return {
                "success": True,
                "agent": self.agent_name,
                "analysis": parsed_response,
                "api_usage": api_response.get("usage", {}),
                "model": api_response.get("model", self.model),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI分析失败 ({self.agent_name}): {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "agent_name": self.agent_name,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "max_retries": self.max_retries,
            "api_key_configured": bool(self.api_key)
        }