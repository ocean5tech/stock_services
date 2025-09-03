# -*- coding: utf-8 -*-
"""
美国股票服务API
US Stock Service API - Port 3004
"""
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import time

from database import get_db, USStock, APILog, init_database, test_database_connection
from akshare_service import AkshareService
from config import Config

# 配置日志 / Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=Config.API_TITLE_US,
    version=Config.API_VERSION,
    description="美国股票信息服务API，提供实时美股数据、公司信息和财务指标 / US stock information service API providing real-time US stock data, company information and financial indicators"
)

# 添加CORS中间件 / Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化akshare服务 / Initialize akshare service
akshare_service = AkshareService()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """API请求日志中间件 / API request logging middleware"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # 记录API调用日志 / Log API calls
    try:
        db = next(get_db())
        log_entry = APILog(
            service_type="us_stock",
            endpoint=str(request.url.path),
            method=request.method,
            request_params=str(request.query_params) if request.query_params else None,
            response_status=response.status_code,
            response_time=process_time,
            client_ip=request.client.host,
            created_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        db.close()
    except Exception as e:
        logger.error(f"日志记录失败 / Failed to log request: {str(e)}")
    
    return response

@app.on_event("startup")
async def startup_event():
    """应用启动事件 / Application startup event"""
    logger.info("美国股票服务API启动中 / US Stock Service API starting...")
    
    # 测试数据库连接 / Test database connection
    if not test_database_connection():
        logger.error("数据库连接失败，服务无法启动 / Database connection failed, service cannot start")
        raise Exception("Database connection failed")
    
    # 初始化数据库表 / Initialize database tables
    if not init_database():
        logger.error("数据库初始化失败 / Database initialization failed")
        raise Exception("Database initialization failed")
    
    logger.info(f"美国股票服务API已在端口{Config.US_STOCK_PORT}启动 / US Stock Service API started on port {Config.US_STOCK_PORT}")

@app.get("/", summary="服务状态检查 / Service health check")
async def root():
    """服务状态检查端点 / Service health check endpoint"""
    return {
        "service": "US Stock Service",
        "status": "running",
        "version": Config.API_VERSION,
        "server_ip": Config.SERVER_IP,
        "port": Config.US_STOCK_PORT,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", summary="健康检查 / Health check")
async def health_check(db: Session = Depends(get_db)):
    """健康检查端点，包含数据库连接测试 / Health check endpoint with database connection test"""
    try:
        # 测试数据库查询 / Test database query
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"服务不可用 / Service unavailable: {str(e)}")

@app.get("/stocks/{stock_symbol}", summary="获取指定美股详细信息 / Get specific US stock detailed information")
async def get_stock_info(
    stock_symbol: str,
    refresh: bool = Query(False, description="是否强制刷新数据 / Whether to force refresh data"),
    db: Session = Depends(get_db)
):
    """
    获取指定美股的详细信息
    Get detailed information for a specific US stock
    
    - **stock_symbol**: 股票代码，如 AAPL, MSFT, GOOGL 等 / Stock symbol, e.g., AAPL, MSFT, GOOGL
    - **refresh**: 是否强制从akshare刷新数据 / Whether to force refresh from akshare
    """
    try:
        # 将股票代码转换为大写 / Convert stock symbol to uppercase
        stock_symbol = stock_symbol.upper()
        
        # 检查数据库中是否有缓存数据 / Check if there's cached data in database
        cached_stock = db.query(USStock).filter(USStock.stock_symbol == stock_symbol).first()
        
        # 判断是否需要刷新数据 / Determine if data refresh is needed
        need_refresh = (
            refresh or 
            cached_stock is None or 
            (datetime.utcnow() - cached_stock.last_updated).total_seconds() > Config.STOCK_DATA_CACHE_MINUTES * 60
        )
        
        if need_refresh:
            # 从akshare获取最新数据 / Get latest data from akshare
            stock_data = akshare_service.get_us_stock_info(stock_symbol)
            
            if stock_data is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"股票代码 {stock_symbol} 不存在或获取数据失败 / Stock symbol {stock_symbol} not found or failed to fetch data"
                )
            
            # 更新或创建数据库记录 / Update or create database record
            if cached_stock:
                # 更新现有记录 / Update existing record
                for key, value in stock_data.items():
                    if hasattr(cached_stock, key):
                        setattr(cached_stock, key, value)
                cached_stock.last_updated = datetime.utcnow()
            else:
                # 创建新记录 / Create new record
                cached_stock = USStock(**stock_data)
                db.add(cached_stock)
            
            db.commit()
            
            # 验证数据库操作 / Verify database operation
            db.refresh(cached_stock)
            verification_query = db.query(USStock).filter(USStock.stock_symbol == stock_symbol).first()
            if verification_query is None:
                logger.error(f"数据库验证失败：股票 {stock_symbol} 未找到 / Database verification failed: Stock {stock_symbol} not found")
                raise HTTPException(status_code=500, detail="数据库操作验证失败 / Database operation verification failed")
        
        # 返回股票信息 / Return stock information
        return {
            "stock_symbol": cached_stock.stock_symbol,
            "stock_name_en": cached_stock.stock_name_en,
            "stock_name_cn": cached_stock.stock_name_cn,
            "company_background": cached_stock.company_background,
            "current_price": cached_stock.current_price,
            "price_change": cached_stock.price_change,
            "price_change_pct": cached_stock.price_change_pct,
            "open_price": cached_stock.open_price,
            "close_price": cached_stock.close_price,
            "high_price": cached_stock.high_price,
            "low_price": cached_stock.low_price,
            "volume": cached_stock.volume,
            "turnover": cached_stock.turnover,
            "market_cap": cached_stock.market_cap,
            "total_shares": cached_stock.total_shares,
            "pe_ratio": cached_stock.pe_ratio,
            "pb_ratio": cached_stock.pb_ratio,
            "sector": cached_stock.sector,
            "exchange": cached_stock.exchange,
            "is_active": cached_stock.is_active,
            "last_updated": cached_stock.last_updated.isoformat(),
            "created_at": cached_stock.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取美股信息失败 / Failed to get US stock info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/stocks", summary="获取美股列表 / Get US stock list")
async def get_stocks_list(
    page: int = Query(1, ge=1, description="页码 / Page number"),
    limit: int = Query(20, ge=1, le=100, description="每页数量 / Items per page"),
    search: Optional[str] = Query(None, description="搜索关键词（股票代码或名称）/ Search keyword (stock symbol or name)"),
    sector: Optional[str] = Query(None, description="行业筛选 / Sector filter"),
    exchange: Optional[str] = Query(None, description="交易所筛选 / Exchange filter"),
    sort_by: str = Query("stock_symbol", description="排序字段 / Sort field"),
    sort_order: str = Query("asc", description="排序顺序：asc或desc / Sort order: asc or desc"),
    active_only: bool = Query(True, description="只显示活跃股票 / Show active stocks only"),
    db: Session = Depends(get_db)
):
    """
    获取美股列表，支持分页、搜索和排序
    Get US stock list with pagination, search and sorting support
    """
    try:
        # 构建查询条件 / Build query conditions
        query = db.query(USStock)
        
        if active_only:
            query = query.filter(USStock.is_active == True)
        
        if search:
            search_condition = or_(
                USStock.stock_symbol.contains(search.upper()),
                USStock.stock_name_en.contains(search),
                USStock.stock_name_cn.contains(search)
            )
            query = query.filter(search_condition)
        
        if sector:
            query = query.filter(USStock.sector.contains(sector))
        
        if exchange:
            query = query.filter(USStock.exchange == exchange.upper())
        
        # 排序 / Sorting
        if hasattr(USStock, sort_by):
            sort_column = getattr(USStock, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        # 计算总数 / Calculate total count
        total_count = query.count()
        
        # 分页 / Pagination
        offset = (page - 1) * limit
        stocks = query.offset(offset).limit(limit).all()
        
        # 格式化返回数据 / Format return data
        stocks_data = []
        for stock in stocks:
            stocks_data.append({
                "stock_symbol": stock.stock_symbol,
                "stock_name_en": stock.stock_name_en,
                "stock_name_cn": stock.stock_name_cn,
                "current_price": stock.current_price,
                "price_change": stock.price_change,
                "price_change_pct": stock.price_change_pct,
                "market_cap": stock.market_cap,
                "volume": stock.volume,
                "sector": stock.sector,
                "exchange": stock.exchange,
                "last_updated": stock.last_updated.isoformat() if stock.last_updated else None
            })
        
        return {
            "stocks": stocks_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"获取美股列表失败 / Failed to get US stock list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.post("/stocks/{stock_symbol}/refresh", summary="刷新指定美股数据 / Refresh specific US stock data")
async def refresh_stock_data(stock_symbol: str, db: Session = Depends(get_db)):
    """
    强制刷新指定美股的数据
    Force refresh data for a specific US stock
    """
    try:
        stock_symbol = stock_symbol.upper()
        
        # 从akshare获取最新数据 / Get latest data from akshare
        stock_data = akshare_service.get_us_stock_info(stock_symbol)
        
        if stock_data is None:
            raise HTTPException(
                status_code=404, 
                detail=f"股票代码 {stock_symbol} 不存在或获取数据失败 / Stock symbol {stock_symbol} not found or failed to fetch data"
            )
        
        # 查找现有记录 / Find existing record
        existing_stock = db.query(USStock).filter(USStock.stock_symbol == stock_symbol).first()
        
        if existing_stock:
            # 更新现有记录 / Update existing record
            for key, value in stock_data.items():
                if hasattr(existing_stock, key):
                    setattr(existing_stock, key, value)
            existing_stock.last_updated = datetime.utcnow()
        else:
            # 创建新记录 / Create new record
            existing_stock = USStock(**stock_data)
            db.add(existing_stock)
        
        db.commit()
        
        # 验证数据库操作 / Verify database operation
        db.refresh(existing_stock)
        verification_query = db.query(USStock).filter(USStock.stock_symbol == stock_symbol).first()
        if verification_query is None:
            logger.error(f"数据库验证失败：股票 {stock_symbol} 刷新后未找到 / Database verification failed: Stock {stock_symbol} not found after refresh")
            raise HTTPException(status_code=500, detail="数据库操作验证失败 / Database operation verification failed")
        
        return {
            "message": f"股票 {stock_symbol} 数据刷新成功 / Stock {stock_symbol} data refreshed successfully",
            "stock_symbol": stock_symbol,
            "last_updated": existing_stock.last_updated.isoformat(),
            "current_price": existing_stock.current_price
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新美股数据失败 / Failed to refresh US stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.delete("/stocks/{stock_symbol}", summary="删除指定美股数据 / Delete specific US stock data")
async def delete_stock_data(stock_symbol: str, db: Session = Depends(get_db)):
    """
    删除指定美股的数据（软删除，设置为不活跃）
    Delete data for a specific US stock (soft delete, set as inactive)
    """
    try:
        stock_symbol = stock_symbol.upper()
        
        # 查找股票记录 / Find stock record
        stock = db.query(USStock).filter(USStock.stock_symbol == stock_symbol).first()
        
        if not stock:
            raise HTTPException(
                status_code=404, 
                detail=f"股票代码 {stock_symbol} 不存在 / Stock symbol {stock_symbol} not found"
            )
        
        # 软删除：设置为不活跃 / Soft delete: set as inactive
        stock.is_active = False
        stock.last_updated = datetime.utcnow()
        
        db.commit()
        
        # 验证数据库操作 / Verify database operation
        db.refresh(stock)
        verification_query = db.query(USStock).filter(
            and_(USStock.stock_symbol == stock_symbol, USStock.is_active == False)
        ).first()
        if verification_query is None:
            logger.error(f"数据库验证失败：股票 {stock_symbol} 删除后验证失败 / Database verification failed: Stock {stock_symbol} deletion verification failed")
            raise HTTPException(status_code=500, detail="数据库操作验证失败 / Database operation verification failed")
        
        return {
            "message": f"股票 {stock_symbol} 数据已删除 / Stock {stock_symbol} data deleted",
            "stock_symbol": stock_symbol,
            "deleted_at": stock.last_updated.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除美股数据失败 / Failed to delete US stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/sectors", summary="获取行业列表 / Get sector list")
async def get_sectors(db: Session = Depends(get_db)):
    """
    获取所有行业列表
    Get all sector list
    """
    try:
        sectors_query = db.query(USStock.sector).filter(
            and_(USStock.sector.isnot(None), USStock.sector != "", USStock.is_active == True)
        ).distinct().all()
        
        sectors = [sector[0] for sector in sectors_query if sector[0]]
        
        return {
            "sectors": sorted(sectors),
            "total_count": len(sectors)
        }
        
    except Exception as e:
        logger.error(f"获取行业列表失败 / Failed to get sectors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/exchanges", summary="获取交易所列表 / Get exchange list")
async def get_exchanges(db: Session = Depends(get_db)):
    """
    获取所有交易所列表
    Get all exchange list
    """
    try:
        exchanges_query = db.query(USStock.exchange).filter(
            and_(USStock.exchange.isnot(None), USStock.exchange != "", USStock.is_active == True)
        ).distinct().all()
        
        exchanges = [exchange[0] for exchange in exchanges_query if exchange[0]]
        
        return {
            "exchanges": sorted(exchanges),
            "total_count": len(exchanges)
        }
        
    except Exception as e:
        logger.error(f"获取交易所列表失败 / Failed to get exchanges: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/stats", summary="获取美股统计信息 / Get US stock statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """
    获取美股服务统计信息
    Get US stock service statistics
    """
    try:
        # 统计活跃股票数量 / Count active stocks
        active_stocks_count = db.query(USStock).filter(USStock.is_active == True).count()
        
        # 统计总股票数量 / Count total stocks
        total_stocks_count = db.query(USStock).count()
        
        # 统计今日API调用次数 / Count today's API calls
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_api_calls = db.query(APILog).filter(
            and_(
                APILog.service_type == "us_stock",
                APILog.created_at >= today_start
            )
        ).count()
        
        # 统计各交易所股票数量 / Count stocks by exchange
        from sqlalchemy import func
        exchange_stats = db.query(
            USStock.exchange,
            func.count(USStock.stock_symbol).label('count')
        ).filter(USStock.is_active == True).group_by(USStock.exchange).all()
        
        exchange_distribution = {exchange: count for exchange, count in exchange_stats if exchange}
        
        # 获取最新更新的股票 / Get latest updated stocks
        latest_updated_stocks = db.query(USStock).filter(
            USStock.is_active == True
        ).order_by(USStock.last_updated.desc()).limit(5).all()
        
        latest_stocks_data = []
        for stock in latest_updated_stocks:
            latest_stocks_data.append({
                "stock_symbol": stock.stock_symbol,
                "stock_name_en": stock.stock_name_en,
                "current_price": stock.current_price,
                "price_change_pct": stock.price_change_pct,
                "exchange": stock.exchange,
                "last_updated": stock.last_updated.isoformat()
            })
        
        return {
            "service": "US Stock Service",
            "statistics": {
                "active_stocks_count": active_stocks_count,
                "total_stocks_count": total_stocks_count,
                "today_api_calls": today_api_calls,
                "exchange_distribution": exchange_distribution,
                "latest_updated_stocks": latest_stocks_data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败 / Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "us_stock_api:app", 
        host="0.0.0.0", 
        port=Config.US_STOCK_PORT,
        reload=True
    )