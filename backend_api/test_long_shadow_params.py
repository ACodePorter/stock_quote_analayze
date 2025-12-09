"""
测试长下影线策略参数化API
"""
import requests

# 测试API
base_url = "http://localhost:5000"

print("=" * 60)
print("测试长下影线策略参数化API")
print("=" * 60)

# 测试1: 使用默认参数
print("\n测试1: 使用默认参数")
try:
    response = requests.get(f"{base_url}/api/screening/long-lower-shadow-strategy", timeout=10)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: 找到 {data.get('total', 0)} 只股票")
        print(f"参数: {data.get('parameters', {})}")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")

# 测试2: 使用自定义参数
print("\n测试2: 使用自定义参数")
params = {
    'lower_shadow_ratio': 1.5,
    'upper_shadow_ratio': 0.25,
    'min_amplitude': 0.03,
    'recent_days': 3
}
try:
    response = requests.get(
        f"{base_url}/api/screening/long-lower-shadow-strategy",
        params=params,
        timeout=10
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: 找到 {data.get('total', 0)} 只股票")
        print(f"参数: {data.get('parameters', {})}")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")

# 测试3: 测试参数边界
print("\n测试3: 测试参数边界")
params = {
    'lower_shadow_ratio': 0.5,  # 最小值
    'upper_shadow_ratio': 0.5,  # 最大值
    'min_amplitude': 0.01,      # 最小值
    'recent_days': 10           # 最大值
}
try:
    response = requests.get(
        f"{base_url}/api/screening/long-lower-shadow-strategy",
        params=params,
        timeout=10
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: 找到 {data.get('total', 0)} 只股票")
        print(f"参数: {data.get('parameters', {})}")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"请求失败: {str(e)}")

print("\n" + "=" * 60)
