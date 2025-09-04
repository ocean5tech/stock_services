#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel无服务器函数 - 股票分析API
Stock Analysis API for Vercel Serverless Functions
轻量级版本 - 不依赖akshare，使用模拟数据
"""
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        try:
            # 解析URL路径
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            query_params = parse_qs(parsed_path.query)
            
            # 设置CORS头
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # API路由处理
            if path.endswith('/api/vercel/stock-analysis') or path.endswith('/api/vercel/stock-analysis.py'):
                response = self.handle_stock_info(query_params)
            elif '/api/vercel/stock-analysis/' in path:
                # 提取股票代码
                stock_code = path.split('/')[-1]
                response = self.handle_stock_analysis(stock_code, query_params)
            else:
                response = {
                    "status": "API is running",
                    "message": "Stock Analysis API for Vercel",
                    "timestamp": datetime.now().isoformat(),
                    "available_endpoints": {
                        "stock_info": "/api/vercel/stock-analysis?code=STOCK_CODE",
                        "stock_analysis": "/api/vercel/stock-analysis/STOCK_CODE"
                    }
                }
            
            # 返回JSON响应
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理OPTIONS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_stock_info(self, query_params):
        """处理股票信息查询"""
        code = query_params.get('code', [''])[0]
        if not code:
            return {"error": "Missing stock code parameter"}
        
        # 增强版模拟数据，更丰富的股票信息
        mock_data = {
            "000001": {
                "name": "平安银行",
                "price": round(11.75 + random.uniform(-0.5, 0.5), 2),
                "change": round(random.uniform(-0.5, 0.5), 2),
                "change_percent": round(random.uniform(-3, 3), 2),
                "market_cap": "2280亿",
                "industry": "银行",
                "volume": random.randint(100000, 500000),
                "high": 12.1,
                "low": 11.2,
                "pe_ratio": 5.8,
                "pb_ratio": 0.7
            },
            "000002": {
                "name": "万科A",
                "price": round(8.45 + random.uniform(-0.3, 0.3), 2),
                "change": round(random.uniform(-0.3, 0.3), 2),
                "change_percent": round(random.uniform(-2, 2), 2),
                "market_cap": "950亿",
                "industry": "房地产",
                "volume": random.randint(80000, 300000),
                "high": 8.8,
                "low": 8.1,
                "pe_ratio": 15.2,
                "pb_ratio": 1.1
            },
            "000858": {
                "name": "五粮液",
                "price": round(158.50 + random.uniform(-2, 2), 2),
                "change": round(random.uniform(-2, 2), 2),
                "change_percent": round(random.uniform(-1.5, 1.5), 2),
                "market_cap": "6180亿",
                "industry": "食品饮料",
                "volume": random.randint(50000, 200000),
                "high": 162.1,
                "low": 155.3,
                "pe_ratio": 28.5,
                "pb_ratio": 4.2
            }
        }
        
        # 为未知股票生成随机数据
        if code not in mock_data:
            base_price = random.uniform(5, 200)
            change_val = random.uniform(-base_price*0.1, base_price*0.1)
            stock_info = {
                "name": f"股票{code}",
                "price": round(base_price, 2),
                "change": round(change_val, 2),
                "change_percent": round((change_val/base_price)*100, 2),
                "market_cap": f"{random.randint(10, 5000)}亿",
                "industry": random.choice(["科技", "金融", "医药", "消费", "制造", "能源"]),
                "volume": random.randint(10000, 1000000),
                "high": round(base_price * 1.05, 2),
                "low": round(base_price * 0.95, 2),
                "pe_ratio": round(random.uniform(5, 50), 1),
                "pb_ratio": round(random.uniform(0.5, 5), 1)
            }
        else:
            stock_info = mock_data[code]
        
        return {
            "stock_code": code,
            "stock_info": stock_info,
            "data_source": "vercel_serverless",
            "timestamp": datetime.now().isoformat(),
            "note": "This is demo data. In production, connect to real stock data API."
        }
    
    def handle_stock_analysis(self, stock_code, query_params):
        """处理股票分析请求"""
        analysis_type = query_params.get('type', ['basic'])[0]
        
        # 模拟分析数据
        analysis_data = {
            "stock_code": stock_code,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "analysis_result": {
                "recommendation": "中性",
                "target_price": "12.50",
                "risk_level": "中等",
                "key_metrics": {
                    "pe_ratio": 5.8,
                    "pb_ratio": 0.7,
                    "roe": 12.5
                }
            }
        }
        
        return analysis_data