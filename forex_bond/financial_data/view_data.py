
import pandas as pd
import os

print("=== 金融数据查看器 | Financial Data Viewer ===\n")

# 汇率数据 | Currency Data
print("【汇率数据历史记录 | Currency Exchange Rate History】")
print("=" * 60)
currency_files = [
    ('usd_cny.csv', '美元/人民币 | USD/CNY'),
    ('gbp_cny.csv', '英镑/人民币 | GBP/CNY'),
    ('usd_gbp.csv', '美元/英镑 | USD/GBP'),
    ('cny_usd.csv', '人民币/美元 | CNY/USD'),
    ('cny_gbp.csv', '人民币/英镑 | CNY/GBP'),
    ('gbp_usd.csv', '英镑/美元 | GBP/USD')
]

for filename, name in currency_files:
    filepath = os.path.join('financial_data', filename)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        print(f"\n{name} ({len(df)} 条记录 | records):")
        print("-" * 40)
        recent = df.tail(5)
        for _, row in recent.iterrows():
            print(f"  {row['timestamp']}  {row['close']:>10.4f}")
        if len(df) > 5:
            print(f"  ... (还有 {len(df)-5} 条更早的记录 | {len(df)-5} more records)")

# 国债数据 | Treasury Data
print("\n\n【国债收益率历史记录 | Treasury Yield History】")
print("=" * 60)
bond_files = [
    ('us_10y.csv', '美国10年期 | US 10Y'),
    ('cn_10y.csv', '中国10年期 | China 10Y'),
    ('uk_10y.csv', '英国10年期 | UK 10Y')
]

for filename, name in bond_files:
    filepath = os.path.join('financial_data', filename)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        print(f"\n{name} ({len(df)} 条记录 | records):")
        print("-" * 40)
        recent = df.tail(5)
        for _, row in recent.iterrows():
            print(f"  {row['timestamp']}  {row['close']:>10.3f}%")
        if len(df) > 5:
            print(f"  ... (还有 {len(df)-5} 条更早的记录 | {len(df)-5} more records)")

# 统计信息 | Statistics
print("\n\n【数据统计 | Data Statistics】")
print("=" * 60)
total_files = 0
total_records = 0

for files in [currency_files, bond_files]:
    for filename, _ in files:
        filepath = os.path.join('financial_data', filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            total_files += 1
            total_records += len(df)

print(f"总文件数 | Total files: {total_files}")
print(f"总记录数 | Total records: {total_records}")
print(f"\n最后更新 | Last updated: 2025/07/23")

print("\n数据来源说明 | Data Sources:")
print("━" * 60)
print("主要数据源 | Primary sources:")
print("  • Twelve Data (专业金融数据 API)")
print("  • Yahoo Finance")
print("  • Exchange Rate API")
print("\n备用数据源 | Backup sources:")
print("  • 东方财富 (中国国债)")
print("  • Investing.com")
print("\nAPI 提供: Twelve Data")
print("每日限额: 800 次请求")
