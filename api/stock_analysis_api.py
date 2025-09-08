# -*- coding: utf-8 -*-
"""
全面股票分析API服务
Complete Stock Analysis API Service
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import akshare as ak
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from akshare_service import AkshareService

app = FastAPI(
    title="Stock Analysis API", 
    description="Complete stock analysis API service for n8n workflows",
    version="2.0.0",
    docs_url=None,  # 禁用默认docs，使用自定义版本
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    servers=[
        {"url": "http://35.77.54.203:3003", "description": "Production server"}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化akshare服务
akshare_service = AkshareService()

def _extract_financial_indicator(df, indicator_name):
    """从财务数据中提取指定指标的最新值"""
    try:
        indicator_row = df[df['指标'] == indicator_name]
        if len(indicator_row) > 0:
            # 获取最近的非空数据列
            for col in df.columns[2:]:  # 跳过'选项'和'指标'列
                if col.startswith('202'):  # 年份列
                    value = indicator_row.iloc[0][col]
                    if value and value != '':
                        try:
                            return float(value)
                        except:
                            return value
        return 0
    except:
        return 0

# ============ 原有的测试API端点 ============
@app.get("/api/financial-abstract/{stock_code}")
async def get_financial_abstract(stock_code: str):
    try:
        df = ak.stock_financial_abstract(symbol=stock_code)
        
        if df is None or len(df) == 0:
            return {"error": f"Stock {stock_code} financial data not found"}
        
        # 处理NaN值以避免JSON序列化错误
        df = df.fillna('')
        
        return {
            "stock_code": stock_code,
            "data_source": "akshare_financial_abstract",
            "update_time": datetime.now().isoformat(),
            "financial_indicators": df.to_dict("records")
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stock-info/{stock_code}")  
async def get_stock_info(stock_code: str):
    try:
        df = ak.stock_individual_info_em(symbol=stock_code)
        
        if df is None or len(df) == 0:
            return {"error": f"Stock {stock_code} info not found"}
        
        result = {}
        for _, row in df.iterrows():
            result[row["item"]] = row["value"]
        
        return {
            "stock_code": stock_code,
            "data_source": "akshare_individual_info",
            "update_time": datetime.now().isoformat(),
            "stock_info": result
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/k-line/{stock_code}")
async def get_k_line_data(stock_code: str, period: str = "daily", days: int = 30):
    try:
        # 计算开始和结束日期
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        df = ak.stock_zh_a_hist(
            symbol=stock_code, 
            period=period, 
            start_date=start_date, 
            end_date=end_date
        )
        
        if df is None or len(df) == 0:
            return {"error": f"Stock {stock_code} K-line data not found"}
        
        # 处理NaN值
        df = df.fillna('')
        
        return {
            "stock_code": stock_code,
            "period": period,
            "days_requested": days,
            "data_source": "akshare_k_line",
            "update_time": datetime.now().isoformat(),
            "data_count": len(df),
            "k_line_data": df.to_dict("records")
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/technical-indicators/{stock_code}")
async def get_technical_indicators(stock_code: str):
    try:
        # 获取实时行情数据
        bid_ask_df = ak.stock_bid_ask_em(symbol=stock_code)
        
        # 获取市场概况数据
        market_df = ak.stock_zh_a_spot_em()
        target_stock = market_df[market_df['代码'] == stock_code]
        
        if bid_ask_df is None or len(bid_ask_df) == 0:
            return {"error": f"Stock {stock_code} bid-ask data not found"}
        
        # 提取实时行情数据
        bid_ask_data = {}
        for _, row in bid_ask_df.iterrows():
            bid_ask_data[row['item']] = row['value']
        
        # 提取技术面数据
        technical_data = {}
        if len(target_stock) > 0:
            stock_data = target_stock.iloc[0]
            technical_data = {
                "涨跌幅": stock_data.get("涨跌幅", 0),
                "换手率": stock_data.get("换手率", 0),
                "量比": stock_data.get("量比", 0),
                "市盈率": stock_data.get("市盈率-动态", 0),
                "市净率": stock_data.get("市净率", 0),
                "总市值": stock_data.get("总市值", 0),
                "流通市值": stock_data.get("流通市值", 0)
            }
        
        return {
            "stock_code": stock_code,
            "data_source": "akshare_technical",
            "update_time": datetime.now().isoformat(),
            "real_time_quotes": bid_ask_data,
            "technical_indicators": technical_data
        }
    except Exception as e:
        return {"error": str(e)}

# ============ workflow所需的API端点 ============

@app.get("/stocks/{stock_code}/analysis/fundamental")
async def get_fundamental_analysis(stock_code: str):
    """
    基本面分析API端点 / Fundamental analysis API endpoint
    对应workflow中的基本面分析HTTP请求
    """
    try:
        # 获取财务摘要数据
        financial_df = ak.stock_financial_abstract(symbol=stock_code)
        
        # 获取股票基本信息
        basic_df = ak.stock_individual_info_em(symbol=stock_code)
        
        if financial_df is None or len(financial_df) == 0:
            return {"error": f"无法获取股票 {stock_code} 的财务数据"}
        
        if basic_df is None or len(basic_df) == 0:
            return {"error": f"无法获取股票 {stock_code} 的基本信息"}
        
        # 处理NaN值
        financial_df = financial_df.fillna('')
        
        # 转换基本信息为字典
        basic_info = {}
        for _, row in basic_df.iterrows():
            basic_info[row['item']] = row['value']
        
        # 构建基本面分析数据
        result = {
            "stock_code": stock_code,
            "stock_name": basic_info.get("股票简称", ""),
            "analysis_type": "fundamental",
            "data_source": "akshare_comprehensive",
            "update_time": datetime.now().isoformat(),
            
            # 基本信息
            "basic_info": basic_info,
            
            # 财务指标
            "financial_indicators": financial_df.to_dict("records"),
            
            # 为AI分析准备的结构化数据
            "analysis_data": {
                "company_overview": {
                    "stock_code": stock_code,
                    "stock_name": basic_info.get("股票简称", ""),
                    "total_shares": basic_info.get("总股本", 0),
                    "circulating_shares": basic_info.get("流通股", 0),
                    "current_price": basic_info.get("最新", 0)
                },
                "financial_metrics": {
                    # 从财务摘要中提取关键指标
                    "revenue": _extract_financial_indicator(financial_df, "营业总收入"),
                    "net_profit": _extract_financial_indicator(financial_df, "归母净利润"), 
                    "total_assets": _extract_financial_indicator(financial_df, "总资产"),
                    "net_assets": _extract_financial_indicator(financial_df, "净资产"),
                    "eps": _extract_financial_indicator(financial_df, "每股收益")
                }
            }
        }
        
        return result
        
    except Exception as e:
        return {"error": f"基本面分析失败: {str(e)}"}

@app.get("/stocks/{stock_code}/analysis/technical")
async def get_technical_analysis(stock_code: str):
    """
    技术面分析API端点 / Technical analysis API endpoint
    对应workflow中的技术面分析HTTP请求
    """
    try:
        # 首先获取股票基本信息以确保股票名称一致性
        basic_df = ak.stock_individual_info_em(symbol=stock_code)
        stock_name = ""
        if basic_df is not None and len(basic_df) > 0:
            for _, row in basic_df.iterrows():
                if row['item'] == '股票简称':
                    stock_name = row['value']
                    break
        
        # 获取K线数据（最近30天）
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')
        
        kline_df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily", 
            start_date=start_date,
            end_date=end_date
        )
        
        # 获取实时行情数据
        realtime_df = ak.stock_bid_ask_em(symbol=stock_code)
        
        # 获取市场概况数据（这个调用可能会比较慢，容易出错）
        try:
            market_df = ak.stock_zh_a_spot_em()
            target_stock = market_df[market_df['代码'] == stock_code]
        except:
            target_stock = []
        
        if kline_df is None or len(kline_df) == 0:
            return {"error": f"无法获取股票 {stock_code} 的K线数据"}
        
        if realtime_df is None or len(realtime_df) == 0:
            return {"error": f"无法获取股票 {stock_code} 的实时数据"}
        
        # 处理NaN值
        kline_df = kline_df.fillna('')
        
        # 提取实时行情数据
        realtime_data = {}
        for _, row in realtime_df.iterrows():
            realtime_data[row['item']] = row['value']
        
        # 提取技术指标数据
        technical_data = {}
        if len(target_stock) > 0:
            stock_data = target_stock.iloc[0]
            technical_data = {
                "涨跌幅": stock_data.get("涨跌幅", 0),
                "换手率": stock_data.get("换手率", 0),
                "量比": stock_data.get("量比", 0),
                "市盈率": stock_data.get("市盈率-动态", 0),
                "市净率": stock_data.get("市净率", 0),
                "总市值": stock_data.get("总市值", 0)
            }
        else:
            # 从实时数据提取技术指标
            technical_data = {
                "涨跌幅": realtime_data.get("涨幅", 0),
                "换手率": 0,  # 实时数据中可能没有
                "量比": 0,    # 实时数据中可能没有
                "市盈率": 0,  # 需要从其他源获取
                "市净率": 0,  # 需要从其他源获取
                "总市值": 0   # 需要计算
            }
        
        # 构建技术分析数据 - 优先使用从基本信息获取的股票名称
        result = {
            "stock_code": stock_code,
            "stock_name": stock_name,  # 使用从基本信息获取的准确股票名称
            "analysis_type": "technical",
            "data_source": "akshare_technical",
            "update_time": datetime.now().isoformat(),
            
            # K线数据
            "k_line_data": kline_df.to_dict("records"),
            
            # 实时行情
            "real_time_data": realtime_data,
            
            # 技术指标
            "technical_indicators": technical_data,
            
            # 为AI分析准备的结构化数据
            "analysis_data": {
                "current_price": float(realtime_data.get("最新", 0)),
                "price_change": float(realtime_data.get("涨跌", 0)),
                "price_change_pct": float(realtime_data.get("涨幅", 0)),
                "volume": float(realtime_data.get("总手", 0)),
                "turnover_rate": float(technical_data.get("换手率", 0)),
                "pe_ratio": float(technical_data.get("市盈率", 0)),
                "pb_ratio": float(technical_data.get("市净率", 0)),
                "recent_high": float(kline_df['最高'].max()) if len(kline_df) > 0 else 0,
                "recent_low": float(kline_df['最低'].min()) if len(kline_df) > 0 else 0
            }
        }
        
        return result
        
    except Exception as e:
        return {"error": f"技术面分析失败: {str(e)}"}

# 消息面分析的占位符端点
@app.get("/stocks/{stock_code}/news/announcements")
async def get_company_announcements(stock_code: str):
    """
    公司公告API端点 / Company Announcements API
    由于akshare公告接口限制，提供基于财务报表的报告期信息
    """
    try:
        # 获取财务摘要数据作为公告信息的替代
        financial_df = ak.stock_financial_abstract(symbol=stock_code)
        
        if financial_df is None or len(financial_df) == 0:
            return {
                "stock_code": stock_code,
                "data_source": "akshare_financial_periods",
                "update_time": datetime.now().isoformat(),
                "announcements": [],
                "note": "暂无可用的财务报告期信息"
            }
        
        # 提取报告期信息
        date_columns = [col for col in financial_df.columns if col.isdigit() and len(col) == 8]
        date_columns = sorted(date_columns, reverse=True)[:4]  # 最近4个报告期
        
        announcements = []
        for period in date_columns:
            formatted_date = f"{period[:4]}-{period[4:6]}-{period[6:]}"
            quarter_info = {
                "report_date": formatted_date,
                "period": period,
                "type": "财务报告",
                "title": f"{period[:4]}年第{(int(period[4:6])//3)}季度财务报告",
                "summary": f"发布{formatted_date}财务报告数据",
                "status": "已发布"
            }
            announcements.append(quarter_info)
        
        return {
            "stock_code": stock_code,
            "data_source": "akshare_financial_periods",
            "update_time": datetime.now().isoformat(),
            "total_announcements": len(announcements),
            "announcements": announcements,
            "note": "基于财务报表期间的报告信息，非完整公告数据"
        }
        
    except Exception as e:
        return {"error": f"获取公司公告信息失败: {str(e)}"}

@app.get("/stocks/{stock_code}/news/shareholders") 
async def get_shareholder_changes(stock_code: str):
    """股东变动API端点"""
    return {
        "stock_code": stock_code,
        "data_source": "placeholder", 
        "update_time": datetime.now().isoformat(),
        "shareholder_changes": [],
        "note": "股东变动数据接口开发中，akshare相关接口响应缓慢"
    }

@app.get("/stocks/{stock_code}/news/dragon-tiger")
async def get_dragon_tiger_list(stock_code: str, days: int = 90):
    """
    龙虎榜API端点 / Dragon Tiger List API
    获取指定股票在指定天数内的龙虎榜记录
    """
    try:
        # 调用akshare服务获取龙虎榜数据
        dragon_tiger_data = akshare_service.get_dragon_tiger_data(stock_code, days)
        
        if dragon_tiger_data is None:
            return {"error": f"Stock {stock_code} dragon tiger data not found"}
        
        return dragon_tiger_data
        
    except Exception as e:
        return {"error": f"获取龙虎榜数据失败: {str(e)}"}

@app.get("/stocks/{stock_code}/news/industry")
async def get_industry_news(stock_code: str):
    """行业新闻API端点"""
    return {
        "stock_code": stock_code,
        "data_source": "placeholder",
        "update_time": datetime.now().isoformat(),
        "industry_news": [],
        "note": "行业新闻数据接口开发中"
    }

# 处理URL编码的openapi.json请求
from urllib.parse import unquote
from fastapi.responses import JSONResponse, HTMLResponse

@app.get("/http%3A//35.77.54.203%3A3003/openapi.json")
async def openapi_encoded():
    """处理浏览器URL编码的openapi.json请求"""
    return JSONResponse(app.openapi())

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义Swagger UI页面，解决URL编码问题"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>Stock Analysis API - Swagger UI</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script>
    const ui = SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
        layout: 'BaseLayout',
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
        oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })
    </script>
    </body>
    </html>
    """)

