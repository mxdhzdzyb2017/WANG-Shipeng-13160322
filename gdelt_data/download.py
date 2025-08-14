import os
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime

# 直接使用同文件夹下的密钥文件 / Use key file from the same directory
key_path = os.path.join(os.path.dirname(__file__), 'bigquery_key.json')
credentials = service_account.Credentials.from_service_account_file(key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

print("=== GDELT 数据下载器 / GDELT Data Downloader ===")
print("正在连接 BigQuery... / Connecting to BigQuery...")

# 获取用户输入 / Get user input
date = input("请输入日期 / Enter date (例如/e.g.: 20150217): ")
output_file = input("请输入保存的文件名 / Enter filename (默认/default: gdelt_data.csv): ").strip()

if not output_file:
    output_file = "gdelt_data.csv"  # 默认文件名 / Default filename
if not output_file.endswith('.csv'):
    output_file += '.csv'

# 查询数据 - 只查询指定的一天 / Query data - only for specified day
query = f"""
SELECT 
    FORMAT_DATE('%Y%m%d', DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(DATEADDED AS STRING)))) as day,
    CASE 
        WHEN Actor1CountryCode = 'CHN' THEN 'CN'
        WHEN Actor1CountryCode = 'GBR' THEN 'UK'
        WHEN Actor1CountryCode = 'USA' THEN 'US'
        WHEN Actor2CountryCode = 'CHN' THEN 'CN'
        WHEN Actor2CountryCode = 'GBR' THEN 'UK'
        WHEN Actor2CountryCode = 'USA' THEN 'US'
    END as country,
    COUNT(*) as news_count,
    AVG(AvgTone) as avg_tone
FROM 
    `gdelt-bq.gdeltv2.events`
WHERE 
    CAST(DATEADDED AS STRING) >= '{date}000000'
    AND CAST(DATEADDED AS STRING) <= '{date}235959'
    AND (
        Actor1CountryCode IN ('CHN', 'GBR', 'USA') OR 
        Actor2CountryCode IN ('CHN', 'GBR', 'USA')
    )
GROUP BY 
    day, country
HAVING 
    country IS NOT NULL
ORDER BY 
    country
"""

print(f"\n正在查询数据... / Querying data...")
print(f"日期 / Date: {date}")

try:
    # 执行查询 / Execute query
    query_job = client.query(query)
    new_df = query_job.to_dataframe()
    
    if new_df.empty:
        print(f"\n未找到 {date} 的数据 / No data found for {date}")
        print("提示 / Tips：")
        print("- GDELT 数据可能有延迟 / GDELT data may have delays")
        print("- 请尝试更早的日期 / Please try an earlier date")
        print("- 建议使用 2015-2024 年的日期 / Recommend using dates from 2015-2024")
    else:
        # 确保 day 列是字符串类型 / Ensure day column is string type
        new_df['day'] = new_df['day'].astype(str)
        
        # 检查是否已存在CSV文件 / Check if CSV file already exists
        if os.path.exists(output_file):
            print(f"\n发现已存在的文件 / Found existing file: {output_file}")
            # 读取现有数据 / Read existing data
            existing_df = pd.read_csv(output_file)
            
            # 确保现有数据的 day 列也是字符串类型 / Ensure existing data's day column is string type
            existing_df['day'] = existing_df['day'].astype(str)
            
            # 显示删除前的数据情况 / Show data before deletion
            same_date_count = len(existing_df[existing_df['day'] == date])
            if same_date_count > 0:
                print(f"发现 {same_date_count} 条日期为 {date} 的旧数据，将被替换 / Found {same_date_count} old records for {date}, will be replaced")
            
            # 合并数据：先删除相同日期的旧数据，再添加新数据 / Merge data: remove old data for same date, then add new data
            # 保留不是当前查询日期的数据 / Keep data not from current query date
            existing_df = existing_df[existing_df['day'] != date]
            
            # 合并新旧数据 / Combine old and new data
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # 按日期和国家排序 / Sort by date and country
            combined_df = combined_df.sort_values(['day', 'country'])
            
            # 保存更新后的数据 / Save updated data
            combined_df.to_csv(output_file, index=False)
            print(f"✓ 数据已更新 / Data updated!")
            
            # 显示更新情况 / Show update status
            print(f"\n文件中现有的日期 / Dates in file:")
            unique_dates = combined_df['day'].unique()
            for d in sorted(unique_dates):
                date_count = len(combined_df[combined_df['day'] == d])
                print(f"  - {d} ({date_count} 条记录/records)")
        else:
            # 如果文件不存在，创建新文件 / If file doesn't exist, create new file
            new_df.to_csv(output_file, index=False)
            print(f"\n✓ 新文件已创建 / New file created!")
        
        # 显示当前查询的数据 / Display current query data
        print(f"\n✓ 日期 {date} 的数据 / Data for {date}：")
        cn_count = new_df[new_df.country=='CN']['news_count'].values[0] if len(new_df[new_df.country=='CN']) > 0 else 0
        uk_count = new_df[new_df.country=='UK']['news_count'].values[0] if len(new_df[new_df.country=='UK']) > 0 else 0
        us_count = new_df[new_df.country=='US']['news_count'].values[0] if len(new_df[new_df.country=='US']) > 0 else 0
        
        print(f"  - CN (中国/China): {cn_count} 条新闻/news")
        print(f"  - UK (英国/UK): {uk_count} 条新闻/news")
        print(f"  - US (美国/USA): {us_count} 条新闻/news")
        print(f"\n✓ 数据已保存到 / Data saved to: {output_file}")
        
        # 显示本次查询的详细数据 / Display detailed data for current query
        print("\n本次查询的详细数据 / Detailed data for current query:")
        print(new_df.to_string(index=False))
        
except Exception as e:
    print(f"\n出错了 / Error occurred: {str(e)}")
    print("\n可能的原因 / Possible reasons:")
    print("1. 日期格式不正确（应该是8位数字，如: 20150217）/ Incorrect date format (should be 8 digits, e.g.: 20150217)")
    print("2. 网络连接问题 / Network connection issues")
    print("3. 请确保已安装 db-dtypes / Please ensure db-dtypes is installed: pip3 install db-dtypes")
    
    # 调试信息 / Debug information
    if 'existing_df' in locals():
        print(f"\n调试信息 / Debug info:")
        print(f"existing_df day 列的数据类型 / existing_df day column type: {existing_df['day'].dtype}")
        print(f"查询的日期 / Query date: {date} (类型/type: {type(date)})")

input("\n按回车键退出... / Press Enter to exit...")