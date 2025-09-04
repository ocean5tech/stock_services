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
        
        # 支持多种数据格式
        if isinstance(result, list) and len(result) >= 1:
            valid_outputs = 0
            for i, item in enumerate(result):
                print(f"DEBUG: Item {i}: type={type(item)}, keys={list(item.keys()) if isinstance(item, dict) else 'not dict'}")
                
                # 检查常见的输出字段
                if isinstance(item, dict):
                    # 方式1: 直接包含output字段 (langchain agent输出)
                    if 'output' in item:
                        output_content = str(item['output'])
                        print(f"DEBUG: Found 'output' field, length: {len(output_content)}")
                        if len(output_content) > 50:
                            valid_outputs += 1
                    
                    # 方式2: 包含text字段 (可能的文本输出)
                    elif 'text' in item:
                        text_content = str(item['text'])
                        print(f"DEBUG: Found 'text' field, length: {len(text_content)}")
                        if len(text_content) > 50:
                            valid_outputs += 1
                    
                    # 方式3: 整个item就是文本内容
                    elif len(str(item)) > 100:
                        print(f"DEBUG: Item itself is text content, length: {len(str(item))}")
                        valid_outputs += 1
                        
                    # 方式4: 检查是否有任何包含实质内容的字段
                    else:
                        for key, value in item.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"DEBUG: Found substantial content in field '{key}', length: {len(value)}")
                                valid_outputs += 1
                                break
                
                # 如果整个item是字符串且足够长
                elif isinstance(item, str) and len(item) > 100:
                    print(f"DEBUG: Item is direct string content, length: {len(item)}")
                    valid_outputs += 1
            
            print(f"DEBUG: Found {valid_outputs} valid outputs")
            return valid_outputs >= 1  # 至少1个有效输出就认为成功
        
        # 如果result是字典，检查是否包含articles数组
        elif isinstance(result, dict):
            if 'articles' in result and isinstance(result['articles'], list):
                print(f"DEBUG: Found articles array with {len(result['articles'])} items")
                return len(result['articles']) > 0
        
        print("DEBUG: No valid analysis result found")
        return False
    
    def process_n8n_result(self, result):
        """处理n8n返回的结果，动态处理任意数量的output"""
        if not isinstance(result, list):
            print(f"DEBUG: Result is not a list, type: {type(result)}")
            return None
            
        articles = []
        article_titles = ['资深股票文章写手', '暗黑股票文章写手']  # 对应你的两个AI agent
        
        try:
            for i, item in enumerate(result):
                content = None
                title = article_titles[i] if i < len(article_titles) else f'分析师 {i+1}'
                
                print(f"DEBUG: Processing item {i} for article")
                
                if isinstance(item, dict):
                    # 方式1: 标准output字段 (langchain agent)
                    if 'output' in item:
                        content = item['output']
                        print(f"DEBUG: Using 'output' field from item {i}")
                    # 方式2: text字段
                    elif 'text' in item:
                        content = item['text']
                        print(f"DEBUG: Using 'text' field from item {i}")
                    # 方式3: 寻找包含实质内容的字段
                    else:
                        for key, value in item.items():
                            if isinstance(value, str) and len(value) > 100:
                                content = value
                                print(f"DEBUG: Using '{key}' field from item {i}")
                                break
                
                elif isinstance(item, str):
                    # 直接是字符串内容
                    content = item
                    print(f"DEBUG: Item {i} is direct string content")
                
                # 确保内容有效且足够长
                if content and len(str(content)) > 50:
                    articles.append({
                        'id': f'article_{i+1}',
                        'title': f'{title} - 专业分析报告',
                        'content': content,
                        'index': i+1
                    })
                    print(f"DEBUG: Added article {i+1} with {len(str(content))} characters")
                else:
                    print(f"DEBUG: Skipping item {i}, insufficient content")
                        
        except Exception as e:
            print(f"DEBUG: Error processing n8n result: {e}")
            return None
        
        print(f"DEBUG: Successfully processed {len(articles)} articles")
        return {'articles': articles} if articles else None