# 增强的全面财务指标端点
@app.get("/api/comprehensive-financial/{stock_code}")
async def get_comprehensive_financial_indicators(stock_code: str):
    """
    获取全面财务指标数据 - 包含更多财务报表指标
    Get comprehensive financial indicators with enhanced metrics
    """
    try:
        # 获取基础财务摘要数据
        financial_df = ak.stock_financial_abstract(symbol=stock_code)
        
        if financial_df is None or len(financial_df) == 0:
            return {"error": f"Stock {stock_code} financial data not found"}
        
        # 处理NaN值
        financial_df = financial_df.fillna('')
        
        # 获取最近4个季度的数据列
        date_columns = [col for col in financial_df.columns if col.isdigit() and len(col) == 8]
        date_columns = sorted(date_columns, reverse=True)[:4]  # 最近4个季度
        
        # 提取完整的财务指标数据
        comprehensive_indicators = {}
        
        # 按季度整理数据
        for i, period in enumerate(date_columns):
            quarter_data = {}
            for _, row in financial_df.iterrows():
                metric_name = row['指标']
                value = row[period]
                if value != '' and value != 0:
                    quarter_data[metric_name] = value
            
            if quarter_data:
                formatted_date = f"{period[:4]}-{period[4:6]}-{period[6:]}"
                quarter_name = f"Q{i+1}_{period[:4]}"
                comprehensive_indicators[quarter_name] = {
                    'date': formatted_date,
                    'period': period,
                    'metrics': quarter_data
                }
        
        # 计算增长率和财务比率
        analysis_summary = {}
        if len(comprehensive_indicators) >= 2:
            quarters = sorted(comprehensive_indicators.keys(), reverse=True)
            latest = comprehensive_indicators[quarters[0]]['metrics']
            previous = comprehensive_indicators[quarters[1]]['metrics']
            
            # 计算同比增长率
            growth_rates = {}
            key_metrics = ['归母净利润', '营业总收入', '营业成本', '净利润', '经营现金流量净额']
            
            for metric in key_metrics:
                if metric in latest and metric in previous:
                    current_val = float(latest[metric])
                    previous_val = float(previous[metric])
                    if previous_val != 0:
                        growth_rate = ((current_val - previous_val) / abs(previous_val)) * 100
                        growth_rates[f"{metric}_增长率"] = round(growth_rate, 2)
            
            analysis_summary['growth_rates'] = growth_rates
            
            # 财务比率分析
            if '归母净利润' in latest and '营业总收入' in latest:
                net_profit = float(latest.get('归母净利润', 0))
                revenue = float(latest.get('营业总收入', 0))
                if revenue > 0:
                    analysis_summary['net_profit_margin'] = round((net_profit / revenue) * 100, 2)
            
            # ROE和ROA分析
            if 'ROE' in latest:
                analysis_summary['roe_current'] = latest['ROE']
            if 'ROA' in latest:
                analysis_summary['roa_current'] = latest['ROA']
        
        # 统计可用的财务指标数量
        all_metrics = set()
        for quarter_data in comprehensive_indicators.values():
            all_metrics.update(quarter_data['metrics'].keys())
        
        result = {
            "stock_code": stock_code,
            "data_source": "akshare_comprehensive_financial",
            "update_time": datetime.now().isoformat(),
            "data_quality": {
                "total_quarters": len(comprehensive_indicators),
                "total_metrics": len(all_metrics),
                "available_metrics": sorted(list(all_metrics)),
                "latest_period": date_columns[0] if date_columns else None
            },
            "quarterly_data": comprehensive_indicators,
            "financial_analysis": analysis_summary,
            "comprehensive_metrics_count": len(all_metrics)
        }
        
        return result
        
    except Exception as e:
        return {"error": f"获取全面财务指标失败: {str(e)}"}

