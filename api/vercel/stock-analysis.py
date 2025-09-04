#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel无服务器函数 - 股票分析API
Stock Analysis API for Vercel Serverless Functions
集成n8n workflow进行专业股票分析
"""
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import urllib.request
import urllib.parse as urlparse_lib

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
            
            # API路由处理 - 统一处理所有请求
            if 'code' in query_params:
                response = self.handle_stock_info(query_params)
            else:
                response = {
                    "status": "API is running",
                    "message": "Stock Analysis API for Vercel",
                    "timestamp": datetime.now().isoformat(),
                    "usage": "Add ?code=STOCK_CODE to get stock info",
                    "example": "/api/vercel/stock-analysis?code=000001"
                }
            
            # 返回JSON响应
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "path": getattr(self, 'path', 'unknown')
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
        """处理股票信息查询 - 调用n8n workflow"""
        code = query_params.get('code', [''])[0]
        if not code:
            return {"error": "Missing stock code parameter"}
        
        try:
            # 直接调用n8n webhook并等待完成
            webhook_base_url = "https://ocean5tech.app.n8n.cloud/webhook/stock-master"
            
            # 构建带参数的URL
            params = urlparse_lib.urlencode({
                'code': code,
                'timestamp': datetime.now().isoformat()
            })
            webhook_url = f"{webhook_base_url}?{params}"
            
            # 发送GET请求到n8n webhook并等待完成
            req = urllib.request.Request(
                webhook_url,
                headers={
                    'User-Agent': 'Stock-Services/1.0'
                },
                method='GET'
            )
            
            # 等待n8n workflow完成（增加超时时间）
            with urllib.request.urlopen(req, timeout=180) as response:  # 3分钟超时
                response_data = response.read().decode('utf-8')
                n8n_result = json.loads(response_data)
                
                # 直接返回n8n的分析结果
                return {
                    "stock_code": code,
                    "data_source": "n8n_workflow",
                    "timestamp": datetime.now().isoformat(),
                    "analysis": n8n_result,
                    "status": "completed",
                    "webhook_url": webhook_url
                }
                
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP Error {e.code}: {e.reason}"
            
            # 特殊处理速率限制错误
            if e.code == 429:
                return {
                    "stock_code": code,
                    "error": "API速率限制：请求过于频繁，请稍后重试",
                    "error_type": "rate_limit",
                    "data_source": "n8n_workflow_error",
                    "timestamp": datetime.now().isoformat(),
                    "status": "rate_limited",
                    "retry_after": "建议等待1-2分钟后重试"
                }
            
            return {
                "stock_code": code,
                "error": error_msg,
                "data_source": "n8n_workflow_error",
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
            
        except urllib.error.URLError as e:
            return {
                "stock_code": code,
                "error": f"Network Error: {str(e)}",
                "data_source": "n8n_workflow_error", 
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
            
        except Exception as e:
            return {
                "stock_code": code,
                "error": f"Unexpected Error: {str(e)}",
                "data_source": "n8n_workflow_error",
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }