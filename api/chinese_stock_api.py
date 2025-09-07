# -*- coding: utf-8 -*-
"""
中国股票服务API
Chinese Stock Service API - Port 3003
"""
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import time

from database import get_db, ChineseStock, APILog, init_database, test_database_connection
from akshare_service import AkshareService
from config import Config

# 配置日志 / Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=Config.API_TITLE_CN,
    version=Config.API_VERSION,
    description="中国股票信息服务API，提供实时股票数据、公司信息和财务指标 / Chinese stock information service API providing real-time stock data, company information and financial indicators"
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

# 在应用末尾添加新的API端点
@app.get("/api/financial-abstract/{stock_code}", summary="获取财务摘要数据")
async def get_financial_abstract(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    获取股票财务摘要数据 / Get stock financial abstract data
    包含营业收入、净利润等关键财务指标的历史数据
    """
    try:
        # 调用akshare获取财务摘要数据
        financial_data = akshare_service.get_financial_abstract(stock_code)
        
        if financial_data is None or len(financial_data) == 0:
            raise HTTPException(status_code=404, detail=f"Stock {stock_code} financial data not found")
        
        # 转换为适合API返回的格式
        result = {
            "stock_code": stock_code,
            "data_source": "akshare_financial_abstract", 
            "update_time": datetime.now().isoformat(),
            "financial_indicators": financial_data.fillna('').to_dict('records')
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting financial abstract for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/comprehensive-financial/{stock_code}", summary="获取全面财务指标数据")
async def get_comprehensive_financial(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    获取股票全面财务指标数据 / Get comprehensive financial indicators data
    包含财务报表、财务比率、盈利能力、运营效率、流动性、杠杆和成长性指标的完整分析
    """
    try:
        # 调用akshare获取全面财务指标数据
        comprehensive_data = akshare_service.get_comprehensive_financial_indicators(stock_code)
        
        if comprehensive_data is None:
            raise HTTPException(status_code=404, detail=f"Comprehensive financial data for stock {stock_code} not found")
        
        return comprehensive_data
        
    except Exception as e:
        logger.error(f"Error getting comprehensive financial data for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/stock-info/{stock_code}", summary="获取股票基本信息")
async def get_stock_info(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    获取股票基本信息 / Get stock basic information
    包含股票代码、名称、总股本、流通股本等基本信息
    """
    try:
        # 调用akshare获取股票基本信息
        stock_info = akshare_service.get_stock_basic_info(stock_code)
        
        if stock_info is None:
            raise HTTPException(status_code=404, detail=f"Stock {stock_code} info not found")
        
        result = {
            "stock_code": stock_code,
            "data_source": "akshare_individual_info",
            "update_time": datetime.now().isoformat(),
            "stock_info": stock_info
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting stock info for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/comprehensive-data/{stock_code}", summary="获取股票综合数据")
async def get_comprehensive_data(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    获取股票综合数据 / Get comprehensive stock data
    包含财务指标、技术指标、基本信息的完整数据集
    """
    try:
        # 调用akshare获取综合数据
        comprehensive_data = akshare_service.get_comprehensive_financial_data(stock_code)
        
        if comprehensive_data is None:
            raise HTTPException(status_code=404, detail=f"Comprehensive data for stock {stock_code} not found")
        
        return comprehensive_data
        
    except Exception as e:
        logger.error(f"Error getting comprehensive data for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/technical-indicators/{stock_code}", summary="获取股票技术指标")
async def get_technical_indicators(
    stock_code: str,
    days: int = Query(60, ge=20, le=250, description="历史数据天数"),
    db: Session = Depends(get_db)
):
    """
    获取股票技术指标 / Get stock technical indicators
    包含移动平均线、成交量指标、价格波动率等技术分析数据
    """
    try:
        # 获取历史数据
        historical_data = akshare_service._get_historical_data(stock_code, days=days)
        if historical_data is None:
            raise HTTPException(status_code=404, detail=f"Historical data for stock {stock_code} not found")
        
        # 计算技术指标
        technical_indicators = akshare_service._calculate_technical_indicators(historical_data)
        
        result = {
            "stock_code": stock_code,
            "data_source": "akshare_historical_data",
            "update_time": datetime.now().isoformat(),
            "analysis_period_days": days,
            "technical_indicators": technical_indicators,
            "data_points_analyzed": len(historical_data)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting technical indicators for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/industry-analysis/{stock_code}", summary="获取股票行业分析")
async def get_industry_analysis_data(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    获取股票行业分析数据 / Get stock industry analysis data
    包含行业概况、市场地位分析等
    """
    try:
        # 调用akshare获取行业分析数据
        industry_analysis = akshare_service.get_industry_analysis(stock_code)
        
        if industry_analysis is None:
            raise HTTPException(status_code=404, detail=f"Industry analysis for stock {stock_code} not found")
        
        return industry_analysis
        
    except Exception as e:
        logger.error(f"Error getting industry analysis for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/historical-data/{stock_code}", summary="获取股票历史数据")
async def get_historical_data(
    stock_code: str,
    period: str = Query("daily", description="数据周期: daily, weekly, monthly"),
    days: int = Query(30, ge=1, le=1000, description="获取天数"),
    db: Session = Depends(get_db)
):
    """
    获取股票历史数据 / Get stock historical data
    包含开高低收、成交量等历史交易数据
    """
    try:
        # 获取历史数据
        historical_data = akshare_service._get_historical_data(stock_code, period=period, days=days)
        
        if historical_data is None or historical_data.empty:
            raise HTTPException(status_code=404, detail=f"Historical data for stock {stock_code} not found")
        
        # 转换为API友好的格式
        data_records = []
        for _, row in historical_data.iterrows():
            data_records.append({
                "date": row["日期"],
                "open": float(row["开盘"]),
                "close": float(row["收盘"]),
                "high": float(row["最高"]),
                "low": float(row["最低"]),
                "volume": int(row["成交量"]),
                "amount": float(row["成交额"]),
                "change_pct": float(row["涨跌幅"]),
                "change_amount": float(row["涨跌额"]),
                "turnover_rate": float(row["换手率"])
            })
        
        result = {
            "stock_code": stock_code,
            "data_source": "akshare_historical_data",
            "update_time": datetime.now().isoformat(),
            "period": period,
            "total_records": len(data_records),
            "data_range": {
                "start_date": data_records[0]["date"] if data_records else None,
                "end_date": data_records[-1]["date"] if data_records else None
            },
            "historical_data": data_records
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting historical data for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/fund-flow/{stock_code}", summary="获取资金流向数据")
async def get_fund_flow(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    获取资金流向数据 / Get fund flow data
    包含主力资金、大单、中单、小单的净流入数据和统计分析
    """
    try:
        # 调用akshare获取资金流向数据
        fund_flow_data = akshare_service.get_fund_flow_data(stock_code)
        
        if fund_flow_data is None:
            raise HTTPException(status_code=404, detail=f"Fund flow data for stock {stock_code} not found")
        
        return fund_flow_data
        
    except Exception as e:
        logger.error(f"Error getting fund flow data for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/news-research/{stock_code}", summary="获取新闻和研报数据")
async def get_news_research(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    获取新闻和研报数据 / Get news and research data
    包含最新的股票相关新闻和券商研究报告
    """
    try:
        # 调用akshare获取新闻研报数据
        news_research_data = akshare_service.get_news_and_research_data(stock_code)
        
        if news_research_data is None:
            raise HTTPException(status_code=404, detail=f"News and research data for stock {stock_code} not found")
        
        return news_research_data
        
    except Exception as e:
        logger.error(f"Error getting news research data for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/minute-data/{stock_code}", summary="获取分钟级数据")
async def get_minute_data(
    stock_code: str,
    period: str = Query("5", description="分钟周期: 1, 5, 15, 30, 60"),
    db: Session = Depends(get_db)
):
    """
    获取分钟级数据 / Get minute-level data
    包含今日分钟级价格数据、成交量和交易模式分析
    """
    try:
        # 验证period参数
        valid_periods = ['1', '5', '15', '30', '60']
        if period not in valid_periods:
            raise HTTPException(status_code=400, detail=f"Invalid period. Must be one of {valid_periods}")
        
        # 调用akshare获取分钟数据
        minute_data = akshare_service.get_minute_data(stock_code, period)
        
        if minute_data is None:
            raise HTTPException(status_code=404, detail=f"Minute data for stock {stock_code} not found")
        
        return minute_data
        
    except Exception as e:
        logger.error(f"Error getting minute data for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/comprehensive-market/{stock_code}", summary="获取综合市场数据")
async def get_comprehensive_market(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    获取综合市场数据 / Get comprehensive market data
    一次性获取资金流向、新闻研报、分钟数据等完整市场信息
    """
    try:
        # 调用akshare获取综合市场数据
        comprehensive_data = akshare_service.get_comprehensive_market_data(stock_code)
        
        if comprehensive_data is None:
            raise HTTPException(status_code=404, detail=f"Comprehensive market data for stock {stock_code} not found")
        
        return comprehensive_data
        
    except Exception as e:
        logger.error(f"Error getting comprehensive market data for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/advanced-technical/{stock_code}", summary="获取高级技术指标")
async def get_advanced_technical(
    stock_code: str,
    days: int = Query(100, ge=30, le=500, description="历史数据天数"),
    db: Session = Depends(get_db)
):
    """
    获取高级技术指标 / Get advanced technical indicators
    包含RSI、MACD、KDJ、布林带、威廉指标、CCI等专业技术分析指标
    """
    try:
        # 获取历史数据
        historical_data = akshare_service._get_historical_data(stock_code, days=days)
        if historical_data is None:
            raise HTTPException(status_code=404, detail=f"Historical data for stock {stock_code} not found")
        
        # 计算高级技术指标
        technical_indicators = akshare_service._calculate_technical_indicators(historical_data)
        
        # 提取高级指标
        advanced_indicators = {
            key: value for key, value in technical_indicators.items() 
            if key in ['rsi_14', 'macd', 'kdj', 'bollinger_bands', 'williams_r', 'cci_20', 'atr_14', 'support_resistance']
        }
        
        result = {
            "stock_code": stock_code,
            "data_source": "akshare_advanced_technical",
            "update_time": datetime.now().isoformat(),
            "analysis_period_days": days,
            "advanced_indicators": advanced_indicators,
            "data_points_analyzed": len(historical_data),
            "indicator_interpretation": {
                "rsi_signal": "overbought" if advanced_indicators.get('rsi_14', 50) > 70 else "oversold" if advanced_indicators.get('rsi_14', 50) < 30 else "neutral",
                "bollinger_position": _analyze_bollinger_position(technical_indicators.get('current_price', 0), advanced_indicators.get('bollinger_bands', {})),
                "kdj_signal": _analyze_kdj_signal(advanced_indicators.get('kdj', {})),
                "macd_trend": _analyze_macd_trend(advanced_indicators.get('macd', {}))
            }
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting advanced technical indicators for {stock_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def _analyze_bollinger_position(current_price: float, bollinger: dict) -> str:
    """分析布林带位置"""
    if not bollinger or not current_price:
        return "unknown"
    
    upper = bollinger.get('upper')
    lower = bollinger.get('lower')
    
    if upper and lower:
        if current_price > upper:
            return "above_upper_band"
        elif current_price < lower:
            return "below_lower_band"
        else:
            return "within_bands"
    return "unknown"

def _analyze_kdj_signal(kdj: dict) -> str:
    """分析KDJ信号"""
    if not kdj:
        return "unknown"
    
    k = kdj.get('K', 50)
    d = kdj.get('D', 50)
    
    if k > 80 and d > 80:
        return "overbought"
    elif k < 20 and d < 20:
        return "oversold"
    elif k > d:
        return "bullish"
    elif k < d:
        return "bearish"
    else:
        return "neutral"

def _analyze_macd_trend(macd: dict) -> str:
    """分析MACD趋势"""
    if not macd:
        return "unknown"
    
    macd_line = macd.get('macd', 0)
    signal_line = macd.get('signal', 0)
    histogram = macd.get('histogram', 0)
    
    if macd_line > signal_line and histogram > 0:
        return "bullish_strong"
    elif macd_line > signal_line and histogram < 0:
        return "bullish_weak"
    elif macd_line < signal_line and histogram < 0:
        return "bearish_strong"
    elif macd_line < signal_line and histogram > 0:
        return "bearish_weak"
    else:
        return "neutral"

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
            service_type="chinese_stock",
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
    logger.info("中国股票服务API启动中 / Chinese Stock Service API starting...")
    
    # 测试数据库连接 / Test database connection
    if not test_database_connection():
        logger.error("数据库连接失败，服务无法启动 / Database connection failed, service cannot start")
        raise Exception("Database connection failed")
    
    # 初始化数据库表 / Initialize database tables
    if not init_database():
        logger.error("数据库初始化失败 / Database initialization failed")
        raise Exception("Database initialization failed")
    
    logger.info(f"中国股票服务API已在端口{Config.CHINESE_STOCK_PORT}启动 / Chinese Stock Service API started on port {Config.CHINESE_STOCK_PORT}")

@app.get("/", summary="服务状态检查 / Service health check")
async def root():
    """服务状态检查端点 / Service health check endpoint"""
    return {
        "service": "Chinese Stock Service",
        "status": "running",
        "version": Config.API_VERSION,
        "server_ip": Config.SERVER_IP,
        "port": Config.CHINESE_STOCK_PORT,
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

@app.get("/stocks/{stock_code}", summary="获取指定股票详细信息 / Get specific stock detailed information")
async def get_stock_info(
    stock_code: str,
    refresh: bool = Query(False, description="是否强制刷新数据 / Whether to force refresh data"),
    db: Session = Depends(get_db)
):
    """
    获取指定股票的详细信息
    Get detailed information for a specific stock
    
    - **stock_code**: 股票代码，如 000001, 600036 等 / Stock code, e.g., 000001, 600036
    - **refresh**: 是否强制从akshare刷新数据 / Whether to force refresh from akshare
    """
    try:
        # 检查数据库中是否有缓存数据 / Check if there's cached data in database
        cached_stock = db.query(ChineseStock).filter(ChineseStock.stock_code == stock_code).first()
        
        # 判断是否需要刷新数据 / Determine if data refresh is needed
        need_refresh = (
            refresh or 
            cached_stock is None or 
            (datetime.utcnow() - cached_stock.last_updated).total_seconds() > Config.STOCK_DATA_CACHE_MINUTES * 60
        )
        
        if need_refresh:
            # 从akshare获取最新数据 / Get latest data from akshare
            stock_data = akshare_service.get_chinese_stock_info(stock_code)
            
            if stock_data is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"股票代码 {stock_code} 不存在或获取数据失败 / Stock code {stock_code} not found or failed to fetch data"
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
                cached_stock = ChineseStock(**stock_data)
                db.add(cached_stock)
            
            db.commit()
            
            # 验证数据库操作 / Verify database operation
            db.refresh(cached_stock)
            verification_query = db.query(ChineseStock).filter(ChineseStock.stock_code == stock_code).first()
            if verification_query is None:
                logger.error(f"数据库验证失败：股票 {stock_code} 未找到 / Database verification failed: Stock {stock_code} not found")
                raise HTTPException(status_code=500, detail="数据库操作验证失败 / Database operation verification failed")
        
        # 返回股票信息 / Return stock information
        return {
            "stock_code": cached_stock.stock_code,
            "stock_name_cn": cached_stock.stock_name_cn,
            "stock_name_en": cached_stock.stock_name_en,
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
            "is_active": cached_stock.is_active,
            "last_updated": cached_stock.last_updated.isoformat(),
            "created_at": cached_stock.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票信息失败 / Failed to get stock info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/stocks", summary="获取股票列表 / Get stock list")
async def get_stocks_list(
    page: int = Query(1, ge=1, description="页码 / Page number"),
    limit: int = Query(20, ge=1, le=100, description="每页数量 / Items per page"),
    search: Optional[str] = Query(None, description="搜索关键词（股票代码或名称）/ Search keyword (stock code or name)"),
    sort_by: str = Query("stock_code", description="排序字段 / Sort field"),
    sort_order: str = Query("asc", description="排序顺序：asc或desc / Sort order: asc or desc"),
    active_only: bool = Query(True, description="只显示活跃股票 / Show active stocks only"),
    db: Session = Depends(get_db)
):
    """
    获取股票列表，支持分页、搜索和排序
    Get stock list with pagination, search and sorting support
    """
    try:
        # 构建查询条件 / Build query conditions
        query = db.query(ChineseStock)
        
        if active_only:
            query = query.filter(ChineseStock.is_active == True)
        
        if search:
            search_condition = or_(
                ChineseStock.stock_code.contains(search),
                ChineseStock.stock_name_cn.contains(search),
                ChineseStock.stock_name_en.contains(search)
            )
            query = query.filter(search_condition)
        
        # 排序 / Sorting
        if hasattr(ChineseStock, sort_by):
            sort_column = getattr(ChineseStock, sort_by)
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
                "stock_code": stock.stock_code,
                "stock_name_cn": stock.stock_name_cn,
                "stock_name_en": stock.stock_name_en,
                "current_price": stock.current_price,
                "price_change": stock.price_change,
                "price_change_pct": stock.price_change_pct,
                "market_cap": stock.market_cap,
                "volume": stock.volume,
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
        logger.error(f"获取股票列表失败 / Failed to get stock list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.post("/stocks/{stock_code}/refresh", summary="刷新指定股票数据 / Refresh specific stock data")
async def refresh_stock_data(stock_code: str, db: Session = Depends(get_db)):
    """
    强制刷新指定股票的数据
    Force refresh data for a specific stock
    """
    try:
        # 从akshare获取最新数据 / Get latest data from akshare
        stock_data = akshare_service.get_chinese_stock_info(stock_code)
        
        if stock_data is None:
            raise HTTPException(
                status_code=404, 
                detail=f"股票代码 {stock_code} 不存在或获取数据失败 / Stock code {stock_code} not found or failed to fetch data"
            )
        
        # 查找现有记录 / Find existing record
        existing_stock = db.query(ChineseStock).filter(ChineseStock.stock_code == stock_code).first()
        
        if existing_stock:
            # 更新现有记录 / Update existing record
            for key, value in stock_data.items():
                if hasattr(existing_stock, key):
                    setattr(existing_stock, key, value)
            existing_stock.last_updated = datetime.utcnow()
        else:
            # 创建新记录 / Create new record
            existing_stock = ChineseStock(**stock_data)
            db.add(existing_stock)
        
        db.commit()
        
        # 验证数据库操作 / Verify database operation
        db.refresh(existing_stock)
        verification_query = db.query(ChineseStock).filter(ChineseStock.stock_code == stock_code).first()
        if verification_query is None:
            logger.error(f"数据库验证失败：股票 {stock_code} 刷新后未找到 / Database verification failed: Stock {stock_code} not found after refresh")
            raise HTTPException(status_code=500, detail="数据库操作验证失败 / Database operation verification failed")
        
        return {
            "message": f"股票 {stock_code} 数据刷新成功 / Stock {stock_code} data refreshed successfully",
            "stock_code": stock_code,
            "last_updated": existing_stock.last_updated.isoformat(),
            "current_price": existing_stock.current_price
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新股票数据失败 / Failed to refresh stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.delete("/stocks/{stock_code}", summary="删除指定股票数据 / Delete specific stock data")
async def delete_stock_data(stock_code: str, db: Session = Depends(get_db)):
    """
    删除指定股票的数据（软删除，设置为不活跃）
    Delete data for a specific stock (soft delete, set as inactive)
    """
    try:
        # 查找股票记录 / Find stock record
        stock = db.query(ChineseStock).filter(ChineseStock.stock_code == stock_code).first()
        
        if not stock:
            raise HTTPException(
                status_code=404, 
                detail=f"股票代码 {stock_code} 不存在 / Stock code {stock_code} not found"
            )
        
        # 软删除：设置为不活跃 / Soft delete: set as inactive
        stock.is_active = False
        stock.last_updated = datetime.utcnow()
        
        db.commit()
        
        # 验证数据库操作 / Verify database operation
        db.refresh(stock)
        verification_query = db.query(ChineseStock).filter(
            and_(ChineseStock.stock_code == stock_code, ChineseStock.is_active == False)
        ).first()
        if verification_query is None:
            logger.error(f"数据库验证失败：股票 {stock_code} 删除后验证失败 / Database verification failed: Stock {stock_code} deletion verification failed")
            raise HTTPException(status_code=500, detail="数据库操作验证失败 / Database operation verification failed")
        
        return {
            "message": f"股票 {stock_code} 数据已删除 / Stock {stock_code} data deleted",
            "stock_code": stock_code,
            "deleted_at": stock.last_updated.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除股票数据失败 / Failed to delete stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 / Internal server error: {str(e)}")

@app.get("/stats", summary="获取股票统计信息 / Get stock statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """
    获取股票服务统计信息
    Get stock service statistics
    """
    try:
        # 统计活跃股票数量 / Count active stocks
        active_stocks_count = db.query(ChineseStock).filter(ChineseStock.is_active == True).count()
        
        # 统计总股票数量 / Count total stocks
        total_stocks_count = db.query(ChineseStock).count()
        
        # 统计今日API调用次数 / Count today's API calls
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_api_calls = db.query(APILog).filter(
            and_(
                APILog.service_type == "chinese_stock",
                APILog.created_at >= today_start
            )
        ).count()
        
        # 获取最新更新的股票 / Get latest updated stocks
        latest_updated_stocks = db.query(ChineseStock).filter(
            ChineseStock.is_active == True
        ).order_by(ChineseStock.last_updated.desc()).limit(5).all()
        
        latest_stocks_data = []
        for stock in latest_updated_stocks:
            latest_stocks_data.append({
                "stock_code": stock.stock_code,
                "stock_name_cn": stock.stock_name_cn,
                "current_price": stock.current_price,
                "price_change_pct": stock.price_change_pct,
                "last_updated": stock.last_updated.isoformat()
            })
        
        return {
            "service": "Chinese Stock Service",
            "statistics": {
                "active_stocks_count": active_stocks_count,
                "total_stocks_count": total_stocks_count,
                "today_api_calls": today_api_calls,
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
        "chinese_stock_api:app", 
        host="0.0.0.0", 
        port=Config.CHINESE_STOCK_PORT,
        reload=True
    )