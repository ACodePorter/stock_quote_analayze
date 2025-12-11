"""
测试港股实时行情接口返回的字段名
用于排查为什么只采集到59条数据
"""
import akshare as ak
import pandas as pd

def test_stock_hk_spot():
    """测试 stock_hk_spot 接口"""
    print("=" * 60)
    print("测试 stock_hk_spot 接口")
    print("=" * 60)
    try:
        df = ak.stock_hk_spot()
        print(f"数据行数: {len(df)}")
        print(f"数据列名: {list(df.columns)}")
        print(f"\n前5行数据:")
        print(df.head(5))
        print(f"\n第一行的所有字段:")
        if len(df) > 0:
            first_row = df.iloc[0]
            for col in df.columns:
                print(f"  {col}: {first_row[col]}")
    except Exception as e:
        print(f"调用 stock_hk_spot 失败: {e}")
        import traceback
        traceback.print_exc()

def test_stock_hk_spot_em():
    """测试 stock_hk_spot_em 接口"""
    print("\n" + "=" * 60)
    print("测试 stock_hk_spot_em 接口")
    print("=" * 60)
    try:
        df = ak.stock_hk_spot_em()
        print(f"数据行数: {len(df)}")
        print(f"数据列名: {list(df.columns)}")
        print(f"\n前5行数据:")
        print(df.head(5))
        print(f"\n第一行的所有字段:")
        if len(df) > 0:
            first_row = df.iloc[0]
            for col in df.columns:
                print(f"  {col}: {first_row[col]}")
        
        # 检查代码字段的可能名称
        print(f"\n检查代码字段:")
        possible_code_fields = ['代码', '股票代码', 'symbol', 'code', '股票编码']
        for field in possible_code_fields:
            if field in df.columns:
                print(f"  找到字段 '{field}': {df[field].iloc[0] if len(df) > 0 else 'N/A'}")
            else:
                print(f"  未找到字段 '{field}'")
        
        # 检查名称字段的可能名称
        print(f"\n检查名称字段:")
        possible_name_fields = ['中文名称', '名称', 'name', '股票名称', '股票名']
        for field in possible_name_fields:
            if field in df.columns:
                print(f"  找到字段 '{field}': {df[field].iloc[0] if len(df) > 0 else 'N/A'}")
            else:
                print(f"  未找到字段 '{field}'")
                
    except Exception as e:
        print(f"调用 stock_hk_spot_em 失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stock_hk_spot()
    test_stock_hk_spot_em()

