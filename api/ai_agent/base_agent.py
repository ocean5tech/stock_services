# -*- coding: utf-8 -*-
"""
基础AI Agent类
Base AI Agent Implementation
"""
import os
import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import logging
from abc import ABC, abstractmethod

# AI相关库
try:
    import anthropic
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    logging.warning("anthropic library not installed. Install with: pip install anthropic")

# Redis缓存（可选）
try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logging.warning("redis library not installed. Install with: pip install redis")

from .prompt_manager import prompt_manager

logger = logging.getLogger(__name__)

class BaseAIAgent(ABC):
    """基础AI Agent类 - 所有AI Agent的基类"""
    
    def __init__(self, agent_name: str, api_key: Optional[str] = None):
        """
        初始化AI Agent
        
        Args:
            agent_name: Agent名称，对应提示词配置文件名
            api_key: Anthropic API Key，如果不提供则从环境变量读取
        """
        self.agent_name = agent_name
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables or parameters")
        
        if not HAS_ANTHROPIC:
            raise ImportError("anthropic library is required. Install with: pip install anthropic")
        
        # 初始化Anthropic客户端
        self.client = Anthropic(api_key=self.api_key)
        
        # 初始化Redis客户端（可选）
        self.redis_client = None
        if HAS_REDIS:
            try:
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                logger.info(f"Redis client initialized for {agent_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis client: {e}")
        
        # 加载Agent配置
        self.config = prompt_manager.load_prompt_config(agent_name)
        self.model_params = prompt_manager.get_model_parameters(agent_name)
        self.cache_config = prompt_manager.get_cache_config(agent_name)
        
        logger.info(f"BaseAIAgent initialized: {agent_name}")
    
    def generate_cache_key(self, **kwargs) -> str:
        """生成缓存键"""
        # 创建包含agent名称和参数的字符串
        key_data = {
            'agent': self.agent_name,
            'params': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        
        # 使用MD5生成短的缓存键
        return f"agent:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从缓存获取结果"""
        if not self.redis_client or not self.cache_config.get('enabled'):
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                result = json.loads(cached_data)
                logger.info(f"Cache hit for {self.agent_name}: {cache_key}")
                return result
        except Exception as e:
            logger.warning(f"Error reading from cache: {e}")
        
        return None
    
    async def set_cached_result(self, cache_key: str, result: Dict[str, Any]):
        """设置缓存结果"""
        if not self.redis_client or not self.cache_config.get('enabled'):
            return
        
        try:
            ttl = self.cache_config.get('ttl', 1800)  # 默认30分钟
            cached_data = json.dumps(result)
            await self.redis_client.setex(cache_key, ttl, cached_data)
            logger.info(f"Cached result for {self.agent_name}: {cache_key} (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"Error writing to cache: {e}")
    
    async def call_ai_model(self, system_prompt: str, user_prompt: str) -> str:
        """
        调用AI模型
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            
        Returns:
            str: AI模型响应
        """
        try:
            # 准备消息
            messages = [
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ]
            
            # 准备参数
            params = {
                "model": self.model_params.get("model", "claude-3-sonnet-20240229"),
                "max_tokens": self.model_params.get("max_tokens", 4000),
                "temperature": self.model_params.get("temperature", 0.1),
                "system": system_prompt,
                "messages": messages
            }
            
            logger.info(f"Calling AI model for {self.agent_name} with model: {params['model']}")
            
            # 调用API
            response = await asyncio.to_thread(
                self.client.messages.create,
                **params
            )
            
            # 提取响应内容
            if response.content and len(response.content) > 0:
                content = response.content[0].text
                logger.info(f"AI model response received for {self.agent_name} (length: {len(content)})")
                return content
            else:
                raise ValueError("Empty response from AI model")
                
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error for {self.agent_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling AI model for {self.agent_name}: {e}")
            raise
    
    @abstractmethod
    async def process_input_data(self, **kwargs) -> Dict[str, Any]:
        """
        处理输入数据 - 子类必须实现
        
        Returns:
            Dict: 处理后的数据，用于填充用户提示词模板
        """
        pass
    
    @abstractmethod  
    def parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        解析AI响应 - 子类必须实现
        
        Args:
            response: AI模型原始响应
            
        Returns:
            Dict: 解析后的结构化数据
        """
        pass
    
    async def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        执行AI分析 - 主要的公共方法
        
        Args:
            **kwargs: 分析参数
            
        Returns:
            Dict: 分析结果
        """
        try:
            # 生成缓存键
            cache_key = self.generate_cache_key(**kwargs)
            
            # 检查缓存
            cached_result = await self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # 处理输入数据
            processed_data = await self.process_input_data(**kwargs)
            
            # 获取提示词
            system_prompt = prompt_manager.get_system_prompt(self.agent_name)
            user_prompt = prompt_manager.get_user_prompt(self.agent_name, **processed_data)
            
            # 调用AI模型
            ai_response = await self.call_ai_model(system_prompt, user_prompt)
            
            # 解析响应
            parsed_result = self.parse_ai_response(ai_response)
            
            # 添加元数据
            result = {
                'agent_name': self.agent_name,
                'analysis_timestamp': datetime.now().isoformat(),
                'model': self.model_params.get("model", "claude-3-sonnet-20240229"),
                'cached': False,
                'data': parsed_result,
                'raw_response': ai_response  # 可选：保留原始响应用于调试
            }
            
            # 缓存结果
            await self.set_cached_result(cache_key, result)
            
            logger.info(f"Analysis completed for {self.agent_name}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed for {self.agent_name}: {e}")
            # 返回错误结果而不是抛出异常
            return {
                'agent_name': self.agent_name,
                'analysis_timestamp': datetime.now().isoformat(),
                'cached': False,
                'error': str(e),
                'success': False
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            'agent_name': self.agent_name,
            'config_version': self.config.get('version', 'unknown'),
            'model': self.model_params.get("model", "claude-3-sonnet-20240229"),
            'cache_enabled': self.cache_config.get('enabled', False),
            'cache_ttl': self.cache_config.get('ttl', 0)
        }