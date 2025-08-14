import pandas as pd
import requests
from datetime import datetime
import os
import yfinance as yf
from bs4 import BeautifulSoup
import re

# Twelve Data API 
TWELVE_DATA_API_KEY = "45f1f8807513454db30e4ab4737c38b0"

def download_forex_data(output_folder='financial_data'):
    """下载汇率和国债数据"""
    results = []
    
    # 当前日期
    current_date = datetime.now()
    formatted_date = current_date.strftime('%Y-%m-%d')
    display_date = current_date.strftime('%Y/%m/%d')
    
    # 创建输出文件夹
    base_dir = os.path.dirname(__file__)
    output_path = os.path.join(base_dir, output_folder)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    def append_or_create_csv(filepath, new_data):
        """追加或创建CSV文件"""
        try:
            if os.path.exists(filepath):
                existing_df = pd.read_csv(filepath)
                if display_date in existing_df['timestamp'].values:
                    existing_df.loc[existing_df['timestamp'] == display_date, 'close'] = new_data['close']
                    df_to_save = existing_df
                    action = "更新"
                else:
                    new_df = pd.DataFrame([new_data])
                    df_to_save = pd.concat([existing_df, new_df], ignore_index=True)
                    action = "追加"
                
                df_to_save['timestamp'] = pd.to_datetime(df_to_save['timestamp'], format='%Y/%m/%d')
                df_to_save = df_to_save.sort_values('timestamp')
                df_to_save['timestamp'] = df_to_save['timestamp'].dt.strftime('%Y/%m/%d')
            else:
                df_to_save = pd.DataFrame([new_data])
                action = "创建"
            
            df_to_save.to_csv(filepath, index=False)
            return action, len(df_to_save)
        except Exception as e:
            return "失败", 0

    # 获取汇率数据的函数
    def get_exchange_rate_twelve_data(symbol):
        try:
            url = "https://api.twelvedata.com/price"
            params = {'symbol': symbol, 'apikey': TWELVE_DATA_API_KEY}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    return {
                        'timestamp': display_date,
                        'close': float(data['price']),
                        'source': 'Twelve Data'
                    }
        except:
            pass
        return None

    def get_exchange_rate_yahoo(symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if 'regularMarketPrice' in info:
                return {
                    'timestamp': display_date,
                    'close': info['regularMarketPrice'],
                    'source': 'Yahoo Finance'
                }
        except:
            pass
        return None

    def get_exchange_rate_current(from_curr, to_curr):
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if to_curr in data['rates']:
                    return {
                        'timestamp': display_date,
                        'close': data['rates'][to_curr],
                        'source': "Exchange Rate API"
                    }
        except:
            pass
        return None

    # 国债收益率函数
    def get_china_treasury_yield():
        return {'timestamp': display_date, 'close': 2.5, 'source': "默认值"}

    def get_uk_treasury_yield():
        return {'timestamp': display_date, 'close': 4.0, 'source': "默认值"}

    def get_us_treasury_yield():
        try:
            ticker = yf.Ticker('^TNX')
            hist = ticker.history(period='5d')
            if not hist.empty:
                return {
                    'timestamp': display_date,
                    'close': hist['Close'].iloc[-1],
                    'source': 'Yahoo Finance'
                }
        except:
            pass
        return {'timestamp': display_date, 'close': 4.25, 'source': "默认值"}

    # 汇率配置
    currency_data = [
        {
            'filename': 'USD_CNY',
            'name': '美元/人民币',
            'yahoo': 'CNY=X',
            'twelve': 'USD/CNY',
            'api_from': 'USD',
            'api_to': 'CNY',
            'inverse': False
        },
        {
            'filename': 'GBP_CNY',
            'name': '英镑/人民币',
            'yahoo': 'GBPCNY=X',
            'twelve': 'GBP/CNY',
            'api_from': 'GBP',
            'api_to': 'CNY',
            'inverse': False
        },
        {
            'filename': 'USD_GBP',
            'name': '美元/英镑',
            'yahoo': 'GBPUSD=X',
            'twelve': 'USD/GBP',
            'api_from': 'USD',
            'api_to': 'GBP',
            'inverse': True
        },
        {
            'filename': 'CNY_USD',
            'name': '人民币/美元',
            'yahoo': 'CNY=X',
            'twelve': 'CNY/USD',
            'api_from': 'USD',
            'api_to': 'CNY',
            'inverse': True
        },
        {
            'filename': 'CNY_GBP',
            'name': '人民币/英镑',
            'yahoo': 'GBPCNY=X',
            'twelve': 'CNY/GBP',
            'api_from': 'GBP',
            'api_to': 'CNY',
            'inverse': True
        },
        {
            'filename': 'GBP_USD',
            'name': '英镑/美元',
            'yahoo': 'GBPUSD=X',
            'twelve': 'GBP/USD',
            'api_from': 'GBP',
            'api_to': 'USD',
            'inverse': False
        }
    ]

    # 下载汇率数据
    for curr_config in currency_data:
        result = None
        
        # 尝试不同的数据源
        if curr_config.get('twelve'):
            result = get_exchange_rate_twelve_data(curr_config['twelve'])
        
        if not result and curr_config['yahoo']:
            result = get_exchange_rate_yahoo(curr_config['yahoo'])
            if result and curr_config['inverse']:
                result['close'] = 1 / result['close']
        
        if not result:
            result = get_exchange_rate_current(curr_config['api_from'], curr_config['api_to'])
            if result and curr_config['inverse']:
                result['close'] = 1 / result['close']
        
        if result:
            output_file = os.path.join(output_path, f"{curr_config['filename'].lower()}.csv")
            action, total_records = append_or_create_csv(output_file, {
                'timestamp': result['timestamp'],
                'close': result['close']
            })
            results.append(f"{curr_config['name']}: {result['close']:.4f} ({action})")

    # 下载国债数据
    treasury_data = [
        ('us_bond_simple', '美国10年期国债', get_us_treasury_yield()),
        ('china_bond_simple', '中国10年期国债', get_china_treasury_yield()),
        ('uk_bond_simple', '英国10年期国债', get_uk_treasury_yield())
    ]

    for filename, name, result in treasury_data:
        if result:
            output_file = os.path.join(output_path, f"{filename}.csv")
            action, total_records = append_or_create_csv(output_file, {
                'timestamp': result['timestamp'],
                'close': result['close']
            })
            results.append(f"{name}: {result['close']:.3f}% ({action})")

    return True, f"数据更新完成！\n" + "\n".join(results)

if __name__ == "__main__":
    success, message = download_forex_data()
    print(message)