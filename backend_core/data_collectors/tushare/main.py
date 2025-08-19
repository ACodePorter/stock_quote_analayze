import argparse
from backend_core.data_collectors.tushare.realtime import RealtimeQuoteCollector
from backend_core.data_collectors.tushare.historical import HistoricalQuoteCollector
from backend_core.data_collectors.tushare.index import IndexQuoteCollector
from backend_core.data_collectors.tushare.historical_import_from_file import HistoricalQuoteImportFromFileCollector

def main():
    parser = argparse.ArgumentParser(description='Tushare数据采集工具')
    parser.add_argument('--type', choices=['realtime', 'historical', 'index', 'historical_import_from_file'], required=True, help='采集类型')
    parser.add_argument('--date', type=str, help='历史行情采集日期，格式YYYYMMDD')
    parser.add_argument('--file_type', type=str, help='文件类型，csv或txt')
    args = parser.parse_args()
    if args.type == 'realtime':
        collector = RealtimeQuoteCollector()
        collector.collect_quotes()
    elif args.type == 'historical':
        if not args.date:
            print('请指定--date参数')
            return
        collector = HistoricalQuoteCollector()
        collector.collect_historical_quotes(args.date)
    elif args.type == 'index':
        collector = IndexQuoteCollector()
        collector.collect_index_quotes()
    elif args.type == 'historical_import_from_file':
        if not args.date:
            print('请指定--date参数')
            return
        if not args.file_type:
            print('请指定--file_type参数')
            return
        collector = HistoricalQuoteImportFromFileCollector()
        collector.collect_historical_quotes(args.date, args.file_type)

if __name__ == '__main__':
    main()
