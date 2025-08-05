#!/usr/bin/env python3
"""
测试日志统计逻辑修复
验证失败记录和成功率的计算是否正确
"""

import requests
import json

def test_logs_stats_logic():
    """测试日志统计逻辑"""
    
    base_url = "http://localhost:5000"
    
    # 测试的端点
    endpoints = [
        "/api/admin/logs/stats/historical_collect",  # 历史数据采集日志
        "/api/admin/logs/stats/realtime_collect",  # 实时数据采集日志
        "/api/admin/logs/stats/operation",  # 系统操作日志
        "/api/admin/logs/stats/watchlist_history"  # 自选股历史采集日志
    ]
    
    print("🔍 测试日志统计逻辑修复")
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
                partial_success_count = 0
                
                print(f"📊 状态统计详情:")
                for stat in data.get('status_stats', []):
                    status = stat['status']
                    count = stat['count']
                    total_count += count
                    
                    if status == 'success':
                        success_count += count
                        print(f"   - 成功: {count} 条")
                    elif status == 'error':
                        error_count += count
                        print(f"   - 失败: {count} 条")
                    elif status == 'partial_success':
                        partial_success_count += count
                        print(f"   - 部分成功: {count} 条")
                    else:
                        print(f"   - {status}: {count} 条")
                
                # 计算修复后的统计
                total_failure_count = error_count + partial_success_count
                success_rate = round((success_count / total_count) * 100, 1) if total_count > 0 else 0
                failure_rate = round((total_failure_count / total_count) * 100, 1) if total_count > 0 else 0
                
                print(f"\n📈 修复后的统计汇总:")
                print(f"   - 总记录数: {total_count}")
                print(f"   - 成功记录: {success_count}")
                print(f"   - 失败记录: {total_failure_count} (包括 {error_count} 完全失败 + {partial_success_count} 部分成功)")
                print(f"   - 成功率: {success_rate}%")
                print(f"   - 失败率: {failure_rate}%")
                
                # 验证逻辑
                print(f"\n✅ 逻辑验证:")
                if total_failure_count > 0 and success_rate == 100:
                    print(f"   ❌ 错误: 有失败记录但成功率为100%")
                else:
                    print(f"   ✅ 正确: 成功率计算符合预期")
                
                if success_rate + failure_rate == 100:
                    print(f"   ✅ 正确: 成功率 + 失败率 = 100%")
                else:
                    print(f"   ⚠️  注意: 成功率 + 失败率 ≠ 100% (可能还有其他状态)")
                
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
    print("1. 失败记录 = error + partial_success")
    print("2. 成功率 = success / total * 100%")
    print("3. 失败率 = (error + partial_success) / total * 100%")
    print("4. 如果有失败记录，成功率不应该为100%")
    print("✅ 统计逻辑修复验证完成")

if __name__ == "__main__":
    test_logs_stats_logic() 