# 财务指标对比分析端点
@app.get("/api/financial-comparison/{stock_code}")
async def get_financial_comparison(stock_code: str, periods: int = 8):
    """
    财务指标趋势对比分析
    Financial indicators trend comparison analysis
    """
    try:
        financial_df = ak.stock_financial_abstract(symbol=stock_code)
        
        if financial_df is None or len(financial_df) == 0:
            return {"error": f"Stock {stock_code} financial data not found"}
        
        financial_df = financial_df.fillna('')
        
        # 获取指定期数的数据
        date_columns = [col for col in financial_df.columns if col.isdigit() and len(col) == 8]
        date_columns = sorted(date_columns, reverse=True)[:periods]
        
        # 重点关注的财务指标
        key_indicators = [
            '归母净利润', '营业总收入', '营业成本', '净利润', '扣非净利润',
            '股东权益合计(净资产)', '经营现金流量净额', '基本每股收益', 
            '每股净资产', '净资产收益率(ROE)', '总资产报酬率(ROA)',
            '毛利率', '销售净利率', '资产负债率'
        ]
        
        # 构建趋势数据
        trend_data = {}
        for indicator in key_indicators:
            indicator_row = financial_df[financial_df['指标'] == indicator]
            if len(indicator_row) > 0:
                trend_values = []
                for period in date_columns:
                    value = indicator_row.iloc[0][period]
                    if value != '' and value != 0:
                        trend_values.append({
                            'period': period,
                            'date': f"{period[:4]}-{period[4:6]}-{period[6:]}",
                            'value': float(value)
                        })
                
                if trend_values:
                    # 计算趋势统计
                    values = [item['value'] for item in trend_values]
                    trend_analysis = {
                        'trend_data': trend_values,
                        'max_value': max(values),
                        'min_value': min(values),
                        'average_value': round(sum(values) / len(values), 2),
                        'volatility': round((max(values) - min(values)) / max(values) * 100, 2) if max(values) > 0 else 0,
                        'recent_trend': 'increasing' if len(values) >= 2 and values[0] > values[1] else 'decreasing' if len(values) >= 2 else 'stable'
                    }
                    
                    trend_data[indicator] = trend_analysis
        
        result = {
            "stock_code": stock_code,
            "data_source": "akshare_financial_comparison",
            "update_time": datetime.now().isoformat(),
            "analysis_periods": periods,
            "trend_analysis": trend_data,
            "summary": {
                "analyzed_indicators": len(trend_data),
                "date_range": f"{date_columns[-1][:4]}-{date_columns[-1][4:6]} to {date_columns[0][:4]}-{date_columns[0][4:6]}" if date_columns else None
            }
        }
        
        return result
        
    except Exception as e:
        return {"error": f"财务对比分析失败: {str(e)}"}

