#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的股票分析API - 专门用于测试文档问题
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import akshare as ak
from datetime import datetime

# 创建最简单的FastAPI应用
app = FastAPI(
    title="Stock Analysis API",
    description="Stock analysis API for testing documentation",
    version="2.0.0"
)

# 添加CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Stock Analysis API is running", "timestamp": datetime.now()}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/test/{stock_code}")
async def test_endpoint(stock_code: str):
    return {
        "stock_code": stock_code,
        "status": "test successful",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stocks/{stock_code}/analysis/fundamental")
async def get_fundamental_analysis(stock_code: str):
    """基本面分析API端点"""
    try:
        # 获取股票基本信息
        basic_df = ak.stock_individual_info_em(symbol=stock_code)
        
        if basic_df is None or len(basic_df) == 0:
            return {"error": f"Stock {stock_code} not found"}
        
        # 转换基本信息为字典
        basic_info = {}
        for _, row in basic_df.iterrows():
            basic_info[row['item']] = row['value']
        
        return {
            "stock_code": stock_code,
            "stock_name": basic_info.get("股票简称", ""),
            "analysis_type": "fundamental",
            "current_price": basic_info.get("最新", 0),
            "market_cap": basic_info.get("总市值", 0),
            "industry": basic_info.get("行业", ""),
            "update_time": datetime.now().isoformat(),
            "basic_info": basic_info
        }
    except Exception as e:
        return {"error": f"Failed to get fundamental analysis: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3004)