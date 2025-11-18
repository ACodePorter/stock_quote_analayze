# 本测试程序用于测试从stock_individual_info_em获取个股信息数据

import sys
import os
import pandas as pd
import akshare as ak
import yfinance as yf

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
    except KeyError as e:
        if 'data' in str(e):
            print("从雪球获取个股信息失败：API 返回数据格式异常，可能需要有效的 token 或 API 访问权限")
            print(f"详细错误：{e}")
        else:
            print(f"从雪球获取个股信息失败：{e}")
    except Exception as e:
        print(f"从雪球获取个股信息失败：{e}")


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


    # stock_board_industry_summary_ths_df = ak.stock_board_industry_summary_ths()
    # print("同花顺-板块-行业板块-一览表，内容如下：")
    # print(stock_board_industry_summary_ths_df)

    # df = ak.stock_board_industry_name_em()
    # print("行业板块名称数据获取成功，内容如下：")
    # print(df)


    # dat = yf.Ticker("SH601127")
    # print(dat.info)
    # print(dat.calendar)
    # print(dat.analyst_price_targets)
    # print(dat.quarterly_income_stmt)
    # print(dat.history(period='1mo'))
    # print(dat.option_chain(dat.options[0]).calls)

    # stock_hk_spot_em_df = ak.stock_hk_spot()
    # print("港股实时行情数据获取成功，内容如下：")
    # print(stock_hk_spot_em_df)

    # 测试从雪球获取港股个股信息
    try:
        stock_individual_basic_info_hk_xq_df = ak.stock_individual_basic_info_hk_xq(symbol="00700", token=None, timeout=None)
        print("港股个股信息获取成功，内容如下：")
        print(stock_individual_basic_info_hk_xq_df)
    except KeyError as e:
        if 'data' in str(e):
            print("从雪球获取港股个股信息失败：API 返回数据格式异常")
            print("可能的原因：")
            print("1. 需要有效的雪球 token（xq_a_token）")
            print("2. token 已过期，需要重新登录获取")
            print("3. API 访问权限受限")
            print(f"详细错误：{e}")
            print("\n提示：如需使用此功能，请先获取有效的雪球 token 并配置到 akshare 中")
        else:
            print(f"从雪球获取港股个股信息失败：{e}")
    except Exception as e:
        print(f"从雪球获取港股个股信息失败：{e}")


    stock_hk_hist_df = ak.stock_hk_hist(symbol="00700", period='daily', start_date="19700101",end_date="22220101",adjust="")    
    print("港股历史行情数据获取成功，内容如下：")
    print(stock_hk_hist_df)

    stock_hk_daily_hfq_df = ak.stock_hk_daily(symbol="00539", adjust="")
    print("港股每日复权行情数据获取成功，内容如下：")
    print(stock_hk_daily_hfq_df)

    stock_hk_spot_df = ak.stock_hk_spot()
    print("港股实时行情数据获取成功，内容如下：")
    print(stock_hk_spot_df)

    stock_hk_spot_em_df = ak.stock_hk_spot_em()
    print("港股实时行情数据获取成功，内容如下：")
    print(stock_hk_spot_em_df)

if __name__ == "__main__":
    main()

