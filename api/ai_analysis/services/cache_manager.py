# -*- coding: utf-8 -*-
"""
缓存管理服务
Cache Management Service
"""
import json
import logging
import redis.asyncio as redis
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AnalysisCache:
    """AI分析缓存管理器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        
        # 缓存TTL设置（秒）
        self.TRADING_SIGNAL_TTL = 1800  # 30分钟
        self.COMPREHENSIVE_EVAL_TTL = 86400  # 24小时
    
    async def connect(self):
        """建立Redis连接"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # 测试连接
            await self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开Redis连接"""
        if self.redis_client:
            await self.redis_client.aclose()
    
    def _generate_cache_key(self, cache_type: str, stock_code: str) -> str:
        """生成缓存键"""
        return f"{cache_type}:{stock_code}"
    
    async def get_trading_signal_cache(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取技术面交易信号缓存"""
        try:
            if not self.redis_client:
                await self.connect()
            
            cache_key = self._generate_cache_key("trading_signal", stock_code)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.info(f"技术面交易信号缓存命中: {stock_code}")
                return data
            
            return None
        except Exception as e:
            logger.error(f"获取技术面交易信号缓存失败 {stock_code}: {e}")
            return None
    
    async def set_trading_signal_cache(self, stock_code: str, data: Dict[str, Any]) -> bool:
        """设置技术面交易信号缓存（30分钟TTL）"""
        try:
            if not self.redis_client:
                await self.connect()
            
            cache_key = self._generate_cache_key("trading_signal", stock_code)
            
            # 添加缓存时间戳和过期时间
            data['cached'] = True
            data['cache_created_at'] = datetime.now().isoformat()
            data['cache_expires_at'] = (datetime.now() + timedelta(seconds=self.TRADING_SIGNAL_TTL)).isoformat()
            
            cached_data = json.dumps(data, ensure_ascii=False)
            result = await self.redis_client.setex(
                cache_key, 
                self.TRADING_SIGNAL_TTL, 
                cached_data
            )
            
            if result:
                logger.info(f"技术面交易信号缓存设置成功: {stock_code} (TTL: 30分钟)")
            
            return result
        except Exception as e:
            logger.error(f"设置技术面交易信号缓存失败 {stock_code}: {e}")
            return False
    
    async def get_comprehensive_cache(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取综合评估缓存"""
        try:
            if not self.redis_client:
                await self.connect()
            
            cache_key = self._generate_cache_key("comprehensive_eval", stock_code)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.info(f"综合评估缓存命中: {stock_code}")
                return data
            
            return None
        except Exception as e:
            logger.error(f"获取综合评估缓存失败 {stock_code}: {e}")
            return None
    
    async def set_comprehensive_cache(self, stock_code: str, data: Dict[str, Any]) -> bool:
        """设置综合评估缓存（24小时TTL）"""
        try:
            if not self.redis_client:
                await self.connect()
            
            cache_key = self._generate_cache_key("comprehensive_eval", stock_code)
            
            # 添加缓存时间戳和过期时间
            data['cached'] = True
            data['cache_created_at'] = datetime.now().isoformat()
            data['cache_expires_at'] = (datetime.now() + timedelta(seconds=self.COMPREHENSIVE_EVAL_TTL)).isoformat()
            
            cached_data = json.dumps(data, ensure_ascii=False)
            result = await self.redis_client.setex(
                cache_key,
                self.COMPREHENSIVE_EVAL_TTL,
                cached_data
            )
            
            if result:
                logger.info(f"综合评估缓存设置成功: {stock_code} (TTL: 24小时)")
            
            return result
        except Exception as e:
            logger.error(f"设置综合评估缓存失败 {stock_code}: {e}")
            return False
    
    async def clear_cache(self, stock_code: str, cache_type: str = "all") -> bool:
        """清除指定股票的缓存"""
        try:
            if not self.redis_client:
                await self.connect()
            
            keys_to_delete = []
            
            if cache_type in ["all", "trading_signal"]:
                keys_to_delete.append(self._generate_cache_key("trading_signal", stock_code))
            
            if cache_type in ["all", "comprehensive_eval"]:
                keys_to_delete.append(self._generate_cache_key("comprehensive_eval", stock_code))
            
            if keys_to_delete:
                deleted_count = await self.redis_client.delete(*keys_to_delete)
                logger.info(f"清除缓存成功: {stock_code}, 删除 {deleted_count} 个键")
                return deleted_count > 0
            
            return True
        except Exception as e:
            logger.error(f"清除缓存失败 {stock_code}: {e}")
            return False
    
    async def get_cache_status(self, stock_code: str) -> Dict[str, Any]:
        """获取指定股票的缓存状态"""
        try:
            if not self.redis_client:
                await self.connect()
            
            status = {
                "stock_code": stock_code,
                "trading_signal": {
                    "exists": False,
                    "ttl": -1,
                    "expires_at": None
                },
                "comprehensive_eval": {
                    "exists": False,
                    "ttl": -1,
                    "expires_at": None
                }
            }
            
            # 检查技术面交易信号缓存
            trading_key = self._generate_cache_key("trading_signal", stock_code)
            trading_ttl = await self.redis_client.ttl(trading_key)
            if trading_ttl > -2:  # -2表示键不存在
                status["trading_signal"]["exists"] = trading_ttl > -1
                status["trading_signal"]["ttl"] = trading_ttl
                if trading_ttl > 0:
                    status["trading_signal"]["expires_at"] = (
                        datetime.now() + timedelta(seconds=trading_ttl)
                    ).isoformat()
            
            # 检查综合评估缓存
            comprehensive_key = self._generate_cache_key("comprehensive_eval", stock_code)
            comprehensive_ttl = await self.redis_client.ttl(comprehensive_key)
            if comprehensive_ttl > -2:
                status["comprehensive_eval"]["exists"] = comprehensive_ttl > -1
                status["comprehensive_eval"]["ttl"] = comprehensive_ttl
                if comprehensive_ttl > 0:
                    status["comprehensive_eval"]["expires_at"] = (
                        datetime.now() + timedelta(seconds=comprehensive_ttl)
                    ).isoformat()
            
            return status
        except Exception as e:
            logger.error(f"获取缓存状态失败 {stock_code}: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """缓存健康检查"""
        try:
            if not self.redis_client:
                await self.connect()
            
            # 执行ping测试
            ping_result = await self.redis_client.ping()
            
            # 获取Redis信息
            info = await self.redis_client.info()
            
            return {
                "status": "healthy" if ping_result else "unhealthy",
                "ping": ping_result,
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "total_connections_received": info.get("total_connections_received", 0),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"缓存健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 全局缓存管理器实例
analysis_cache = AnalysisCache()