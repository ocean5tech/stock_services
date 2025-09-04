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
            # 调用n8n webhook (异步触发，不等待完成)
            webhook_base_url = "https://ocean5tech.app.n8n.cloud/webhook/stock-master"
            
            # 生成任务ID
            import hashlib
            task_id = hashlib.md5(f"{code}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            # 构建带参数的URL
            params = urlparse_lib.urlencode({
                'code': code,
                'task_id': task_id,
                'timestamp': datetime.now().isoformat()
            })
            webhook_url = f"{webhook_base_url}?{params}"
            
            # 发送GET请求到n8n webhook (短超时，只确认触发成功)
            req = urllib.request.Request(
                webhook_url,
                headers={
                    'User-Agent': 'Stock-Services/1.0'
                },
                method='GET'
            )
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    response_data = response.read().decode('utf-8')
                    trigger_result = json.loads(response_data)
                    
                    # 立即返回任务信息，不等待workflow完成
                    return {
                        "stock_code": code,
                        "task_id": task_id,
                        "data_source": "n8n_workflow",
                        "timestamp": datetime.now().isoformat(),
                        "status": "processing",
                        "message": "股票分析任务已启动",
                        "webhook_url": webhook_url,
                        "trigger_result": trigger_result,
                        "estimated_time": "预计需要2-3分钟完成分析"
                    }
                    
            except Exception as trigger_error:
                # 如果触发失败，尝试fallback方案
                return {
                    "stock_code": code,
                    "task_id": task_id,
                    "data_source": "n8n_workflow",
                    "timestamp": datetime.now().isoformat(),
                    "status": "triggered",
                    "message": "分析任务可能已启动",
                    "webhook_url": webhook_url,
                    "trigger_error": str(trigger_error),
                    "note": "由于超时限制，无法确认任务状态，请稍后查看结果"
                }
                
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP Error {e.code}: {e.reason}"
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