# 资金流向数据端点
@app.get("/api/fund-flow/{stock_code}")
async def get_fund_flow_analysis(stock_code: str):
    """
    获取资金流向数据 / Get fund flow data
    包含主力资金、大单、中单、小单的净流入数据和统计分析
    """
    try:
        # 调用akshare服务获取资金流向数据
        fund_flow_data = akshare_service.get_fund_flow_data(stock_code)
        
        if fund_flow_data is None:
            return {"error": f"Stock {stock_code} fund flow data not found"}
        
        return fund_flow_data
        
    except Exception as e:
        return {"error": f"获取资金流向数据失败: {str(e)}"}

# 健康检查端点
@app.get("/")
async def root():
    return {
        "message": "股票分析API服务正常运行",
        "service": "comprehensive_stock_api", 
        "version": "1.0.0",
        "endpoints": {
            "fundamental": "/stocks/{stock_code}/analysis/fundamental",
            "technical": "/stocks/{stock_code}/analysis/technical", 
            "announcements": "/stocks/{stock_code}/news/announcements",
            "shareholders": "/stocks/{stock_code}/news/shareholders",
            "dragon_tiger": "/stocks/{stock_code}/news/dragon-tiger",
            "industry": "/stocks/{stock_code}/news/industry",
            "fund_flow": "/api/fund-flow/{stock_code}",
            "comprehensive_financial": "/api/comprehensive-financial/{stock_code}",
            "financial_comparison": "/api/financial-comparison/{stock_code}"
        },
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3003)