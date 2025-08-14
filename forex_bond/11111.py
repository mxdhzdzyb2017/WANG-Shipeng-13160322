import pandas as pd
import os
from datetime import datetime
from forex_data_api import download_forex_data

def update_all_data():
    """
    更新所有汇率和国债数据
    """
    try:
        # 调用 forex_data_api.py 中的函数
        success, message = download_forex_data()
        
        if success:
            # 同时创建/更新 news_features.csv 文件，确保格式正确
            news_file = os.path.join(os.path.dirname(__file__), 'news_features.csv')
            
            # 如果文件不存在，创建一个默认的结构
            if not os.path.exists(news_file):
                # 创建一个空的新闻数据文件
                default_news = pd.DataFrame({
                    'timestamp': [datetime.now().strftime('%Y-%m-%d')],
                    'country': ['CN'],
                    'news_count': [0],
                    'avg_tone': [0]
                })
                default_news.to_csv(news_file, index=False)
                print(f"创建了新的 news_features.csv 文件")
            
            return True, message
        else:
            return False, message
            
    except Exception as e:
        return False, f"更新数据时出错: {str(e)}"

if __name__ == "__main__":
    success, message = update_all_data()
    print(message)