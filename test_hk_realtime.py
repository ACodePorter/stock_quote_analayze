
import logging
from backend_core.data_collectors.akshare.hk_realtime import HKRealtimeQuoteCollector

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_hk_collection():
    print("Starting HK Realtime Collection Test...")
    collector = HKRealtimeQuoteCollector()
    result = collector.collect_quotes()
    if result:
        print("Test Passed: Successfully collected HK quotes.")
    else:
        print("Test Failed: Failed to collect HK quotes.")

if __name__ == "__main__":
    test_hk_collection()
