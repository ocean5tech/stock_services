# -*- coding: utf-8 -*-
"""
AI分析API测试脚本
Test script for AI Analysis APIs
"""
import asyncio
import aiohttp
import json
import os
from datetime import datetime

# 测试配置
BASE_URL = "http://35.77.54.203:3003"  # 使用3003端口的整合API
TEST_STOCK_CODE = "000001"  # 平安银行作为测试股票

async def test_health_check():
    """测试健康检查端点"""
    print(f"\n=== 测试健康检查 ===")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/ai/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✓ 健康检查通过")
                    print(f"状态: {data.get('status')}")
                    
                    # 显示组件状态
                    components = data.get('components', {})
                    for component, status in components.items():
                        if isinstance(status, dict):
                            comp_status = status.get('status', 'unknown')
                            print(f"  - {component}: {comp_status}")
                        else:
                            print(f"  - {component}: {status}")
                    
                    return True
                else:
                    print(f"✗ 健康检查失败: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        print(f"✗ 健康检查异常: {e}")
        return False

async def test_cache_status():
    """测试缓存状态查询"""
    print(f"\n=== 测试缓存状态查询 ===")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}/ai/cache/status/{TEST_STOCK_CODE}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 缓存状态查询成功: {TEST_STOCK_CODE}")
                    print(f"技术面缓存: {'存在' if data.get('trading_signal', {}).get('exists') else '不存在'}")
                    print(f"综合评估缓存: {'存在' if data.get('comprehensive_eval', {}).get('exists') else '不存在'}")
                    return True
                else:
                    print(f"✗ 缓存状态查询失败: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        print(f"✗ 缓存状态查询异常: {e}")
        return False

async def test_trading_signal_api():
    """测试技术面交易信号API"""
    print(f"\n=== 测试技术面交易信号API ===")
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            url = f"{BASE_URL}/ai/trading-signal/{TEST_STOCK_CODE}"
            request_data = {"force_refresh": True}
            
            print(f"请求URL: {url}")
            print("发起请求...")
            
            async with session.post(url, json=request_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 技术面交易信号API测试成功: {TEST_STOCK_CODE}")
                    
                    # 显示关键信息
                    signal = data.get('immediate_trading_signal', {})
                    print(f"交易行动: {signal.get('action', 'N/A')}")
                    print(f"入场条件: {signal.get('entry_condition', 'N/A')}")
                    print(f"数据完整性: {data.get('data_completeness', 0):.2%}")
                    
                    # 显示API使用情况
                    usage = data.get('api_usage', {})
                    if usage:
                        print(f"AI使用token: 输入{usage.get('input_tokens', 0)}, 输出{usage.get('output_tokens', 0)}")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"✗ 技术面交易信号API失败: HTTP {response.status}")
                    print(f"错误响应: {error_text}")
                    return False
                    
    except asyncio.TimeoutError:
        print("✗ 技术面交易信号API超时")
        return False
    except Exception as e:
        print(f"✗ 技术面交易信号API异常: {e}")
        return False

async def test_comprehensive_evaluation_api():
    """测试综合评估API"""
    print(f"\n=== 测试综合评估API ===")
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=90)) as session:
            url = f"{BASE_URL}/ai/comprehensive-evaluation/{TEST_STOCK_CODE}"
            request_data = {"force_refresh": True}
            
            print(f"请求URL: {url}")
            print("发起请求...")
            
            async with session.post(url, json=request_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ 综合评估API测试成功: {TEST_STOCK_CODE}")
                    
                    # 显示关键信息
                    evaluation = data.get('comprehensive_evaluation', {})
                    print(f"投资评级: {evaluation.get('investment_rating', 'N/A')}")
                    print(f"目标价格: {evaluation.get('target_price', 'N/A')}")
                    print(f"上涨空间: {evaluation.get('upside_potential', 'N/A')}")
                    print(f"数据完整性: {data.get('data_completeness', 0):.2%}")
                    
                    # 显示推理过程
                    reasoning = data.get('evidence_and_reasoning', {})
                    reasoning_chain = reasoning.get('reasoning_chain', [])
                    if reasoning_chain:
                        print(f"推理步骤: {len(reasoning_chain)}步")
                    
                    # 显示API使用情况
                    usage = data.get('api_usage', {})
                    if usage:
                        print(f"AI使用token: 输入{usage.get('input_tokens', 0)}, 输出{usage.get('output_tokens', 0)}")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"✗ 综合评估API失败: HTTP {response.status}")
                    print(f"错误响应: {error_text}")
                    return False
                    
    except asyncio.TimeoutError:
        print("✗ 综合评估API超时")
        return False
    except Exception as e:
        print(f"✗ 综合评估API异常: {e}")
        return False

