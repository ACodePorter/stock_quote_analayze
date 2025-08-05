#!/usr/bin/env python3
"""
简单测试operation_logs API
不依赖数据库连接，只测试API响应
"""

import requests
import json

def test_operation_logs_api():
    """测试operation_logs API"""
    
    print("🔍 简单测试operation_logs API")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # 测试端点
    endpoints = [
        "/api/admin/logs/tables",
        "/api/admin/logs/query/operation?page=1&page_size=5",
        "/api/admin/logs/stats/operation"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 测试URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ 状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 请求成功")
                
                if endpoint.endswith("/tables"):
                    tables = data.get('tables', [])
                    print(f"📊 可用表数量: {len(tables)}")
                    for table in tables:
                        print(f"   - {table['key']}: {table['table_name']} ({table['display_name']})")
                
                elif endpoint.endswith("/stats/operation"):
                    print(f"📊 统计信息:")
                    print(f"   - 表名: {data.get('table_name')}")
                    print(f"   - 统计范围: {'全部数据' if data.get('is_all_data') else f'最近{data.get('period_days')}天'}")
                    print(f"   - 状态统计: {data.get('status_stats', [])}")
                
                else:
                    pagination = data.get('pagination', {})
                    print(f"📊 查询结果:")
                    print(f"   - 总记录数: {pagination.get('total_count', 0)}")
                    print(f"   - 当前页: {pagination.get('page', 0)}")
                    print(f"   - 总页数: {pagination.get('total_pages', 0)}")
                    print(f"   - 数据条数: {len(data.get('data', []))}")
                    
                    # 显示前几条数据
                    for i, log in enumerate(data.get('data', [])[:3], 1):
                        print(f"   记录{i}: ID={log.get('id')}, 类型={log.get('operation_type')}, 状态={log.get('status')}")
            
            elif response.status_code == 500:
                print("❌ 500 内部服务器错误")
                try:
                    error_data = response.json()
                    print(f"❌ 错误详情: {error_data}")
                except:
                    print(f"❌ 错误响应: {response.text[:200]}...")
            
            elif response.status_code == 401:
                print("⚠️  需要认证 (这是正常的)")
            
            elif response.status_code == 404:
                print("❌ 404 Not Found - 端点不存在")
            
            else:
                print(f"⚠️  其他状态码: {response.status_code}")
                print(f"响应内容: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - 请确保后端服务正在运行")
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    print("\n" + "=" * 50)
    print("📝 问题诊断:")
    print("1. 如果/tables返回成功，说明API基本正常")
    print("2. 如果/query/operation返回500错误，可能是:")
    print("   - operation_logs表不存在")
    print("   - 表字段结构与API期望不匹配")
    print("   - 数据库连接问题")
    print("3. 如果/stats/operation返回500错误，原因同上")
    print("✅ 测试完成")

if __name__ == "__main__":
    test_operation_logs_api() 