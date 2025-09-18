#!/usr/bin/env python3
"""
测试自选股数据库查询修复
验证数据库查询是否能正确获取最新交易日期的行情数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置环境变量
os.environ['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from backend_api.database import get_db
from backend_api.models import StockRealtimeQuote, Watchlist
from sqlalchemy.orm import Session
import pandas as pd
from sqlalchemy import text

def test_latest_trade_date_query():
    """测试获取最新交易日期"""
    print("🧪 测试获取最新交易日期...")
    
    db = next(get_db())
    try:
        # 查询最新交易日期
        latest_date_result = pd.read_sql_query("""
            SELECT MAX(trade_date) as latest_date 
            FROM stock_realtime_quote 
            WHERE change_percent IS NOT NULL AND change_percent != 0
        """, db.bind)
        
        if latest_date_result.empty or latest_date_result.iloc[0]['latest_date'] is None:
            print("❌ 未找到有效的交易日期数据")
            return None
        
        latest_trade_date = latest_date_result.iloc[0]['latest_date']
        print(f"✅ 最新交易日期: {latest_trade_date}")
        return latest_trade_date
        
    except Exception as e:
        print(f"❌ 查询最新交易日期失败: {str(e)}")
        return None
    finally:
        db.close()

def test_stock_realtime_quote_structure():
    """测试StockRealtimeQuote表结构"""
    print("🧪 测试StockRealtimeQuote表结构...")
    
    db = next(get_db())
    try:
        # 检查表结构
        result = pd.read_sql_query("PRAGMA table_info(stock_realtime_quote)", db.bind)
        print("📋 表结构:")
        for _, row in result.iterrows():
            print(f"  - {row['name']}: {row['type']} {'(PK)' if row['pk'] else ''}")
        
        # 检查是否有trade_date字段
        has_trade_date = 'trade_date' in result['name'].values
        print(f"✅ 包含trade_date字段: {has_trade_date}")
        
        return has_trade_date
        
    except Exception as e:
        print(f"❌ 检查表结构失败: {str(e)}")
        return False
    finally:
        db.close()

def test_watchlist_query_with_date():
    """测试自选股查询（带交易日期过滤）"""
    print("🧪 测试自选股查询（带交易日期过滤）...")
    
    db = next(get_db())
    try:
        # 获取最新交易日期
        latest_trade_date = test_latest_trade_date_query()
        if not latest_trade_date:
            return False
        
        # 查询自选股数据
        watchlist_items = db.query(Watchlist.stock_code, Watchlist.stock_name).limit(3).all()
        if not watchlist_items:
            print("⚠️ 没有自选股数据，创建测试数据...")
            # 创建测试自选股
            test_watchlist = Watchlist(
                user_id=1,
                stock_code="000001",
                stock_name="平安银行",
                group_name="default"
            )
            db.add(test_watchlist)
            db.commit()
            watchlist_items = [(test_watchlist.stock_code, test_watchlist.stock_name)]
        
        codes = [item[0] for item in watchlist_items]
        print(f"📋 测试股票代码: {codes}")
        
        # 查询行情数据（带交易日期过滤）
        quotes = db.query(StockRealtimeQuote).filter(
            StockRealtimeQuote.code.in_(codes),
            StockRealtimeQuote.trade_date == latest_trade_date
        ).all()
        
        print(f"📊 查询到 {len(quotes)} 条行情数据")
        
        for quote in quotes:
            print(f"  - {quote.name} ({quote.code})")
            print(f"    交易日期: {quote.trade_date}")
            print(f"    最新价: {quote.current_price}")
            print(f"    涨跌幅: {quote.change_percent}%")
            print()
        
        return len(quotes) > 0
        
    except Exception as e:
        print(f"❌ 测试自选股查询失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_old_vs_new_query():
    """对比新旧查询方式"""
    print("🧪 对比新旧查询方式...")
    
    db = next(get_db())
    try:
        # 获取最新交易日期
        latest_trade_date = test_latest_trade_date_query()
        if not latest_trade_date:
            return False
        
        # 旧查询方式（不按交易日期过滤）
        print("📊 旧查询方式（不按交易日期过滤）:")
        old_quotes = db.query(StockRealtimeQuote).filter(StockRealtimeQuote.code == "000001").all()
        print(f"  查询到 {len(old_quotes)} 条数据")
        for quote in old_quotes:
            print(f"    - 交易日期: {quote.trade_date}, 价格: {quote.current_price}")
        
        # 新查询方式（按交易日期过滤）
        print("📊 新查询方式（按交易日期过滤）:")
        new_quotes = db.query(StockRealtimeQuote).filter(
            StockRealtimeQuote.code == "000001",
            StockRealtimeQuote.trade_date == latest_trade_date
        ).all()
        print(f"  查询到 {len(new_quotes)} 条数据")
        for quote in new_quotes:
            print(f"    - 交易日期: {quote.trade_date}, 价格: {quote.current_price}")
        
        return True
        
    except Exception as e:
        print(f"❌ 对比查询失败: {str(e)}")
        return False
    finally:
        db.close()

def main():
    """主测试函数"""
    print("=" * 60)
    print("🔧 自选股数据库查询修复测试")
    print("=" * 60)
    
    try:
        # 测试表结构
        print("\n1. 测试表结构...")
        structure_ok = test_stock_realtime_quote_structure()
        
        # 测试最新交易日期查询
        print("\n2. 测试最新交易日期查询...")
        date_ok = test_latest_trade_date_query() is not None
        
        # 测试自选股查询
        print("\n3. 测试自选股查询...")
        query_ok = test_watchlist_query_with_date()
        
        # 对比新旧查询
        print("\n4. 对比新旧查询方式...")
        compare_ok = test_old_vs_new_query()
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结:")
        print(f"表结构正确: {'✅ 是' if structure_ok else '❌ 否'}")
        print(f"交易日期查询: {'✅ 成功' if date_ok else '❌ 失败'}")
        print(f"自选股查询: {'✅ 成功' if query_ok else '❌ 失败'}")
        print(f"查询对比: {'✅ 成功' if compare_ok else '❌ 失败'}")
        
        if all([structure_ok, date_ok, query_ok, compare_ok]):
            print("\n🎉 自选股数据库查询修复成功！")
            print("现在自选股API应该能正确获取最新交易日期的行情数据。")
        else:
            print("\n⚠️ 部分测试失败，需要进一步检查。")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
