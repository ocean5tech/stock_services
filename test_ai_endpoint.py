#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI端点的简化脚本
Test script for AI endpoints
"""
import asyncio
import aiohttp
import json
import sys
from datetime import datetime

async def test_comprehensive_evaluation():
    """测试综合评估端点"""
    stock_code = "000858"
    url = "http://35.77.54.203:3003/ai/comprehensive-evaluation/000858"
    
    try:
        print(f"[{datetime.now()}] 开始测试综合评估端点...")
        print(f"URL: {url}")
        
        # 使用较短的超时时间来快速发现问题
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # 发送POST请求（如API所要求的）
            async with session.post(
                url, 
                json={"force_refresh": False},
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"[{datetime.now()}] 响应状态码: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"[{datetime.now()}] 成功获取响应数据:")
                    print(json.dumps(data, ensure_ascii=False, indent=2)[:500] + "...")
                else:
                    error_text = await response.text()
                    print(f"[{datetime.now()}] 错误响应: {error_text}")
    
    except asyncio.TimeoutError:
        print(f"[{datetime.now()}] ❌ 请求超时 (10秒)")
        print("可能的原因：")
        print("1. 数据聚合器调用过多接口导致超时")
        print("2. AI API调用时间过长")
        print("3. Redis连接问题")
        print("4. 内部循环调用")
        
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 请求失败: {e}")

async def test_basic_endpoints():
    """测试基础端点是否正常"""
    endpoints = [
        ("根端点", "GET", "http://35.77.54.203:3003/"),
        ("统一股票信息", "GET", "http://35.77.54.203:3003/stocks/000858"),
        ("基本面分析", "GET", "http://35.77.54.203:3003/stocks/000858/analysis/fundamental"),
        ("技术面分析", "GET", "http://35.77.54.203:3003/stocks/000858/analysis/technical"),
    ]
    
    print(f"\n[{datetime.now()}] 测试基础端点...")
    
    timeout = aiohttp.ClientTimeout(total=5)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for name, method, url in endpoints:
            try:
                if method == "GET":
                    async with session.get(url) as response:
                        print(f"  {name}: {response.status}")
                        if response.status >= 400:
                            error_text = await response.text()
                            print(f"    错误: {error_text[:100]}...")
                            
            except Exception as e:
                print(f"  {name}: ❌ {e}")

async def main():
    """主测试函数"""
    print("=" * 60)
    print("AI端点问题诊断测试")
    print("=" * 60)
    
    # 先测试基础端点
    await test_basic_endpoints()
    
    # 再测试AI端点
    await test_comprehensive_evaluation()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())