async def test_cache_functionality():
    """测试缓存功能"""
    print(f"\n=== 测试缓存功能 ===")
    
    try:
        # 第一次请求（强制刷新，不使用缓存）
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}/ai/trading-signal/{TEST_STOCK_CODE}"
            
            # 第一次请求
            start_time = datetime.now()
            async with session.post(url, json={"force_refresh": True}) as response:
                first_duration = (datetime.now() - start_time).total_seconds()
                if response.status != 200:
                    print("✗ 缓存测试失败：第一次请求失败")
                    return False
                first_data = await response.json()
            
            # 等待1秒
            await asyncio.sleep(1)
            
            # 第二次请求（使用缓存）
            start_time = datetime.now()
            async with session.post(url, json={"force_refresh": False}) as response:
                second_duration = (datetime.now() - start_time).total_seconds()
                if response.status != 200:
                    print("✗ 缓存测试失败：第二次请求失败")
                    return False
                second_data = await response.json()
            
            # 验证缓存
            if second_data.get('cached'):
                print(f"✓ 缓存功能正常")
                print(f"第一次请求耗时: {first_duration:.2f}秒")
                print(f"第二次请求耗时(缓存): {second_duration:.2f}秒")
                print(f"缓存加速比: {first_duration/second_duration:.1f}x")
                return True
            else:
                print("✗ 缓存功能异常：第二次请求未使用缓存")
                return False
                
    except Exception as e:
        print(f"✗ 缓存测试异常: {e}")
        return False

async def test_invalid_stock_code():
    """测试无效股票代码"""
    print(f"\n=== 测试无效股票代码处理 ===")
    
    invalid_codes = ["12345", "abcdef", "0000012"]
    
    for code in invalid_codes:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{BASE_URL}/ai/trading-signal/{code}"
                async with session.post(url, json={}) as response:
                    if response.status == 400:
                        print(f"✓ 正确拒绝无效股票代码: {code}")
                    else:
                        print(f"✗ 未正确处理无效股票代码: {code} (HTTP {response.status})")
                        return False
        except Exception as e:
            print(f"✗ 测试无效股票代码时异常: {e}")
            return False
    
    print("✓ 无效股票代码处理测试通过")
    return True

async def main():
    """主测试函数"""
    print("=== AI分析API集成测试 ===")
    print(f"测试服务器: {BASE_URL}")
    print(f"测试股票: {TEST_STOCK_CODE}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查环境变量
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n⚠️ 警告: ANTHROPIC_API_KEY环境变量未设置")
        print("某些测试可能会失败")
    
    test_results = []
    
    # 运行所有测试
    tests = [
        ("健康检查", test_health_check),
        ("缓存状态查询", test_cache_status),
        ("无效股票代码处理", test_invalid_stock_code),
        ("技术面交易信号API", test_trading_signal_api),
        ("综合评估API", test_comprehensive_evaluation_api),
        ("缓存功能", test_cache_functionality),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        result = await test_func()
        test_results.append((test_name, result))
    
    # 测试总结
    print(f"\n{'='*50}")
    print("=== 测试总结 ===")
    
    passed = 0
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(test_results)
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！AI分析API部署成功")
    else:
        print("⚠️ 部分测试失败，请检查配置和服务状态")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())