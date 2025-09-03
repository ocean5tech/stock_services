# -*- coding: utf-8 -*-
"""
数据库连接和模型定义模块
Database connection and model definition module
"""
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from datetime import datetime
import asyncio
from config import Config

# 创建数据库引擎，使用连接池 / Create database engine with connection pool
engine = create_engine(
    Config.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# 创建会话工厂 / Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类 / Create base model class
Base = declarative_base()

class ChineseStock(Base):
    """中国股票信息表 / Chinese stock information table"""
    __tablename__ = "chinese_stocks"
    
    stock_code = Column(String(20), primary_key=True, comment="股票代码")
    stock_name_cn = Column(String(100), nullable=False, comment="中文股票名称")
    stock_name_en = Column(String(100), comment="英文股票名称")
    company_background = Column(Text, comment="公司背景信息")
    market_cap = Column(Float, comment="市值")
    total_shares = Column(Float, comment="总股本")
    current_price = Column(Float, comment="最新价格")
    price_change = Column(Float, comment="涨跌额")
    price_change_pct = Column(Float, comment="涨跌幅百分比")
    volume = Column(Float, comment="成交量")
    turnover = Column(Float, comment="成交额")
    pe_ratio = Column(Float, comment="市盈率")
    pb_ratio = Column(Float, comment="市净率")
    high_price = Column(Float, comment="最高价")
    low_price = Column(Float, comment="最低价")
    open_price = Column(Float, comment="开盘价")
    close_price = Column(Float, comment="收盘价")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    last_updated = Column(DateTime, default=datetime.utcnow, comment="最后更新时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

class USStock(Base):
    """美国股票信息表 / US stock information table"""
    __tablename__ = "us_stocks"
    
    stock_symbol = Column(String(20), primary_key=True, comment="股票代码")
    stock_name_en = Column(String(200), nullable=False, comment="英文股票名称")
    stock_name_cn = Column(String(200), comment="中文股票名称")
    company_background = Column(Text, comment="公司背景信息")
    market_cap = Column(Float, comment="市值")
    total_shares = Column(Float, comment="总股本")
    current_price = Column(Float, comment="最新价格")
    price_change = Column(Float, comment="涨跌额")
    price_change_pct = Column(Float, comment="涨跌幅百分比")
    volume = Column(Float, comment="成交量")
    turnover = Column(Float, comment="成交额")
    pe_ratio = Column(Float, comment="市盈率")
    pb_ratio = Column(Float, comment="市净率")
    high_price = Column(Float, comment="最高价")
    low_price = Column(Float, comment="最低价")
    open_price = Column(Float, comment="开盘价")
    close_price = Column(Float, comment="收盘价")
    sector = Column(String(100), comment="所属行业")
    exchange = Column(String(50), comment="交易所")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    last_updated = Column(DateTime, default=datetime.utcnow, comment="最后更新时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

class ChineseFutures(Base):
    """中国期货信息表 / Chinese futures information table"""
    __tablename__ = "chinese_futures"
    
    futures_code = Column(String(20), primary_key=True, comment="期货代码")
    futures_name = Column(String(100), nullable=False, comment="期货名称")
    contract_month = Column(String(20), comment="合约月份")
    underlying_asset = Column(String(100), comment="标的资产")
    contract_size = Column(Float, comment="合约规模")
    tick_size = Column(Float, comment="最小变动价位")
    current_price = Column(Float, comment="最新价格")
    price_change = Column(Float, comment="涨跌额")
    price_change_pct = Column(Float, comment="涨跌幅百分比")
    volume = Column(Float, comment="成交量")
    open_interest = Column(Float, comment="持仓量")
    settlement_price = Column(Float, comment="结算价")
    high_price = Column(Float, comment="最高价")
    low_price = Column(Float, comment="最低价")
    open_price = Column(Float, comment="开盘价")
    close_price = Column(Float, comment="收盘价")
    exchange = Column(String(50), comment="交易所")
    trading_unit = Column(String(50), comment="交易单位")
    delivery_month = Column(String(50), comment="交割月份")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    last_updated = Column(DateTime, default=datetime.utcnow, comment="最后更新时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

class APILog(Base):
    """API调用日志表 / API call log table"""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_type = Column(String(50), nullable=False, comment="服务类型")
    endpoint = Column(String(200), nullable=False, comment="API端点")
    method = Column(String(10), nullable=False, comment="HTTP方法")
    request_params = Column(Text, comment="请求参数")
    response_status = Column(Integer, comment="响应状态码")
    response_time = Column(Float, comment="响应时间(秒)")
    client_ip = Column(String(50), comment="客户端IP")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

def get_db():
    """获取数据库会话 / Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """初始化数据库，创建所有表 / Initialize database, create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功 / Database tables created successfully")
        return True
    except Exception as e:
        print(f"数据库初始化失败 / Database initialization failed: {str(e)}")
        return False

def test_database_connection():
    """测试数据库连接 / Test database connection"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("数据库连接测试成功 / Database connection test successful")
        return True
    except Exception as e:
        print(f"数据库连接测试失败 / Database connection test failed: {str(e)}")
        return False