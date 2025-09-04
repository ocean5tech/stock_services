#!/usr/bin/env python3
"""
本地测试Vercel API功能
"""
import sys
import os
import importlib.util

# 动态加载模块
spec = importlib.util.spec_from_file_location("stock_analysis", "api/vercel/stock-analysis.py")
stock_analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stock_analysis)

handler = stock_analysis.handler
from io import StringIO
import json

class MockRequest:
    def __init__(self, path, method='GET'):
        self.path = path
        self.command = method
        
def test_api():
    """测试API功能"""
    print("🔧 测试Vercel API本地功能...")
    
    # 创建模拟处理器
    h = handler()
    h.path = '/api/vercel/stock-analysis?code=000001'
    
    # 模拟响应输出
    h.wfile = StringIO()
    
    # 模拟方法
    def mock_send_response(code):
        print(f"Response Code: {code}")
    def mock_send_header(name, value):
        print(f"Header: {name}: {value}")
    def mock_end_headers():
        print("Headers ended")
        
    h.send_response = mock_send_response
    h.send_header = mock_send_header  
    h.end_headers = mock_end_headers
    
    try:
        # 测试股票信息查询
        query_params = {'code': ['000001']}
        result = h.handle_stock_info(query_params)
        print("\n✅ 股票信息查询测试成功:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 测试股票分析
        analysis_result = h.handle_stock_analysis('000001', {'type': ['basic']})
        print("\n✅ 股票分析测试成功:")
        print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
        
        print("\n🎉 所有API功能测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api()