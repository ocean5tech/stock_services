#!/usr/bin/env python3
"""
测试n8n webhook的GET请求方式
"""
import json
import urllib.request
import urllib.parse
from datetime import datetime

def test_webhook_get(base_url, description):
    """测试使用GET请求调用webhook"""
    print(f"\n🔧 测试{description} (GET方式): {base_url}")
    
    stock_code = "000001"
    
    try:
        # 方式1：通过URL参数传递
        url_with_params = f"{base_url}?code={stock_code}&timestamp={datetime.now().isoformat()}"
        print(f"📤 请求URL: {url_with_params}")
        
        req = urllib.request.Request(
            url_with_params,
            headers={
                'User-Agent': 'Stock-Services-Test/1.0'
            },
            method='GET'
        )
        
        print("🌐 正在调用webhook (GET)...")
        
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
                    return True, result, url_with_params
                except json.JSONDecodeError:
                    print(f"📄 原始响应: {response_data}")
                    return True, response_data, url_with_params
            else:
                print(f"⚠️  状态码: {status_code}")
                return False, None, None
        
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误: {e.code} - {e.reason}")
        try:
            error_response = e.read().decode('utf-8')
            print(f"错误详情: {error_response}")
        except:
            pass
        return False, None, None
        
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {str(e)}")
        return False, None, None
        
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return False, None, None

def main():
    """测试两个webhook地址的GET方式"""
    print("🚀 开始测试n8n webhook (GET方式)...")
    
    # 测试地址1：webhook-test路径
    url1 = "https://ocean5tech.app.n8n.cloud/webhook-test/stock-master"
    success1, result1, final_url1 = test_webhook_get(url1, "测试环境webhook")
    
    # 测试地址2：webhook路径  
    url2 = "https://ocean5tech.app.n8n.cloud/webhook/stock-master"
    success2, result2, final_url2 = test_webhook_get(url2, "生产环境webhook")
    
    # 总结结果
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"🔗 webhook-test路径: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"🔗 webhook路径: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1:
        print(f"\n✅ 推荐使用GET方式: {url1}")
        return url1, 'GET'
    elif success2:
        print(f"\n✅ 推荐使用GET方式: {url2}")
        return url2, 'GET'
    else:
        print("\n❌ GET方式也无法访问webhook")
        return None, None

if __name__ == "__main__":
    correct_url, method = main()
    if correct_url:
        print(f"\n🎉 找到可用的webhook: {correct_url} (方法: {method})")
        print("💡 需要修改API代码使用GET方式调用webhook")
    else:
        print("\n💡 建议检查n8n workflow配置和webhook设置")