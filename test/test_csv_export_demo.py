#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
演示历史行情导出CSV格式化效果
"""

import csv
import io

def demo_csv_export():
    """演示CSV导出格式化效果"""
    
    # 从history_api.py中复制的格式化函数
    def format_volume(volume):
        """格式化成交量为万手"""
        if volume is None:
            return '-'
        vol = float(volume)
        if vol >= 10000:
            return f"{vol / 10000:.2f}万手"
        return f"{vol:.0f}手"
    
    def format_amount(amount):
        """格式化成交额为亿"""
        if amount is None:
            return '-'
        amt = float(amount)
        return f"{amt / 100000000:.2f}亿"
    
    def format_percent(value):
        """格式化百分比"""
        if value is None:
            return '-'
        return f"{float(value):.2f}%"
    
    def format_price(value):
        """格式化价格"""
        if value is None:
            return '-'
        return f"{float(value):.2f}"
    
    print("📋 演示历史行情导出CSV格式化效果\n")
    
    # 模拟数据（根据您提供的Excel图片数据）
    sample_data = [
        ("300475", "聚光科技", "2025-09-11", 52.85, 64.51, 64.51, 52.84, 572458, 3391296600, 20, 10.75, 12.89),
        ("300475", "聚光科技", "2025-09-10", 53.52, 53.76, 54.6, 52.5, 867340, 1965836800, 0.49, 0.26, 8.27),
        ("300475", "聚光科技", "2025-09-09", 49.99, 53.5, 55.43, 48.8, 572197, 3012156400, 6.09, 3.07, 12.88),
        ("300475", "聚光科技", "2025-09-08", 43.99, 50.43, 51.5, 43.6, 568629, 2683321000, 17.31, 7.44, 12.76),
    ]
    
    # 创建CSV内容
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入CSV头部（修改后的格式）
    headers = [
        "股票代码", "股票名称", "日期", "开盘", "收盘", "最高", "最低",
        "成交量(万手)", "成交额(亿)", "涨跌幅%", "涨跌额", "换手率%"
    ]
    writer.writerow(headers)
    
    # 写入格式化后的数据
    for row in sample_data:
        formatted_row = [
            row[0], row[1], row[2],  # 股票代码、名称、日期
            format_price(row[3]),    # 开盘
            format_price(row[4]),    # 收盘
            format_price(row[5]),    # 最高
            format_price(row[6]),    # 最低
            format_volume(row[7]),   # 成交量(万手)
            format_amount(row[8]),   # 成交额(亿)
            format_percent(row[9]),  # 涨跌幅%
            format_price(row[10]),   # 涨跌额
            format_percent(row[11])  # 换手率%
        ]
        writer.writerow(formatted_row)
    
    # 显示CSV内容
    csv_content = output.getvalue()
    print("生成的CSV内容:")
    print("=" * 120)
    print(csv_content)
    print("=" * 120)
    
    # 解析并以表格形式显示
    output.seek(0)
    csv_reader = csv.reader(output)
    
    print("\n📊 表格形式显示:")
    for i, row in enumerate(csv_reader):
        if i == 0:
            # 头部
            print("| " + " | ".join(f"{cell:^12}" for cell in row) + " |")
            print("|" + "|".join("-" * 14 for _ in row) + "|")
        else:
            # 数据行
            print("| " + " | ".join(f"{cell:^12}" for cell in row) + " |")
    
    print(f"\n✅ 格式化完成！")
    print(f"📋 主要改进:")
    print(f"   • 成交量单位：显示为 '万手'（如：57.24万手）")
    print(f"   • 成交额单位：统一显示为 '亿'（如：33.91亿）")
    print(f"   • 涨跌幅/换手率：显示百分比符号（如：20.00%）")
    print(f"   • 价格数据：保留两位小数")

if __name__ == "__main__":
    demo_csv_export()