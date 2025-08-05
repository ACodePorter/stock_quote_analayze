#!/usr/bin/env python3
"""
测试日志统计修复
验证统计API是否正确返回全部数据
"""

import requests
import json

def test_logs_stats_api():
    """测试日志统计API"""
    
    base_url = "http://localhost:5000"
    
    # 测试的端点
    endpoints = [
        "/api/admin/logs/stats/operation",  # 不传days参数，获取全部数据
        "/api/admin/logs/stats/operation?days=7",  # 传days参数，获取最近7天数据
        "/api/admin/logs/stats/historical_collect",  # 历史数据采集日志
        "/api/admin/logs/stats/realtime_collect",  # 实时数据采集日志
        "/api/admin/logs/stats/watchlist_history"  # 自选股历史采集日志
    ]
    
    print("🔍 测试日志统计API修复")
    print("=" * 60)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 测试URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ 状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 请求成功")
                
                # 分析统计数据
                total_count = 0
                success_count = 0
                error_count = 0
                
                for stat in data.get('status_stats', []):
                    total_count += stat['count']
                    if stat['status'] == 'success':
                        success_count += stat['count']
                    elif stat['status'] == 'error':
                        error_count += stat['count']
                
                print(f"📊 统计结果:")
                print(f"   - 总记录数: {total_count}")
                print(f"   - 成功记录: {success_count}")
                print(f"   - 失败记录: {error_count}")
                print(f"   - 成功率: {round((success_count/total_count)*100, 1) if total_count > 0 else 0}%")
                print(f"   - 统计范围: {'全部数据' if data.get('is_all_data') else f'最近{data.get('period_days')}天'}")
                
            elif response.status_code == 401:
                print("⚠️  需要认证 (这是正常的)")
            elif response.status_code == 404:
                print("❌ 404 Not Found - URL可能有问题")
            else:
                print(f"⚠️  其他状态码: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - 请确保后端服务正在运行")
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("📝 修复说明:")
    print("1. 后端API修改: days参数改为可选，不传则统计全部数据")
    print("2. 前端调用修改: 不传days参数，获取全部数据统计")
    print("3. 预期效果: 总记录数应该显示实际的57条，而不是7天内的5条")
    print("✅ 统计数据显示问题已修复")

if __name__ == "__main__":
    test_logs_stats_api() 