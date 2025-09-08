#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API文档生成器
Generate API Documentation
"""
import json
import requests
from datetime import datetime

def generate_api_documentation():
    """生成API文档"""
    try:
        # 获取OpenAPI JSON数据
        response = requests.get('http://localhost:3003/openapi.json', timeout=10)
        if response.status_code != 200:
            print(f"❌ 无法获取OpenAPI数据: {response.status_code}")
            return
        
        data = response.json()
        
        # 生成Markdown文档
        markdown_content = f"""# Stock Analysis API 文档

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
服务地址: http://35.77.54.203:3003  
文档地址: http://35.77.54.203:3003/docs

## 服务概览
- **标题**: {data.get('info', {}).get('title', 'Stock Analysis API')}
- **版本**: {data.get('info', {}).get('version', '2.0.0')}  
- **描述**: {data.get('info', {}).get('description', '完整的股票分析API服务')}

## API 端点列表

"""
        
        # 分组整理API端点
        categories = {
            '### 基础数据API': [],
            '### 分析类API': [],
            '### 消息面API': [],
            '### 高级分析API': [],
            '### 系统API': []
        }
        
        for path, methods in data.get('paths', {}).items():
            for method, details in methods.items():
                endpoint_info = {
                    'method': method.upper(),
                    'path': path,
                    'summary': details.get('summary', '无描述'),
                    'description': details.get('description', ''),
                    'parameters': details.get('parameters', [])
                }
                
                # 根据路径分类
                if path.startswith('/api/'):
                    if 'comprehensive' in path or 'comparison' in path or 'fund-flow' in path:
                        categories['### 高级分析API'].append(endpoint_info)
                    else:
                        categories['### 基础数据API'].append(endpoint_info)
                elif '/analysis/' in path:
                    categories['### 分析类API'].append(endpoint_info)
                elif '/news/' in path:
                    categories['### 消息面API'].append(endpoint_info)
                elif path == '/':
                    categories['### 系统API'].append(endpoint_info)
                else:
                    categories['### 基础数据API'].append(endpoint_info)
        
        # 输出分类的API文档
        for category, endpoints in categories.items():
            if endpoints:
                markdown_content += f"{category}\n\n"
                for ep in endpoints:
                    markdown_content += f"#### `{ep['method']} {ep['path']}`\n\n"
                    markdown_content += f"**功能**: {ep['summary']}\n\n"
                    
                    if ep['description']:
                        markdown_content += f"**描述**: {ep['description']}\n\n"
                    
                    # 参数说明
                    if ep['parameters']:
                        markdown_content += "**参数**:\n"
                        for param in ep['parameters']:
                            param_name = param.get('name', '未知')
                            param_type = param.get('schema', {}).get('type', '未知类型')
                            param_desc = param.get('description', '无描述')
                            required = '必需' if param.get('required', False) else '可选'
                            markdown_content += f"- `{param_name}` ({param_type}, {required}): {param_desc}\n"
                        markdown_content += "\n"
                    
                    # 示例
                    example_url = path.replace('{stock_code}', '000001')
                    markdown_content += "**示例**:\n"
                    markdown_content += f"```bash\n"
                    markdown_content += f"curl \"http://35.77.54.203:3003{example_url}\"\n"
                    markdown_content += f"```\n\n"
                    markdown_content += "---\n\n"
        
        # 添加使用说明
        markdown_content += """## 使用说明

### 1. 股票代码格式
使用6位数字股票代码，如：
- `000001` - 平安银行
- `600519` - 贵州茅台  
- `000858` - 五粮液

### 2. 响应格式
所有API都返回JSON格式数据，基本结构：
```json
{
  "stock_code": "000001",
  "data_source": "akshare_comprehensive", 
  "update_time": "2025-09-08T07:03:28.201924",
  "data": { ... }
}
```

### 3. 错误处理
错误时返回包含 `error` 字段的JSON：
```json
{
  "error": "错误描述信息"
}
```

### 4. 数据源说明
- **akshare**: 主要数据提供商，提供A股实时和历史数据
- **更新频率**: 大部分数据实时更新，部分财务数据按季度更新

## 错误码说明

| 状态码 | 说明 |
|-------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |

## 开发示例

### Python调用示例
```python
import requests
import json

# 获取股票基本面分析
response = requests.get('http://35.77.54.203:3003/stocks/000001/analysis/fundamental')
if response.status_code == 200:
    data = response.json()
    print(f"股票名称: {data.get('stock_name')}")
    print(f"更新时间: {data.get('update_time')}")
else:
    print(f"请求失败: {response.status_code}")
```

### JavaScript调用示例
```javascript
// 获取技术面分析
fetch('http://35.77.54.203:3003/stocks/000001/analysis/technical')
  .then(response => response.json())
  .then(data => {
    console.log('股票代码:', data.stock_code);
    console.log('分析数据:', data.analysis_data);
  })
  .catch(error => {
    console.error('请求失败:', error);
  });
```

## 性能说明

- **响应时间**: 大部分API响应时间在1-3秒
- **并发限制**: 建议单个IP每分钟不超过60次请求
- **数据缓存**: 部分数据有短期缓存，避免频繁重复请求

## 联系信息

- **项目地址**: https://github.com/ocean5tech/stock_services
- **服务器**: 35.77.54.203:3003
- **技术支持**: 请通过GitHub Issues联系

---
*此文档由API自动生成，最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 保存文档
        with open('/home/ubuntu/stock_services/docs/API_DOCUMENTATION_COMPLETE.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print("✅ 完整API文档已生成: docs/API_DOCUMENTATION_COMPLETE.md")
        
        # 也生成简化版本
        simple_content = f"""# Stock Analysis API - 快速参考

服务地址: http://35.77.54.203:3003
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 主要API端点

"""
        for category, endpoints in categories.items():
            if endpoints:
                simple_content += f"{category}\n"
                for ep in endpoints:
                    simple_content += f"- `{ep['method']} {ep['path']}` - {ep['summary']}\n"
                simple_content += "\n"
        
        with open('/home/ubuntu/stock_services/docs/API_QUICK_REFERENCE.md', 'w', encoding='utf-8') as f:
            f.write(simple_content)
        
        print("✅ 快速参考文档已生成: docs/API_QUICK_REFERENCE.md")
        
    except Exception as e:
        print(f"❌ 生成文档失败: {e}")

if __name__ == "__main__":
    generate_api_documentation()