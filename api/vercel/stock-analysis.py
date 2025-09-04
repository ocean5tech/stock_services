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
            
            # API路由处理 - 区分触发和检查
            if 'code' in query_params:
                # 检查是否是结果检查请求
                if 'check_result' in query_params:
                    response = self.handle_check_result(query_params)
                else:
                    response = self.handle_stock_info(query_params)
            else:
                response = {
                    "status": "API is running",
                    "message": "Stock Analysis API for Vercel",
                    "timestamp": datetime.now().isoformat(),
                    "usage": "Add ?code=STOCK_CODE to trigger analysis, ?code=XXX&check_result=1 to check results",
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
            # 触发n8n workflow但不等待完成
            webhook_base_url = "https://ocean5tech.app.n8n.cloud/webhook/stock-master"
            
            # 构建带参数的URL
            params = urlparse_lib.urlencode({
                'code': code,
                'timestamp': datetime.now().isoformat()
            })
            webhook_url = f"{webhook_base_url}?{params}"
            
            # 发送GET请求触发workflow（短超时）
            req = urllib.request.Request(
                webhook_url,
                headers={
                    'User-Agent': 'Stock-Services/1.0'
                },
                method='GET'
            )
            
            try:
                with urllib.request.urlopen(req, timeout=60) as response:  # 增加超时让workflow有时间完成
                    response_data = response.read().decode('utf-8')
                    trigger_result = json.loads(response_data)
                    
                    # 检查是否返回了实际的分析结果
                    if self.is_analysis_result(trigger_result):
                        # 如果返回了分析结果，直接处理并返回
                        processed_analysis = self.process_n8n_result(trigger_result)
                        return {
                            "stock_code": code,
                            "data_source": "n8n_workflow",
                            "timestamp": datetime.now().isoformat(),
                            "analysis": processed_analysis,
                            "status": "completed",
                            "webhook_url": webhook_url
                        }
                    else:
                        # 立即返回任务状态，等待后续检查
                        return {
                            "stock_code": code,
                            "data_source": "n8n_workflow",
                            "timestamp": datetime.now().isoformat(),
                            "status": "processing",
                            "message": f"股票 {code} 分析已启动",
                            "note": "请点击下方按钮检查分析结果",
                            "webhook_url": webhook_url,
                            "trigger_result": trigger_result
                        }
                    
            except Exception as trigger_error:
                # 触发可能成功但响应超时
                return {
                    "stock_code": code,
                    "data_source": "n8n_workflow", 
                    "timestamp": datetime.now().isoformat(),
                    "status": "triggered",
                    "message": f"股票 {code} 分析可能已启动",
                    "note": "由于网络原因无法确认，请稍后检查结果",
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
    
    def handle_check_result(self, query_params):
        """检查分析结果 - 重新调用n8n获取结果"""
        code = query_params.get('code', [''])[0]
        if not code:
            return {"error": "Missing stock code parameter"}
        
        # 重新调用n8n webhook获取最新结果
        try:
            webhook_base_url = "https://ocean5tech.app.n8n.cloud/webhook/stock-master"
            
            # 构建带参数的URL
            params = urlparse_lib.urlencode({
                'code': code,
                'timestamp': datetime.now().isoformat()
            })
            webhook_url = f"{webhook_base_url}?{params}"
            
            print(f"DEBUG: Calling webhook for result check: {webhook_url}")
            
            req = urllib.request.Request(
                webhook_url,
                headers={
                    'User-Agent': 'Stock-Services/1.0'
                },
                method='GET'
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:  # 长超时等待workflow完成
                response_data = response.read().decode('utf-8')
                print(f"DEBUG: Raw response length: {len(response_data)}")
                print(f"DEBUG: Raw response preview: {response_data[:200]}...")
                
                result = json.loads(response_data)
                print(f"DEBUG: Parsed result type: {type(result)}")
                
                # 检查是否有分析结果
                if self.is_analysis_result(result):
                    print("DEBUG: Analysis result found, processing...")
                    processed_analysis = self.process_n8n_result(result)
                    return {
                        "stock_code": code,
                        "data_source": "n8n_workflow",
                        "timestamp": datetime.now().isoformat(),
                        "analysis": processed_analysis,
                        "status": "completed",
                        "webhook_url": webhook_url
                    }
                else:
                    print("DEBUG: No analysis result found, returning processing status")
                    return {
                        "stock_code": code,
                        "data_source": "result_check",
                        "timestamp": datetime.now().isoformat(),
                        "status": "processing",
                        "message": "分析还在进行中",
                        "note": "workflow尚未完成，请稍后再试",
                        "debug_result_type": str(type(result)),
                        "debug_result_preview": str(result)[:200] if result else "null"
                    }
                    
        except Exception as e:
            return {
                "stock_code": code,
                "error": f"检查结果失败: {str(e)}",
                "data_source": "result_check_error",
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def is_analysis_result(self, result):
        """判断是否是真正的分析结果"""
        print(f"DEBUG: Checking result type: {type(result)}")
        print(f"DEBUG: Result content: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
        
        if isinstance(result, list) and len(result) >= 1:  # 至少1个输出就算有结果
            # 检查是否包含分析输出
            for i, item in enumerate(result):
                print(f"DEBUG: Item {i}: type={type(item)}, keys={list(item.keys()) if isinstance(item, dict) else 'not dict'}")
                if isinstance(item, dict) and 'output' in item:
                    output_content = str(item['output'])
                    print(f"DEBUG: Output length: {len(output_content)}")
                    if len(output_content) > 50:  # 降低阈值，确保有实际内容
                        print(f"DEBUG: Found valid output in item {i}")
                        return True
        print("DEBUG: No valid analysis result found")
        return False
    
    def process_n8n_result(self, result):
        """处理n8n返回的结果，动态处理任意数量的output"""
        if not isinstance(result, list):
            return None
            
        articles = []
        
        try:
            for i, item in enumerate(result):
                if isinstance(item, dict) and 'output' in item:
                    output_content = item['output']
                    if output_content and len(str(output_content)) > 50:  # 确保有实际内容
                        articles.append({
                            'id': f'article_{i+1}',
                            'title': f'分析文章 {i+1}',
                            'content': output_content,
                            'index': i+1
                        })
                        
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error processing n8n result: {e}")
            return None
            
        return {'articles': articles} if articles else None