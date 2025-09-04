#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel无服务器函数 - 股票分析API
Stock Analysis API for Vercel Serverless Functions
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# 添加路径以导入akshare (如果需要的话)
# 注意：Vercel上可能需要使用轻量级的数据源替代akshare

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
            if path == '/api/vercel/stock-analysis':
                response = self.handle_stock_info(query_params)
            elif path.startswith('/api/vercel/stock-analysis/'):
                # 提取股票代码
                stock_code = path.split('/')[-1]
                response = self.handle_stock_analysis(stock_code, query_params)
            else:
                response = {
                    "error": "API endpoint not found",
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
        
        # 这里使用模拟数据，实际部署时可以接入真实数据源
        mock_data = {
            "000001": {
                "name": "平安银行",
                "price": 11.75,
                "change": -0.23,
                "change_percent": -1.92,
                "market_cap": "2280亿",
                "industry": "银行"
            },
            "000002": {
                "name": "万科A",
                "price": 8.45,
                "change": 0.12,
                "change_percent": 1.44,
                "market_cap": "950亿",
                "industry": "房地产"
            }
        }
        
        stock_info = mock_data.get(code, {
            "name": f"股票{code}",
            "price": 0,
            "change": 0,
            "change_percent": 0,
            "market_cap": "未知",
            "industry": "未知"
        })
        
        return {
            "stock_code": code,
            "stock_info": stock_info,
            "data_source": "vercel_serverless",
            "timestamp": datetime.now().isoformat()
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