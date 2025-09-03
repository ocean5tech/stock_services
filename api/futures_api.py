# -*- coding: utf-8 -*-
"""
中国期货服务API
Chinese Futures Service API - Port 3005
"""
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import time

from database import get_db, ChineseFutures, APILog, init_database, test_database_connection
from akshare_service import AkshareService
from config import Config

# 配置日志 / Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=Config.API_TITLE_FUTURES,
    version=Config.API_VERSION,
    description="中国期货信息服务API，提供实时期货数据、合约信息和交易数据 / Chinese futures information service API providing real-time futures data, contract information and trading data"
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
            service_type="futures",
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
    logger.info("中国期货服务API启动中 / Chinese Futures Service API starting...")
    
    # 测试数据库连接 / Test database connection
    if not test_database_connection():
        logger.error("数据库连接失败，服务无法启动 / Database connection failed, service cannot start")
        raise Exception("Database connection failed")
    
    # 初始化数据库表 / Initialize database tables
    if not init_database():
        logger.error("数据库初始化失败 / Database initialization failed")
        raise Exception("Database initialization failed")
    
    logger.info(f"中国期货服务API已在端口{Config.FUTURES_PORT}启动 / Chinese Futures Service API started on port {Config.FUTURES_PORT}")

@app.get("/", summary="服务状态检查 / Service health check")
async def root():
    """服务状态检查端点 / Service health check endpoint"""
    return {
        "service": "Chinese Futures Service",
        "status": "running",
        "version": Config.API_VERSION,
        "server_ip": Config.SERVER_IP,
        "port": Config.FUTURES_PORT,
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

@app.get("/futures/{futures_code}", summary="获取指定期货详细信息 / Get specific futures detailed information")
async def get_futures_info(
    futures_code: str,
    refresh: bool = Query(False, description="是否强制刷新数据 / Whether to force refresh data"),
    db: Session = Depends(get_db)
):
    """
    获取指定期货的详细信息
    Get detailed information for a specific futures contract
    
    - **futures_code**: 期货代码，如 cu2410, al2410, IF2410 等 / Futures code, e.g., cu2410, al2410, IF2410
    - **refresh**: 是否强制从akshare刷新数据 / Whether to force refresh from akshare
    """
    try:
        # 将期货代码转换为小写 / Convert futures code to lowercase
        futures_code = futures_code.lower()
        
        # 检查数据库中是否有缓存数据 / Check if there's cached data in database
        cached_futures = db.query(ChineseFutures).filter(ChineseFutures.futures_code == futures_code).first()
        
        # 判断是否需要刷新数据 / Determine if data refresh is needed
        need_refresh = (
            refresh or 
            cached_futures is None or 
            (datetime.utcnow() - cached_futures.last_updated).total_seconds() > Config.FUTURES_DATA_CACHE_MINUTES * 60
        )
        
        if need_refresh:
            # 从akshare获取最新数据 / Get latest data from akshare
            futures_data = akshare_service.get_chinese_futures_info(futures_code)
            
            if futures_data is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"期货代码 {futures_code} 不存在或获取数据失败 / Futures code {futures_code} not found or failed to fetch data"
                )
            
            # 更新或创建数据库记录 / Update or create database record
            if cached_futures:
                # 更新现有记录 / Update existing record
                for key, value in futures_data.items():
                    if hasattr(cached_futures, key):
                        setattr(cached_futures, key, value)
                cached_futures.last_updated = datetime.utcnow()
            else:
                # 创建新记录 / Create new record
                cached_futures = ChineseFutures(**futures_data)
                db.add(cached_futures)
            
            db.commit()
            
            # 验证数据库操作 / Verify database operation
            db.refresh(cached_futures)
            verification_query = db.query(ChineseFutures).filter(ChineseFutures.futures_code == futures_code).first()
            if verification_query is None:
                logger.error(f"数据库验证失败：期货 {futures_code} 未找到 / Database verification failed: Futures {futures_code} not found")
                raise HTTPException(status_code=500, detail="数据库操作验证失败 / Database operation verification failed")
        
        # 返回期货信息 / Return futures information
        return {
            "futures_code": cached_futures.futures_code,
            "futures_name": cached_futures.futures_name,
            "contract_month": cached_futures.contract_month,
            "underlying_asset": cached_futures.underlying_asset,
            "current_price": cached_futures.current_price,
            "price_change": cached_futures.price_change,
            "price_change_pct": cached_futures.price_change_pct,
            "open_price": cached_futures.open_price,
            "close_price": cached_futures.close_price,
            "high_price": cached_futures.high_price,
            "low_price": cached_futures.low_price,
            "settlement_price": cached_futures.settlement_price,
            "volume": cached_futures.volume,
            "open_interest": cached_futures.open_interest,
            "contract_size": cached_futures.contract_size,
            "tick_size": cached_futures.tick_size,
            "exchange": cached_futures.exchange,
            "trading_unit": cached_futures.trading_unit,
            "delivery_month": cached_futures.delivery_month,
            "is_active": cached_futures.is_active,
            "last_updated": cached_futures.last_updated.isoformat(),
            "created_at": cached_futures.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取期货信息失败 / Failed to get futures info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/futures", summary="获取期货列表 / Get futures list")
async def get_futures_list(
    page: int = Query(1, ge=1, description="页码 / Page number"),
    limit: int = Query(20, ge=1, le=100, description="每页数量 / Items per page"),
    search: Optional[str] = Query(None, description="搜索关键词（期货代码或名称）/ Search keyword (futures code or name)"),
    exchange: Optional[str] = Query(None, description="交易所筛选 / Exchange filter"),
    underlying_asset: Optional[str] = Query(None, description="标的资产筛选 / Underlying asset filter"),
    sort_by: str = Query("futures_code", description="排序字段 / Sort field"),
    sort_order: str = Query("asc", description="排序顺序：asc或desc / Sort order: asc or desc"),
    active_only: bool = Query(True, description="只显示活跃合约 / Show active contracts only"),
    db: Session = Depends(get_db)
):
    """
    获取期货列表，支持分页、搜索和排序
    Get futures list with pagination, search and sorting support
    """
    try:
        # 构建查询条件 / Build query conditions
        query = db.query(ChineseFutures)
        
        if active_only:
            query = query.filter(ChineseFutures.is_active == True)
        
        if search:
            search_condition = or_(
                ChineseFutures.futures_code.contains(search.lower()),
                ChineseFutures.futures_name.contains(search),
                ChineseFutures.underlying_asset.contains(search)
            )
            query = query.filter(search_condition)
        
        if exchange:
            query = query.filter(ChineseFutures.exchange == exchange.upper())
        
        if underlying_asset:
            query = query.filter(ChineseFutures.underlying_asset.contains(underlying_asset))
        
        # 排序 / Sorting
        if hasattr(ChineseFutures, sort_by):
            sort_column = getattr(ChineseFutures, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        # 计算总数 / Calculate total count
        total_count = query.count()
        
        # 分页 / Pagination
        offset = (page - 1) * limit
        futures = query.offset(offset).limit(limit).all()
        
        # 格式化返回数据 / Format return data
        futures_data = []
        for future in futures:
            futures_data.append({
                "futures_code": future.futures_code,
                "futures_name": future.futures_name,
                "underlying_asset": future.underlying_asset,
                "current_price": future.current_price,
                "price_change": future.price_change,
                "price_change_pct": future.price_change_pct,
                "volume": future.volume,
                "open_interest": future.open_interest,
                "exchange": future.exchange,
                "contract_month": future.contract_month,
                "last_updated": future.last_updated.isoformat() if future.last_updated else None
            })
        
        return {
            "futures": futures_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"获取期货列表失败 / Failed to get futures list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.post("/futures/{futures_code}/refresh", summary="刷新指定期货数据 / Refresh specific futures data")
async def refresh_futures_data(futures_code: str, db: Session = Depends(get_db)):
    """
    强制刷新指定期货的数据
    Force refresh data for a specific futures contract
    """
    try:
        futures_code = futures_code.lower()
        
        # 从akshare获取最新数据 / Get latest data from akshare
        futures_data = akshare_service.get_chinese_futures_info(futures_code)
        
        if futures_data is None:
            raise HTTPException(
                status_code=404, 
                detail=f"期货代码 {futures_code} 不存在或获取数据失败 / Futures code {futures_code} not found or failed to fetch data"
            )
        
        # 查找现有记录 / Find existing record
        existing_futures = db.query(ChineseFutures).filter(ChineseFutures.futures_code == futures_code).first()
        
        if existing_futures:
            # 更新现有记录 / Update existing record
            for key, value in futures_data.items():
                if hasattr(existing_futures, key):
                    setattr(existing_futures, key, value)
            existing_futures.last_updated = datetime.utcnow()
        else:
            # 创建新记录 / Create new record
            existing_futures = ChineseFutures(**futures_data)
            db.add(existing_futures)
        
        db.commit()
        
        # 验证数据库操作 / Verify database operation
        db.refresh(existing_futures)
        verification_query = db.query(ChineseFutures).filter(ChineseFutures.futures_code == futures_code).first()
        if verification_query is None:
            logger.error(f"数据库验证失败：期货 {futures_code} 刷新后未找到 / Database verification failed: Futures {futures_code} not found after refresh")
            raise HTTPException(status_code=500, detail="数据库操作验证失败 / Database operation verification failed")
        
        return {
            "message": f"期货 {futures_code} 数据刷新成功 / Futures {futures_code} data refreshed successfully",
            "futures_code": futures_code,
            "last_updated": existing_futures.last_updated.isoformat(),
            "current_price": existing_futures.current_price
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新期货数据失败 / Failed to refresh futures data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.delete("/futures/{futures_code}", summary="删除指定期货数据 / Delete specific futures data")
async def delete_futures_data(futures_code: str, db: Session = Depends(get_db)):
    """
    删除指定期货的数据（软删除，设置为不活跃）
    Delete data for a specific futures contract (soft delete, set as inactive)
    """
    try:
        futures_code = futures_code.lower()
        
        # 查找期货记录 / Find futures record
        futures = db.query(ChineseFutures).filter(ChineseFutures.futures_code == futures_code).first()
        
        if not futures:
            raise HTTPException(
                status_code=404, 
                detail=f"期货代码 {futures_code} 不存在 / Futures code {futures_code} not found"
            )
        
        # 软删除：设置为不活跃 / Soft delete: set as inactive
        futures.is_active = False
        futures.last_updated = datetime.utcnow()
        
        db.commit()
        
        # 验证数据库操作 / Verify database operation
        db.refresh(futures)
        verification_query = db.query(ChineseFutures).filter(
            and_(ChineseFutures.futures_code == futures_code, ChineseFutures.is_active == False)
        ).first()
        if verification_query is None:
            logger.error(f"数据库验证失败：期货 {futures_code} 删除后验证失败 / Database verification failed: Futures {futures_code} deletion verification failed")
            raise HTTPException(status_code=500, detail="数据库操作验证失败 / Database operation verification failed")
        
        return {
            "message": f"期货 {futures_code} 数据已删除 / Futures {futures_code} data deleted",
            "futures_code": futures_code,
            "deleted_at": futures.last_updated.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除期货数据失败 / Failed to delete futures data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/exchanges", summary="获取期货交易所列表 / Get futures exchange list")
async def get_exchanges(db: Session = Depends(get_db)):
    """
    获取所有期货交易所列表
    Get all futures exchange list
    """
    try:
        exchanges_query = db.query(ChineseFutures.exchange).filter(
            and_(ChineseFutures.exchange.isnot(None), ChineseFutures.exchange != "", ChineseFutures.is_active == True)
        ).distinct().all()
        
        exchanges = [exchange[0] for exchange in exchanges_query if exchange[0]]
        
        # 交易所中英文对照 / Exchange Chinese-English mapping
        exchange_mappings = {
            'SHFE': '上海期货交易所',
            'DCE': '大连商品交易所', 
            'CZCE': '郑州商品交易所',
            'CFFEX': '中国金融期货交易所',
            'INE': '上海国际能源交易中心'
        }
        
        exchange_info = []
        for exchange in sorted(exchanges):
            exchange_info.append({
                "code": exchange,
                "name_cn": exchange_mappings.get(exchange, exchange),
                "name_en": exchange
            })
        
        return {
            "exchanges": exchange_info,
            "total_count": len(exchanges)
        }
        
    except Exception as e:
        logger.error(f"获取交易所列表失败 / Failed to get exchanges: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/assets", summary="获取标的资产列表 / Get underlying assets list")
async def get_underlying_assets(db: Session = Depends(get_db)):
    """
    获取所有标的资产列表
    Get all underlying assets list
    """
    try:
        assets_query = db.query(ChineseFutures.underlying_asset).filter(
            and_(ChineseFutures.underlying_asset.isnot(None), ChineseFutures.underlying_asset != "", ChineseFutures.is_active == True)
        ).distinct().all()
        
        assets = [asset[0] for asset in assets_query if asset[0]]
        
        return {
            "underlying_assets": sorted(assets),
            "total_count": len(assets)
        }
        
    except Exception as e:
        logger.error(f"获取标的资产列表失败 / Failed to get underlying assets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/contracts/{underlying_asset}", summary="获取指定标的资产的所有合约 / Get all contracts for specific underlying asset")
async def get_contracts_by_asset(
    underlying_asset: str,
    active_only: bool = Query(True, description="只显示活跃合约 / Show active contracts only"),
    db: Session = Depends(get_db)
):
    """
    获取指定标的资产的所有合约
    Get all contracts for a specific underlying asset
    """
    try:
        query = db.query(ChineseFutures).filter(ChineseFutures.underlying_asset.contains(underlying_asset))
        
        if active_only:
            query = query.filter(ChineseFutures.is_active == True)
        
        contracts = query.order_by(ChineseFutures.contract_month.asc()).all()
        
        contracts_data = []
        for contract in contracts:
            contracts_data.append({
                "futures_code": contract.futures_code,
                "futures_name": contract.futures_name,
                "contract_month": contract.contract_month,
                "current_price": contract.current_price,
                "price_change_pct": contract.price_change_pct,
                "volume": contract.volume,
                "open_interest": contract.open_interest,
                "exchange": contract.exchange,
                "last_updated": contract.last_updated.isoformat() if contract.last_updated else None
            })
        
        return {
            "underlying_asset": underlying_asset,
            "contracts": contracts_data,
            "total_count": len(contracts_data)
        }
        
    except Exception as e:
        logger.error(f"获取合约列表失败 / Failed to get contracts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/stats", summary="获取期货统计信息 / Get futures statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """
    获取期货服务统计信息
    Get futures service statistics
    """
    try:
        # 统计活跃合约数量 / Count active contracts
        active_contracts_count = db.query(ChineseFutures).filter(ChineseFutures.is_active == True).count()
        
        # 统计总合约数量 / Count total contracts
        total_contracts_count = db.query(ChineseFutures).count()
        
        # 统计今日API调用次数 / Count today's API calls
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_api_calls = db.query(APILog).filter(
            and_(
                APILog.service_type == "futures",
                APILog.created_at >= today_start
            )
        ).count()
        
        # 统计各交易所合约数量 / Count contracts by exchange
        from sqlalchemy import func
        exchange_stats = db.query(
            ChineseFutures.exchange,
            func.count(ChineseFutures.futures_code).label('count')
        ).filter(ChineseFutures.is_active == True).group_by(ChineseFutures.exchange).all()
        
        exchange_distribution = {exchange: count for exchange, count in exchange_stats if exchange}
        
        # 统计各标的资产合约数量 / Count contracts by underlying asset
        asset_stats = db.query(
            ChineseFutures.underlying_asset,
            func.count(ChineseFutures.futures_code).label('count')
        ).filter(ChineseFutures.is_active == True).group_by(ChineseFutures.underlying_asset).all()
        
        asset_distribution = {asset: count for asset, count in asset_stats if asset}
        
        # 获取最新更新的合约 / Get latest updated contracts
        latest_updated_futures = db.query(ChineseFutures).filter(
            ChineseFutures.is_active == True
        ).order_by(ChineseFutures.last_updated.desc()).limit(5).all()
        
        latest_futures_data = []
        for futures in latest_updated_futures:
            latest_futures_data.append({
                "futures_code": futures.futures_code,
                "futures_name": futures.futures_name,
                "underlying_asset": futures.underlying_asset,
                "current_price": futures.current_price,
                "price_change_pct": futures.price_change_pct,
                "exchange": futures.exchange,
                "last_updated": futures.last_updated.isoformat()
            })
        
        return {
            "service": "Chinese Futures Service",
            "statistics": {
                "active_contracts_count": active_contracts_count,
                "total_contracts_count": total_contracts_count,
                "today_api_calls": today_api_calls,
                "exchange_distribution": exchange_distribution,
                "asset_distribution": asset_distribution,
                "latest_updated_contracts": latest_futures_data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败 / Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "futures_api:app", 
        host="0.0.0.0", 
        port=Config.FUTURES_PORT,
        reload=True
    )