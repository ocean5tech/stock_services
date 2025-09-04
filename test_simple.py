#!/usr/bin/env python3
"""
简单测试API功能
"""
import json
from datetime import datetime
import random

def handle_stock_info(query_params):
    """处理股票信息查询"""
    code = query_params.get('code', [''])[0]
    if not code:
        return {"error": "Missing stock code parameter"}
    
    # 增强版模拟数据
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

def test_api():
    """测试API功能"""
    print("🔧 测试API功能...")
    
    try:
        # 测试股票信息查询
        query_params = {'code': ['000001']}
        result = handle_stock_info(query_params)
        print("\n✅ 股票信息查询测试成功:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n🎉 API功能测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api()