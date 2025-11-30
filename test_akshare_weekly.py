import akshare as ak
import pandas as pd
from datetime import datetime

try:
    print("Testing ak.stock_zh_a_hist with period='weekly'...")
    # Test with a known stock code, e.g., 000001 (Ping An Bank)
    df = ak.stock_zh_a_hist(symbol="000001", period="weekly", start_date="20230101", end_date="20231231", adjust="qfq")
    if not df.empty:
        print("Success! Weekly data fetched.")
        print(df.head())
        print(df.columns)
    else:
        print("Returned empty dataframe.")
except Exception as e:
    print(f"Error: {e}")
