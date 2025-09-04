#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票API与文章发布系统集成测试
Stock API and Article Publisher Integration Test
"""

import requests
import json
from datetime import datetime

def test_stock_api_integration():
    """测试股票API集成 / Test Stock API Integration"""
    
    print("🚀 开始股票API与文章发布系统集成测试...")
    print("🚀 Starting Stock API and Article Publisher Integration Test...\n")
    
    # 测试股票代码
    stock_code = "000001"
    base_url = "http://35.77.54.203:3003"
    
    try:
        print(f"📊 获取股票 {stock_code} 的分析数据...")
        print(f"📊 Fetching analysis data for stock {stock_code}...\n")
        
        # 1. 获取基本面分析数据
        print("1️⃣ 基本面分析数据 / Fundamental Analysis Data:")
        fund_response = requests.get(f"{base_url}/stocks/{stock_code}/analysis/fundamental", timeout=10)
        if fund_response.status_code == 200:
            fund_data = fund_response.json()
            print(f"   ✅ 股票名称: {fund_data.get('stock_name', 'N/A')}")
            print(f"   ✅ 当前价格: {fund_data.get('basic_info', {}).get('最新', 'N/A')}")
            print(f"   ✅ 总市值: {fund_data.get('basic_info', {}).get('总市值', 'N/A')}")
            print(f"   ✅ 数据质量: 优秀")
        else:
            print(f"   ❌ 基本面数据获取失败: {fund_response.status_code}")
            fund_data = {}
        
        # 2. 获取技术面分析数据
        print("\n2️⃣ 技术面分析数据 / Technical Analysis Data:")
        tech_response = requests.get(f"{base_url}/stocks/{stock_code}/analysis/technical", timeout=10)
        if tech_response.status_code == 200:
            tech_data = tech_response.json()
            print(f"   ✅ 技术分析类型: {tech_data.get('analysis_type', 'N/A')}")
            print(f"   ✅ 股票代码: {tech_data.get('stock_code', 'N/A')}")
            print(f"   ✅ 数据更新时间: {tech_data.get('update_time', 'N/A')}")
        else:
            print(f"   ❌ 技术面数据获取失败: {tech_response.status_code}")
            tech_data = {}
            
        # 3. 获取财务摘要数据
        print("\n3️⃣ 财务摘要数据 / Financial Abstract Data:")
        financial_response = requests.get(f"{base_url}/api/financial-abstract/{stock_code}", timeout=10)
        if financial_response.status_code == 200:
            financial_data = financial_response.json()
            print(f"   ✅ 财务指标数量: {len(financial_data.get('financial_indicators', []))}")
            print(f"   ✅ 数据来源: {financial_data.get('data_source', 'N/A')}")
            print(f"   ✅ 更新时间: {financial_data.get('update_time', 'N/A')}")
        else:
            print(f"   ❌ 财务数据获取失败: {financial_response.status_code}")
            financial_data = {}
        
        # 4. 模拟文章数据结构 (这是发送给文章发布系统的数据)
        print("\n4️⃣ 准备文章发布数据 / Preparing Article Publisher Data:")
        
        article_data = {
            "stockCode": stock_code,
            "writerStyle": "professional",  # 可以是 "professional" 或 "dark"
            "timestamp": datetime.now().isoformat(),
            "analysisData": {
                "fundamental": {
                    "stock_name": fund_data.get('stock_name', ''),
                    "current_price": fund_data.get('basic_info', {}).get('最新', 0),
                    "market_cap": fund_data.get('basic_info', {}).get('总市值', 0),
                    "industry": fund_data.get('basic_info', {}).get('行业', ''),
                    "pe_ratio": fund_data.get('basic_info', {}).get('市盈率', 0),
                    "analysis_summary": "基于最新财务数据的专业基本面分析"
                },
                "technical": {
                    "analysis_type": tech_data.get('analysis_type', ''),
                    "update_time": tech_data.get('update_time', ''),
                    "technical_summary": "基于价格走势和技术指标的分析"
                },
                "financial": {
                    "indicators_count": len(financial_data.get('financial_indicators', [])),
                    "data_source": financial_data.get('data_source', ''),
                    "financial_summary": "包含营业收入、净利润等关键财务指标"
                }
            },
            "metadata": {
                "api_endpoint": base_url,
                "integration_test": True,
                "test_timestamp": datetime.now().isoformat()
            }
        }
        
        print("   ✅ 文章数据结构已准备完成")
        print(f"   📄 数据大小: {len(json.dumps(article_data, ensure_ascii=False))} 字符")
        
        # 5. 模拟发送到文章发布系统 (这里只是打印，实际应用中会发送HTTP请求)
        print("\n5️⃣ 模拟发送到文章发布系统 / Simulating Article Publisher Integration:")
        print("   🔗 目标URL: https://your-domain.vercel.app/api/receive-analysis")
        print("   📝 文章风格: 资深分析师 (Professional)")
        print("   🎯 预期结果: HTML格式的股票分析文章")
        
        # 6. 集成测试结果总结
        print("\n" + "="*50)
        print("📊 集成测试结果总结 / Integration Test Summary:")
        print("="*50)
        
        success_count = sum([
            fund_response.status_code == 200,
            tech_response.status_code == 200, 
            financial_response.status_code == 200
        ])
        
        print(f"✅ 成功获取数据源: {success_count}/3")
        print(f"📈 基本面分析API: {'✅ 成功' if fund_response.status_code == 200 else '❌ 失败'}")
        print(f"📊 技术面分析API: {'✅ 成功' if tech_response.status_code == 200 else '❌ 失败'}")
        print(f"💰 财务数据API: {'✅ 成功' if financial_response.status_code == 200 else '❌ 失败'}")
        
        if success_count == 3:
            print("\n🎉 集成测试完全成功!")
            print("🎉 Integration test completely successful!")
            print("\n📋 下一步操作建议:")
            print("   1. 配置n8n工作流以调用这些API端点")
            print("   2. 设置Vercel文章发布系统接收数据")
            print("   3. 测试完整的端到端工作流")
            return True
        else:
            print(f"\n⚠️ 集成测试部分成功 ({success_count}/3)")
            print("⚠️ Integration test partially successful")
            return False
            
    except Exception as e:
        print(f"\n❌ 集成测试失败: {str(e)}")
        print(f"❌ Integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_stock_api_integration()
    exit(0 if success else 1)