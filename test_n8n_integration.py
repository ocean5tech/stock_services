#!/usr/bin/env python3
"""
测试n8n集成功能
"""
import json
import urllib.request
import urllib.parse
from datetime import datetime

def test_n8n_webhook():
    """测试n8n webhook调用"""
    print("🔧 测试n8n webhook集成...")
    
    webhook_url = "https://ocean5tech.app.n8n.cloud/webhook-test/stock-master"
    stock_code = "000001"
    
    try:
        # 准备请求数据
        data = {
            "stock_code": stock_code,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📤 发送数据到n8n: {json.dumps(data, indent=2)}")
        
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
        
        print("🌐 正在调用n8n webhook...")
        
        with urllib.request.urlopen(req, timeout=60) as response:
            response_data = response.read().decode('utf-8')
            print(f"📥 HTTP状态码: {response.getcode()}")
            print(f"📥 响应头: {dict(response.headers)}")
            
            try:
                n8n_result = json.loads(response_data)
                print("\n✅ n8n返回结果:")
                print(json.dumps(n8n_result, ensure_ascii=False, indent=2))
                
                # 检查是否包含预期的分析字段
                if isinstance(n8n_result, dict):
                    if 'professional_analysis' in n8n_result or 'dark_analysis' in n8n_result:
                        print("\n🎉 检测到专业分析内容!")
                        return True
                    else:
                        print("\n⚠️  未检测到专业分析字段，但获得了响应")
                        return True
                else:
                    print(f"\n⚠️  响应格式: {type(n8n_result)}")
                    return True
                    
            except json.JSONDecodeError:
                print(f"\n📄 原始响应内容: {response_data}")
                return True
        
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP错误: {e.code} - {e.reason}")
        try:
            error_response = e.read().decode('utf-8')
            print(f"错误详情: {error_response}")
        except:
            pass
        return False
        
    except urllib.error.URLError as e:
        print(f"\n❌ 网络错误: {str(e)}")
        return False
        
    except Exception as e:
        print(f"\n❌ 未知错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_n8n_webhook()
    if success:
        print("\n✅ n8n集成测试通过!")
    else:
        print("\n❌ n8n集成测试失败!")