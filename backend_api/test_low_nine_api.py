"""
测试低九策略API端点
"""
import requests
import json

# API配置
API_BASE_URL = "http://192.168.31.237:5000"  # 根据实际情况修改
API_ENDPOINT = f"{API_BASE_URL}/api/screening/low-nine-strategy"

print("=" * 60)
print("测试低九策略API端点")
print("=" * 60)
print(f"API URL: {API_ENDPOINT}\n")

try:
    print("发送GET请求...")
    response = requests.get(API_ENDPOINT, timeout=30)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        result = response.json()
        print("✓ 请求成功!")
        print(f"\n策略名称: {result.get('strategy_name')}")
        print(f"筛选日期: {result.get('search_date')}")
        print(f"找到股票数量: {result.get('total')}")
        
        if result.get('data'):
            print(f"\n前3只股票:")
            for i, stock in enumerate(result['data'][:3], 1):
                print(f"  {i}. {stock['code']} {stock['name']}")
                print(f"     当前价格: {stock['current_price']}")
                print(f"     形态日期: {stock['pattern_start_date']} ~ {stock['pattern_end_date']}")
                print(f"     9天跌幅: {stock['decline_ratio']*100:.2f}%")
        else:
            print("\n未找到符合条件的股票")
    else:
        print(f"✗ 请求失败!")
        print(f"错误信息: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("✗ 连接失败! 请检查:")
    print("  1. 后端服务是否运行")
    print("  2. API_BASE_URL是否正确")
    print("  3. 端口是否被占用")
    
except requests.exceptions.Timeout:
    print("✗ 请求超时! 策略执行时间较长，这是正常的")
    print("  建议增加timeout时间或等待更长时间")
    
except Exception as e:
    print(f"✗ 发生错误: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
