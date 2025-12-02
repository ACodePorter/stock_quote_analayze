---
description: How to start the background data collection service
---
To ensure the stock analysis system has up-to-date and complete market data, you need to run the background data collection service.

1. Open a new terminal window.
2. Navigate to the project root directory:
   ```powershell
   cd e:\wangxw\股票分析软件\编码\stock_quote_analayze
   ```
3. Run the startup script:
   ```powershell
   python start_backend_core.py
   ```
   
This service will:
- Collect real-time quotes for all A-shares during trading hours.
- Collect historical data daily.
- Update news and other information.

Without this service running, the system may rely on stale data or fallback mechanisms which might be slower or less complete.
