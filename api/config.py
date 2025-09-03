# -*- coding: utf-8 -*-
"""
配置管理模块
Configuration management module for stock services
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """应用配置类 / Application configuration class"""
    
    # 数据库配置 / Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/stock_services")
    ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/stock_services")
    
    # 服务器配置 / Server configuration
    SERVER_IP = "35.77.54.203"
    CHINESE_STOCK_PORT = 3003
    US_STOCK_PORT = 3004
    FUTURES_PORT = 3005
    
    # API配置 / API configuration
    API_TITLE_CN = "中国股票服务API"
    API_TITLE_US = "美国股票服务API"
    API_TITLE_FUTURES = "中国期货服务API"
    API_VERSION = "1.0.0"
    
    # Redis配置 / Redis configuration (for caching)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # 安全配置 / Security configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "stock_services_secret_key_2024")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # 数据更新频率配置 / Data update frequency configuration
    STOCK_DATA_CACHE_MINUTES = 5  # 股票数据缓存5分钟
    FUTURES_DATA_CACHE_MINUTES = 3  # 期货数据缓存3分钟
    
    # akshare配置 / akshare configuration
    AKSHARE_TIMEOUT = 30  # 请求超时时间
    MAX_RETRY_ATTEMPTS = 3  # 最大重试次数