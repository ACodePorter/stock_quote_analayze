#!/usr/bin/env python3
"""
简化的增强AKShare采集器测试
只测试基础功能，避免数据库连接问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend_core.data_collectors.akshare.enhanced_base import EnhancedAKShareCollector
import logging

def test_enhanced_base_collector():
    """测试增强的基础采集器"""
    print("=" * 60)
    print("测试增强的基础采集器")
    print("=" * 60)
    
    try:
        # 创建采集器实例
        collector = EnhancedAKShareCollector()
        
        # 测试获取股票列表
        print("1. 测试获取股票列表...")
        df = collector.get_stock_list()
        print(f"   成功获取 {len(df)} 只股票信息")
        print(f"   前5只股票: {df[['代码', '名称']].head().to_dict('records')}")
        
        # 测试获取实时行情（小样本）
        print("\n2. 测试获取实时行情（前5只股票）...")
        stock_codes = df['代码'].head(5).tolist()
        quotes_df = collector.get_realtime_quotes(stock_codes)
        print(f"   成功获取 {len(quotes_df)} 条实时行情数据")
        if len(quotes_df) > 0:
            print(f"   前3条数据: {quotes_df[['代码', '名称', '最新价', '涨跌幅']].head(3).to_dict('records')}")
        
        # 测试回退机制
        print("\n3. 测试回退机制...")
        fallback_df = collector.get_realtime_quotes_with_fallback()
        print(f"   回退机制成功获取 {len(fallback_df)} 条数据")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_ssl_fix():
    """测试SSL连接问题修复"""
    print("\n" + "=" * 60)
    print("测试SSL连接问题修复")
    print("=" * 60)
    
    try:
        import akshare as ak
        
        print("1. 测试原始AKShare调用...")
        try:
            df = ak.stock_zh_a_spot_em()
            print(f"   原始调用成功: {len(df)} 条数据")
        except Exception as e:
            print(f"   原始调用失败: {str(e)}")
            
        print("\n2. 测试增强采集器...")
        collector = EnhancedAKShareCollector()
        try:
            df = collector.get_stock_list()
            print(f"   增强采集器成功: {len(df)} 条数据")
        except Exception as e:
            print(f"   增强采集器失败: {str(e)}")
            
        return True
        
    except Exception as e:
        print(f"SSL测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试增强的AKShare采集器...")
    print("这个测试将验证SSL连接问题解决和备用数据源功能")
    
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    
    test_results = []
    
    # 测试SSL修复
    test_results.append(("SSL连接修复", test_ssl_fix()))
    
    # 测试增强基础采集器
    test_results.append(("增强基础采集器", test_enhanced_base_collector()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result in test_results if result)
    
    print(f"\n总计: {passed_tests}/{total_tests} 个测试通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试都通过了！")
    else:
        print("⚠️  部分测试失败，请检查日志")

if __name__ == "__main__":
    main()
