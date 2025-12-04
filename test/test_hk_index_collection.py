"""
测试港股指数实时行情采集功能
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend_core.data_collectors.akshare.hk_index_realtime import HKIndexRealtimeCollector
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_hk_index_collection():
    """测试港股指数采集"""
    print("=" * 60)
    print("测试港股指数实时行情采集功能")
    print("=" * 60)
    
    # 创建采集器
    collector = HKIndexRealtimeCollector()
    
    # 执行采集
    print("\n开始采集港股指数数据...")
    result = collector.collect_realtime_quotes()
    
    if result:
        print(f"\n✓ 采集成功！共采集 {len(result)} 条港股指数数据\n")
        print("-" * 60)
        print(f"{'指数代码':<10} {'指数名称':<20} {'最新价':<10} {'涨跌幅(%)':<10}")
        print("-" * 60)
        for item in result:
            code = item.get('code', 'N/A')
            name = item.get('name', 'N/A')
            price = item.get('price', 0)
            pct_chg = item.get('pct_chg', 0)
            print(f"{code:<10} {name:<20} {price:<10.2f} {pct_chg:<10.2f}")
        print("-" * 60)
    else:
        print("\n✗ 采集失败！")
        return False
    
    return True

if __name__ == '__main__':
    success = test_hk_index_collection()
    if success:
        print("\n测试通过！港股指数采集功能正常。")
    else:
        print("\n测试失败！请检查错误日志。")
        sys.exit(1)
