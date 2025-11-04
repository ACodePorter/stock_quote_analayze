# 本测试程序用于测试从stock_individual_info_em获取个股信息数据

import sys
import os
import pandas as pd
import akshare as ak
import yfinance as yf

# 假设stock_individual_info_em函数在backend_core/data_collectors/akshare/stock_individual_info_em.py中
# 为了便于测试，临时加入backend_core到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

proxy = 'http://127.0.0.1:9910'
os.environ['HTTP_PROXY'] = proxy
os.environ['HTTPS_PROXY'] = proxy
#yf.set_proxy(proxy)


def main():



    dat = yf.Ticker("TSLA")
    print(dat.info)
    print(dat.calendar)
    print(dat.analyst_price_targets)
    print(dat.quarterly_income_stmt)
    print(dat.history(period='1mo'))
    print(dat.option_chain(dat.options[0]).calls)

if __name__ == "__main__":
    main()

