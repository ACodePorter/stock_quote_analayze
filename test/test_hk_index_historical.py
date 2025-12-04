"""
测试港股指数历史行情采集功能
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend_core.data_collectors.akshare.hk_index_historical_collector import HKIndexHistoricalCollector
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_hk_index_historical_collection():
    """测试港股指数历史行情采集"""
    print("=" * 60)
    print("测试港股指数历史行情采集功能")
    print("=" * 60)
    
    # 创建采集器
    collector = HKIndexHistoricalCollector()
    
    # 测试采集当天数据
    print("\n1. 测试采集当天历史行情数据...")
    result = collector.collect_daily_to_historical()
    
    if result.get('success', 0) > 0:
        print(f"\n✓ 采集成功！")
        print(f"  - 交易日期: {result.get('trade_date', 'N/A')}")
        print(f"  - 成功: {result.get('success', 0)} 条")
        print(f"  - 失败: {result.get('failed', 0)} 条")
        print(f"  - 消息: {result.get('message', '')}")
    else:
        print(f"\n✗ 采集失败！")
        print(f"  - 消息: {result.get('message', '未知错误')}")
        if 'error' in result:
            print(f"  - 错误: {result['error']}")
    
    print("\n" + "=" * 60)
    
    # 测试采集指定日期数据
    print("\n2. 测试采集指定日期历史行情数据...")
    from datetime import datetime, timedelta
    
    # 获取昨天的日期
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"   采集日期: {yesterday}")
    
    result2 = collector.collect_daily_to_historical(yesterday)
    
    if result2.get('success', 0) > 0:
        print(f"\n✓ 采集成功！")
        print(f"  - 交易日期: {result2.get('trade_date', 'N/A')}")
        print(f"  - 成功: {result2.get('success', 0)} 条")
        print(f"  - 失败: {result2.get('failed', 0)} 条")
    else:
        print(f"\n✗ 采集失败或无数据")
        print(f"  - 消息: {result2.get('message', '')}")
    
    print("\n" + "=" * 60)
    
    return result.get('success', 0) > 0

if __name__ == '__main__':
    success = test_hk_index_historical_collection()
    
    if success:
        print("\n✓ 测试通过！港股指数历史行情采集功能正常。")
    else:
        print("\n⚠ 测试完成，请检查日志了解详情。")
