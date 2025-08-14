import os
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime

def download_gdelt_data(date_str, output_file='gdelt_data.csv'):
    """
    下载 GDELT 数据的函数版本
    date_str: YYYYMMDD 格式的日期字符串
    """
    # 使用同文件夹下的密钥文件
    key_path = os.path.join(os.path.dirname(__file__), '..', 'gdelt_data', 'bigquery_key.json')
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    # 查询数据
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
        CAST(DATEADDED AS STRING) >= '{date_str}000000'
        AND CAST(DATEADDED AS STRING) <= '{date_str}235959'
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

    try:
        # 执行查询
        query_job = client.query(query)
        new_df = query_job.to_dataframe()
        
        if new_df.empty:
            return False, f"未找到 {date_str} 的数据"
        
        # 保存数据
        output_path = os.path.join(os.path.dirname(__file__), '..', 'gdelt_data', output_file)
        
        if os.path.exists(output_path):
            existing_df = pd.read_csv(output_path)
            existing_df['day'] = existing_df['day'].astype(str)
            new_df['day'] = new_df['day'].astype(str)
            
            # 删除相同日期的旧数据
            existing_df = existing_df[existing_df['day'] != date_str]
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df = combined_df.sort_values(['day', 'country'])
            combined_df.to_csv(output_path, index=False)
        else:
            new_df.to_csv(output_path, index=False)
        
        # 返回成功信息
        result_msg = f"日期 {date_str} 的数据：\n"
        for _, row in new_df.iterrows():
            result_msg += f"  - {row['country']}: {int(row['news_count'])} 条新闻\n"
        
        return True, result_msg
        
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    # 测试
    success, message = download_gdelt_data('20250722')
    print(message)