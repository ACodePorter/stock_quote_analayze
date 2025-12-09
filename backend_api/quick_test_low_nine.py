"""
快速测试低九策略API - 使用简单的HTTP请求
"""
import sys
import time
import threading

def test_api():
    try:
        import requests
        
        url = "http://localhost:5000/api/screening/low-nine-strategy"
        print(f"正在测试API: {url}")
        print("请求已发送，等待响应...")
        print("注意：这个策略需要遍历所有A股，可能需要1-5分钟\n")
        
        start_time = time.time()
        
        # 设置较长的超时时间
        response = requests.get(url, timeout=300)  # 5分钟超时
        
        elapsed = time.time() - start_time
        
        print(f"\n✓ 收到响应! 耗时: {elapsed:.2f}秒")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"策略名称: {result.get('strategy_name')}")
            print(f"找到股票数量: {result.get('total')}")
            
            if result.get('data'):
                print(f"\n前5只股票:")
                for i, stock in enumerate(result['data'][:5], 1):
                    print(f"  {i}. {stock['code']} {stock['name']} - "
                          f"跌幅: {stock['decline_ratio']*100:.2f}%")
        else:
            print(f"错误: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n✗ 请求超时（超过5分钟）")
        print("可能原因:")
        print("  1. 数据库查询太慢")
        print("  2. 数据量太大")
        print("  3. 后端代码有死循环")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 连接失败")
        print("请检查后端服务是否在 localhost:5000 运行")
        
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("低九策略API测试")
    print("=" * 60)
    print()
    
    # 在单独的线程中运行，这样可以看到进度
    test_thread = threading.Thread(target=test_api)
    test_thread.daemon = True
    test_thread.start()
    
    # 显示进度
    start = time.time()
    while test_thread.is_alive():
        elapsed = int(time.time() - start)
        print(f"\r等待中... {elapsed}秒", end='', flush=True)
        time.sleep(1)
        
        if elapsed > 300:  # 5分钟后停止
            print("\n\n超过5分钟，停止等待")
            break
    
    test_thread.join(timeout=1)
    print("\n\n" + "=" * 60)
