#!/usr/bin/env python3
"""
测试n8n webhook的正确地址
"""
import json
import urllib.request
import urllib.parse
from datetime import datetime

def test_webhook_url(webhook_url, description):
    """测试单个webhook URL"""
    print(f"\n🔧 测试{description}: {webhook_url}")
    
    stock_code = "000001"
    
    try:
        # 准备请求数据
        data = {
            "stock_code": stock_code,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📤 发送数据: {json.dumps(data, indent=2)}")
        
        # 发送POST请求到n8n webhook
        json_data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            webhook_url,
            data=json_data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Stock-Services-Test/1.0'
            },
            method='POST'
        )
        
        print("🌐 正在调用webhook...")
        
        with urllib.request.urlopen(req, timeout=45) as response:
            response_data = response.read().decode('utf-8')
            status_code = response.getcode()
            print(f"📥 HTTP状态码: {status_code}")
            
            if status_code == 200:
                print("✅ Webhook调用成功!")
                try:
                    result = json.loads(response_data)
                    print("📄 响应内容:")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                    return True, result
                except json.JSONDecodeError:
                    print(f"📄 原始响应: {response_data}")
                    return True, response_data
            else:
                print(f"⚠️  状态码: {status_code}")
                return False, None
        
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误: {e.code} - {e.reason}")
        try:
            error_response = e.read().decode('utf-8')
            print(f"错误详情: {error_response}")
        except:
            pass
        return False, None
        
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {str(e)}")
        return False, None
        
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return False, None

def main():
    """测试两个可能的webhook地址"""
    print("🚀 开始测试n8n webhook地址...")
    
    # 测试地址1：webhook-test路径
    url1 = "https://ocean5tech.app.n8n.cloud/webhook-test/stock-master"
    success1, result1 = test_webhook_url(url1, "测试环境webhook")
    
    # 测试地址2：webhook路径
    url2 = "https://ocean5tech.app.n8n.cloud/webhook/stock-master"  
    success2, result2 = test_webhook_url(url2, "生产环境webhook")
    
    # 总结结果
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"🔗 webhook-test路径: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"🔗 webhook路径: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1:
        print(f"\n✅ 推荐使用: {url1}")
        return url1
    elif success2:
        print(f"\n✅ 推荐使用: {url2}")
        return url2
    else:
        print("\n❌ 两个webhook地址都无法访问")
        return None

if __name__ == "__main__":
    correct_url = main()
    if correct_url:
        print(f"\n🎉 找到可用的webhook地址: {correct_url}")
    else:
        print("\n💡 建议检查n8n workflow是否已激活，或确认webhook路径是否正确")