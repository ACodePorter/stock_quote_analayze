#!/usr/bin/env python3
"""
测试独立的系统操作日志功能
验证独立API和前端页面
"""

import requests
import json

def test_operation_logs_standalone():
    """测试独立的系统操作日志功能"""
    
    print("🔍 测试独立的系统操作日志功能")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 测试端点
    endpoints = [
        "/api/admin/operation-logs/info",
        "/api/admin/operation-logs/query?page=1&page_size=5",
        "/api/admin/operation-logs/stats",
        "/api/admin/operation-logs/recent?limit=3"
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
                
                if endpoint.endswith("/info"):
                    print(f"📊 表信息:")
                    print(f"   - 表名: {data.get('table_name')}")
                    print(f"   - 显示名: {data.get('display_name')}")
                    print(f"   - 字段: {data.get('columns')}")
                    print(f"   - 描述: {data.get('description')}")
                
                elif endpoint.endswith("/stats"):
                    print(f"📊 统计信息:")
                    print(f"   - 表名: {data.get('table_name')}")
                    print(f"   - 统计范围: {'全部数据' if data.get('is_all_data') else f'最近{data.get('period_days')}天'}")
                    print(f"   - 状态统计: {data.get('status_stats', [])}")
                    print(f"   - 日志类型统计: {data.get('log_type_stats', [])}")
                
                elif endpoint.endswith("/recent"):
                    print(f"📊 最近记录:")
                    print(f"   - 表名: {data.get('table_name')}")
                    print(f"   - 记录数: {len(data.get('data', []))}")
                    
                    # 显示前几条记录
                    for i, log in enumerate(data.get('data', [])[:3], 1):
                        print(f"   记录{i}: ID={log.get('id')}, 类型={log.get('log_type', 'N/A')}, 状态={log.get('log_status', 'N/A')}")
                
                else:
                    pagination = data.get('pagination', {})
                    print(f"📊 查询结果:")
                    print(f"   - 表名: {data.get('table_name')}")
                    print(f"   - 总记录数: {pagination.get('total_count', 0)}")
                    print(f"   - 当前页: {pagination.get('page', 0)}")
                    print(f"   - 总页数: {pagination.get('total_pages', 0)}")
                    print(f"   - 数据条数: {len(data.get('data', []))}")
                    
                    # 显示前几条数据
                    for i, log in enumerate(data.get('data', [])[:3], 1):
                        print(f"   记录{i}: ID={log.get('id')}, 类型={log.get('log_type', 'N/A')}, 状态={log.get('log_status', 'N/A')}, 时间={log.get('log_time', 'N/A')}")
            
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
    
    print("\n" + "=" * 60)
    print("📝 独立实现说明:")
    print("1. 后端独立API: /api/admin/operation-logs/*")
    print("2. 前端独立页面: admin/operation_logs.html")
    print("3. 直接显示operation_logs表字段内容")
    print("4. 无需字段映射，直接使用实际字段名")
    print("5. 独立的JavaScript模块: admin/js/operation_logs.js")
    print("✅ 独立实现测试完成")

def test_frontend_page():
    """测试前端页面访问"""
    
    print("\n🌐 测试前端页面访问")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    page_url = f"{base_url}/admin/operation_logs.html"
    
    print(f"📡 页面URL: {page_url}")
    
    try:
        response = requests.get(page_url, timeout=10)
        print(f"✅ 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 页面访问成功")
            print("📝 页面内容长度: {} 字符".format(len(response.text)))
            
            # 检查关键元素
            content = response.text
            if "系统操作日志" in content:
                print("✅ 页面标题正确")
            if "operation_logs.js" in content:
                print("✅ JavaScript文件引用正确")
            if "operationLogsTable" in content:
                print("✅ 表格ID正确")
        else:
            print(f"❌ 页面访问失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 页面访问失败: {e}")

if __name__ == "__main__":
    test_operation_logs_standalone()
    test_frontend_page() 