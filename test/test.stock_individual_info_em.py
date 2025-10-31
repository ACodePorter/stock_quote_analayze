# 本测试程序用于测试从stock_individual_info_em获取个股信息数据

import sys
import os
import pandas as pd
import akshare as ak

# 假设stock_individual_info_em函数在backend_core/data_collectors/akshare/stock_individual_info_em.py中
# 为了便于测试，临时加入backend_core到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



def main():
    print("开始测试 stock_individual_info_em 获取数据...")
    try:
        df = ak.stock_individual_info_em(symbol='603667')
        print("数据获取成功，前5行如下：")
        print(df.head())
        print("完整数据如下：")
        print(df)
    except Exception as e:
        print("获取数据失败：", e)

        
    # 测试从雪球获取个股信息
    try:
        xq_df = ak.stock_individual_basic_info_xq(symbol="SH601127")
        print("雪球个股信息获取成功，内容如下：")
        print(xq_df)
    except Exception as e:
        print("从雪球获取个股信息失败：", e)


    #stock_zh_index_spot_sina_df = ak.stock_zh_index_spot_sina()
    #print("新浪指数数据获取成功，内容如下：")
    #print(stock_zh_index_spot_sina_df)

    industry_board_name_df = ak.stock_board_industry_name_ths() 
    print("行业板块名称数据获取成功，内容如下：")
    print(industry_board_name_df)


    # 测试同花顺-板块-行业板块-指数日频率数据接口
    # 此接口用于获取某行业板块在指定日期范围内的指数日线数据
    # industry_board_index_daily_df = ak.stock_board_industry_index_ths(symbol="半导体", start_date="20251029", end_date="20251031")
    # print("同花顺-板块-行业板块-指数日频率数据，内容如下：")
    # print(industry_board_index_daily_df)


    stock_board_industry_summary_ths_df = ak.stock_board_industry_summary_ths()
    print("同花顺-板块-行业板块-一览表，内容如下：")
    print(stock_board_industry_summary_ths_df)

    df = ak.stock_board_industry_name_em()
    print("行业板块名称数据获取成功，内容如下：")
    print(df)

if __name__ == "__main__":
    main()

