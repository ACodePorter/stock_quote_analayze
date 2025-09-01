#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5日涨跌幅计算功能使用示例
演示如何使用5日涨跌幅自动计算功能
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from backend_core.database.db import SessionLocal
from backend_core.data_collectors.tushare.five_day_change_calculator import FiveDayChangeCalculator

def example_1_basic_usage():
    """示例1: 基本使用方法"""
    print("=== 示例1: 基本使用方法 ===")
    
    session = SessionLocal()
    calculator = FiveDayChangeCalculator(session)
    
    try:
        # 获取今日日期
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 查看今日计算状态
        status = calculator.get_calculation_status(today)
        print(f"今日({today})的计算状态:")
        print(f"  总记录数: {status['total_records']}")
        print(f"  已计算记录数: {status['calculated_records']}")
        print(f"  待计算记录数: {status['pending_records']}")
        print(f"  完成率: {status['completion_rate']}%")
        
        # 如果有待计算的记录，执行计算
        if status['pending_records'] > 0:
            print(f"\n开始计算今日的5日涨跌幅...")
            result = calculator.calculate_for_date(today)
            print(f"计算完成:")
            print(f"  总计股票: {result['total']}")
            print(f"  成功计算: {result['success']}")
            print(f"  失败计算: {result['failed']}")
        else:
            print(f"\n今日数据已全部计算完成！")
        
    except Exception as e:
        print(f"示例1执行失败: {e}")
    finally:
        session.close()

def example_2_batch_calculation():
    """示例2: 批量计算"""
    print("\n=== 示例2: 批量计算 ===")
    
    session = SessionLocal()
    calculator = FiveDayChangeCalculator(session)
    
    try:
        # 计算最近7天的数据
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        print(f"开始批量计算日期范围: {start_date} 到 {end_date}")
        result = calculator.calculate_batch_for_date_range(start_date, end_date)
        
        print(f"批量计算完成:")
        print(f"  日期范围: {result['start_date']} 到 {result['end_date']}")
        print(f"  总计日期: {result['total_dates']}")
        print(f"  总计成功: {result['total_success']}")
        print(f"  总计失败: {result['total_failed']}")
        
        if result['total_failed'] > 0:
            print(f"  失败详情:")
            for detail in result['details'][:5]:  # 只显示前5个失败详情
                print(f"    - {detail}")
            if len(result['details']) > 5:
                print(f"    ... 还有 {len(result['details']) - 5} 个失败详情")
        
    except Exception as e:
        print(f"示例2执行失败: {e}")
    finally:
        session.close()

def example_3_status_monitoring():
    """示例3: 状态监控"""
    print("\n=== 示例3: 状态监控 ===")
    
    session = SessionLocal()
    calculator = FiveDayChangeCalculator(session)
    
    try:
        # 监控最近5天的计算状态
        for i in range(5):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            status = calculator.get_calculation_status(date)
            
            print(f"日期 {date}:")
            print(f"  总记录数: {status['total_records']}")
            print(f"  完成率: {status['completion_rate']}%")
            
            if status['completion_rate'] < 100:
                print(f"  ⚠️  需要补充计算")
            else:
                print(f"  ✅ 计算完成")
        
    except Exception as e:
        print(f"示例3执行失败: {e}")
    finally:
        session.close()

def example_4_error_handling():
    """示例4: 错误处理"""
    print("\n=== 示例4: 错误处理 ===")
    
    session = SessionLocal()
    calculator = FiveDayChangeCalculator(session)
    
    try:
        # 尝试计算一个不存在的日期
        invalid_date = "2020-01-01"
        print(f"尝试计算无效日期: {invalid_date}")
        
        result = calculator.calculate_for_date(invalid_date)
        print(f"计算结果: {result}")
        
        # 尝试计算一个未来日期
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"\n尝试计算未来日期: {future_date}")
        
        result = calculator.calculate_for_date(future_date)
        print(f"计算结果: {result}")
        
    except Exception as e:
        print(f"示例4执行失败: {e}")
    finally:
        session.close()

def example_5_performance_test():
    """示例5: 性能测试"""
    print("\n=== 示例5: 性能测试 ===")
    
    session = SessionLocal()
    calculator = FiveDayChangeCalculator(session)
    
    try:
        import time
        
        # 测试单日计算性能
        test_date = datetime.now().strftime("%Y-%m-%d")
        print(f"测试单日计算性能: {test_date}")
        
        start_time = time.time()
        result = calculator.calculate_for_date(test_date)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"执行时间: {execution_time:.2f} 秒")
        print(f"处理记录数: {result['total']}")
        if result['total'] > 0:
            print(f"平均处理速度: {result['total'] / execution_time:.2f} 记录/秒")
        
    except Exception as e:
        print(f"示例5执行失败: {e}")
    finally:
        session.close()

def main():
    """主函数"""
    print("5日涨跌幅计算功能使用示例")
    print("=" * 50)
    
    examples = [
        ("基本使用方法", example_1_basic_usage),
        ("批量计算", example_2_batch_calculation),
        ("状态监控", example_3_status_monitoring),
        ("错误处理", example_4_error_handling),
        ("性能测试", example_5_performance_test),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{i}. {name}")
        try:
            func()
        except Exception as e:
            print(f"示例执行失败: {e}")
    
    print("\n" + "=" * 50)
    print("所有示例执行完成！")
    print("\n使用提示:")
    print("1. 确保数据库连接正常")
    print("2. 确保历史行情数据已采集")
    print("3. 检查日志文件了解详细执行情况")
    print("4. 如有问题，请查看错误日志")

if __name__ == "__main__":
    main()
