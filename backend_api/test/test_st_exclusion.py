"""
测试低九策略是否正确排除ST股票
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入数据库配置
try:
    from database import get_db, engine
    print("✓ 成功导入数据库配置")
except ImportError:
    print("✗ 无法导入数据库配置，请确保在backend_api目录下运行")
    sys.exit(1)

def test_st_stock_exclusion():
    """测试ST股票排除功能"""
    
    print("=" * 60)
    print("测试低九策略 - ST股票排除功能")
    print("=" * 60)
    
    # 创建数据库会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 1. 查询所有A股数量（不排除ST）
        all_stocks_query = db.execute(text("""
            SELECT COUNT(*) as total
            FROM stock_basic_info 
            WHERE LENGTH(code) = 6
        """))
        all_stocks_count = all_stocks_query.fetchone()[0]
        
        # 2. 查询排除ST后的股票数量
        non_st_stocks_query = db.execute(text("""
            SELECT COUNT(*) as total
            FROM stock_basic_info 
            WHERE LENGTH(code) = 6
            AND name NOT LIKE '%ST%'
        """))
        non_st_stocks_count = non_st_stocks_query.fetchone()[0]
        
        # 3. 查询ST股票数量
        st_stocks_query = db.execute(text("""
            SELECT COUNT(*) as total
            FROM stock_basic_info 
            WHERE LENGTH(code) = 6
            AND name LIKE '%ST%'
        """))
        st_stocks_count = st_stocks_query.fetchone()[0]
        
        # 4. 查询一些ST股票示例
        st_examples_query = db.execute(text("""
            SELECT code, name
            FROM stock_basic_info 
            WHERE LENGTH(code) = 6
            AND name LIKE '%ST%'
            ORDER BY code
            LIMIT 10
        """))
        st_examples = st_examples_query.fetchall()
        
        # 输出结果
        print(f"\n📊 统计结果:")
        print(f"  全部A股数量: {all_stocks_count:,} 只")
        print(f"  非ST股票数量: {non_st_stocks_count:,} 只")
        print(f"  ST股票数量: {st_stocks_count:,} 只")
        print(f"  排除比例: {(st_stocks_count/all_stocks_count*100):.2f}%")
        
        print(f"\n📋 ST股票示例（前10只）:")
        for code, name in st_examples:
            print(f"  {code} - {name}")
        
        # 验证
        print(f"\n✅ 验证结果:")
        if all_stocks_count == non_st_stocks_count + st_stocks_count:
            print(f"  ✓ 数量验证通过: {all_stocks_count} = {non_st_stocks_count} + {st_stocks_count}")
        else:
            print(f"  ✗ 数量验证失败")
        
        if st_stocks_count > 0:
            print(f"  ✓ 成功识别 {st_stocks_count} 只ST股票")
        else:
            print(f"  ⚠ 未找到ST股票（可能数据库中没有ST股票）")
        
        print(f"\n💡 低九策略将排除这 {st_stocks_count} 只ST股票")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_st_stock_exclusion()
