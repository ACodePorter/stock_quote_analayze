#!/usr/bin/env python3
"""
测试指数行情排序逻辑
确保空值（显示为"-"的数据）排在最后
"""

import requests
import json
from typing import List, Dict, Any

def test_index_sorting():
    """测试指数行情排序功能"""
    base_url = "http://localhost:8000"
    
    # 测试不同的排序字段
    sort_fields = [
        "pct_chg",      # 涨跌幅
        "price",        # 点位
        "change",       # 涨跌
        "high",         # 最高
        "low",          # 最低
        "open",         # 开盘
        "pre_close",    # 昨收
        "volume",       # 成交量
        "amount",       # 成交额
        "amplitude",    # 振幅
        "turnover",     # 换手率
        "pe",           # 市盈率
        "volume_ratio"  # 量比
    ]
    
    print("🔍 测试指数行情排序功能...")
    print("=" * 60)
    
    for sort_field in sort_fields:
        print(f"\n📊 测试排序字段: {sort_field}")
        print("-" * 40)
        
        try:
            # 请求数据
            url = f"{base_url}/api/quotes/indices"
            params = {
                "page": 1,
                "page_size": 10,
                "sort_by": sort_field
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    quotes = data.get("data", [])
                    total = data.get("total", 0)
                    
                    print(f"✅ 获取到 {len(quotes)} 条数据 (总计: {total})")
                    
                    # 检查前5条数据
                    print("前5条数据:")
                    for i, quote in enumerate(quotes[:5]):
                        value = quote.get(sort_field, "N/A")
                        display_value = value if value is not None else "-"
                        print(f"  {i+1}. {quote.get('code')} - {quote.get('name')}: {display_value}")
                    
                    # 检查后5条数据
                    if len(quotes) > 5:
                        print("后5条数据:")
                        for i, quote in enumerate(quotes[-5:]):
                            value = quote.get(sort_field, "N/A")
                            display_value = value if value is not None else "-"
                            print(f"  {len(quotes)-4+i}. {quote.get('code')} - {quote.get('name')}: {display_value}")
                    
                    # 检查空值分布
                    null_count = sum(1 for quote in quotes if quote.get(sort_field) is None)
                    non_null_count = len(quotes) - null_count
                    
                    print(f"📈 数据分布: 非空值 {non_null_count} 条, 空值 {null_count} 条")
                    
                    # 验证排序逻辑：空值应该在最后
                    if null_count > 0:
                        # 找到第一个空值的位置
                        first_null_index = None
                        for i, quote in enumerate(quotes):
                            if quote.get(sort_field) is None:
                                first_null_index = i
                                break
                        
                        if first_null_index is not None:
                            # 检查第一个空值之后是否还有非空值
                            has_non_null_after_null = False
                            for i in range(first_null_index + 1, len(quotes)):
                                if quote.get(sort_field) is not None:
                                    has_non_null_after_null = True
                                    break
                            
                            if has_non_null_after_null:
                                print(f"❌ 排序错误: 空值后还有非空值 (位置: {first_null_index})")
                            else:
                                print(f"✅ 排序正确: 空值都在最后 (从位置 {first_null_index} 开始)")
                        else:
                            print("✅ 排序正确: 没有空值")
                    else:
                        print("✅ 排序正确: 没有空值")
                        
                else:
                    print(f"❌ API返回失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 测试完成!")

if __name__ == "__main__":
    test_index_sorting()
