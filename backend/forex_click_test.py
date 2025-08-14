import pandas as pd
import joblib
import os

class ForexPredictor:
    def __init__(self):
        # 获取当前文件所在目录
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 定义你的6个货币对和文件映射
        self.currency_dict = {
            'USD_CNY': {'fx': "usd_cny.csv", 'model': "USD_CNY_GradientBoosting.pkl"},
            'USD_GBP': {'fx': "usd_gbp.csv", 'model': "USD_GBP_GradientBoosting.pkl"},
            'CNY_USD': {'fx': "cny_usd.csv", 'model': "CNY_USD_LogisticRegression.pkl"},
            'GBP_CNY': {'fx': "gbp_cny.csv", 'model': "GBP_CNY_LogisticRegression.pkl"},
            'GBP_USD': {'fx': "gbp_usd.csv", 'model': "GBP_USD_LogisticRegression.pkl"},
            'CNY_GBP': {'fx': "cny_gbp.csv", 'model': "CNY_GBP_RandomForest.pkl"},
        }

        # 需要使用的特征列
        self.features = [
            'bond_CN', 'bond_US', 'bond_UK',
            'news_count_CN', 'news_count_UK', 'news_count_US',
            'avg_tone_CN', 'avg_tone_UK', 'avg_tone_US'
        ]
        self._init_data()

    def _init_data(self):
        try:
            # 加载国债数据 - 在 financial_data 文件夹
            bond_CN = pd.read_csv(os.path.join(self.base_dir, "financial_data", "china_bond_simple.csv"))
            bond_CN['timestamp'] = pd.to_datetime(bond_CN['timestamp'])
            bond_CN = bond_CN.rename(columns={'close': 'bond_CN'})[['timestamp', 'bond_CN']]

            bond_US = pd.read_csv(os.path.join(self.base_dir, "financial_data", "us_bond_simple.csv"))
            bond_US['timestamp'] = pd.to_datetime(bond_US['timestamp'])
            bond_US = bond_US.rename(columns={'close': 'bond_US'})[['timestamp', 'bond_US']]

            bond_UK = pd.read_csv(os.path.join(self.base_dir, "financial_data", "uk_bond_simple.csv"))
            bond_UK['timestamp'] = pd.to_datetime(bond_UK['timestamp'])
            bond_UK = bond_UK.rename(columns={'close': 'bond_UK'})[['timestamp', 'bond_UK']]

            # 加载新闻数据 - 更智能的处理
            news_path = os.path.join(self.base_dir, "news_features.csv")
            news_pivot = None
            
            if os.path.exists(news_path):
                news = pd.read_csv(news_path)
                print(f"news_features.csv 列名: {news.columns.tolist()}")
                
                # 查找时间列
                time_col = None
                for col in ['timestamp', 'date', 'day', 'Date', 'Day']:
                    if col in news.columns:
                        time_col = col
                        break
                
                if time_col:
                    # 尝试多种日期格式
                    for fmt in ['%Y%m%d', '%Y-%m-%d', '%Y/%m/%d', None]:
                        try:
                            news['timestamp'] = pd.to_datetime(news[time_col], format=fmt)
                            break
                        except:
                            continue
                    
                    # 检查是否已经是 pivot 格式
                    if all(col in news.columns for col in ['news_count_CN', 'news_count_UK', 'news_count_US']):
                        # 已经是 pivot 格式
                        news_pivot = news.copy()
                        if 'timestamp' not in news_pivot.columns and time_col != 'timestamp':
                            news_pivot = news_pivot.rename(columns={time_col: 'timestamp'})
                    elif 'country' in news.columns:
                        # 需要 pivot
                        news_pivot = news.pivot(index='timestamp', columns='country', values=['news_count', 'avg_tone'])
                        news_pivot.columns = ['_'.join(col).strip() for col in news_pivot.columns.values]
                        news_pivot = news_pivot.reset_index()
            
            # 如果 news_features.csv 处理失败，尝试 gdelt_data.csv
            if news_pivot is None:
                gdelt_path = os.path.join(self.base_dir, "..", "gdelt_data", "gdelt_data.csv")
                if os.path.exists(gdelt_path):
                    gdelt = pd.read_csv(gdelt_path)
                    print(f"gdelt_data.csv 列名: {gdelt.columns.tolist()}")
                    
                    if 'day' in gdelt.columns:
                        gdelt['timestamp'] = pd.to_datetime(gdelt['day'], format='%Y%m%d', errors='coerce')
                        if 'country' in gdelt.columns:
                            gdelt_pivot = gdelt.pivot(index='timestamp', columns='country', values=['news_count', 'avg_tone'])
                            gdelt_pivot.columns = ['_'.join(col).strip() for col in gdelt_pivot.columns.values]
                            news_pivot = gdelt_pivot.reset_index()
            
            # 如果还是没有新闻数据，创建空的
            if news_pivot is None:
                print("警告：无法加载新闻数据，将使用空数据")
                # 创建一个包含所有日期的空新闻数据框
                all_dates = set()
                for curr, files in self.currency_dict.items():
                    fx_path = os.path.join(self.base_dir, "financial_data", files['fx'])
                    if os.path.exists(fx_path):
                        fx = pd.read_csv(fx_path)
                        fx['timestamp'] = pd.to_datetime(fx['timestamp'])
                        all_dates.update(fx['timestamp'])
                
                news_pivot = pd.DataFrame({'timestamp': sorted(list(all_dates))})
                for col in self.features:
                    if 'news' in col or 'tone' in col:
                        news_pivot[col] = 0

            # 合并每个币对数据和特征
            self.all_currency_data = {}
            for curr, files in self.currency_dict.items():
                # 汇率文件在 financial_data 文件夹
                fx_path = os.path.join(self.base_dir, "financial_data", files['fx'])
                
                if not os.path.exists(fx_path):
                    print(f"警告：找不到文件 {fx_path}")
                    continue
                
                fx = pd.read_csv(fx_path)
                fx['timestamp'] = pd.to_datetime(fx['timestamp'])
                
                # 合并所有数据
                df = fx.merge(bond_CN, on='timestamp', how='left')
                df = df.merge(bond_US, on='timestamp', how='left')
                df = df.merge(bond_UK, on='timestamp', how='left')
                df = df.merge(news_pivot, on='timestamp', how='left')
                
                # 填充缺失的特征列
                for col in self.features:
                    if col not in df.columns:
                        df[col] = 0
                df[self.features] = df[self.features].fillna(0)
                
                # 只保留需要的列
                test_df = df[['timestamp', 'close'] + self.features].copy()
                test_df = test_df.sort_values('timestamp').reset_index(drop=True)
                self.all_currency_data[curr] = test_df

            # 加载所有模型 - 在 backend 根目录
            self.models = {}
            for curr, files in self.currency_dict.items():
                if curr in self.all_currency_data:  # 只加载有数据的模型
                    model_path = os.path.join(self.base_dir, files['model'])
                    if os.path.exists(model_path):
                        self.models[curr] = joblib.load(model_path)
                    else:
                        print(f"警告：找不到模型文件 {model_path}")

            # 找到所有币对的共同日期
            if self.all_currency_data:
                date_sets = [set(df['timestamp']) for df in self.all_currency_data.values()]
                self.common_dates = sorted(list(set.intersection(*date_sets)))
            else:
                self.common_dates = []
            
            print(f"初始化成功！找到 {len(self.common_dates)} 个共同交易日")
            if self.common_dates:
                print(f"日期范围：{self.common_dates[0].strftime('%Y-%m-%d')} 到 {self.common_dates[-1].strftime('%Y-%m-%d')}")
            
            self.reset()
            
        except Exception as e:
            print(f"初始化错误: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def reset(self):
        # 重置历史预测和计数
        self.index = 0
        self.pred_history = {curr: [] for curr in self.currency_dict}
        self.correct = {curr: 0 for curr in self.currency_dict}
        self.total = {curr: 0 for curr in self.currency_dict}
        self.is_predicting_future = False  # 标记是否在预测未来

    def predict_next_day(self):
        if self.index >= len(self.common_dates):
            return None  # 已到末尾
        
        # 如果是最后一天，预测未来
        if self.index == len(self.common_dates) - 1:
            self.is_predicting_future = True
            today = self.common_dates[self.index]
            
            out = {
                'date': today.strftime('%Y-%m-%d'),
                'pairs': [],
                'is_future_prediction': True  # 标记这是对未来的预测
            }
            
            for curr in self.currency_dict:
                if curr not in self.all_currency_data or curr not in self.models:
                    continue
                    
                df = self.all_currency_data[curr]
                row_now = df[df['timestamp'] == today]
                
                if row_now.empty:
                    pred = None
                    close_now = None
                else:
                    # 获取特征和预测
                    X = row_now[self.features].values
                    pred = int(self.models[curr].predict(X)[0])
                    close_now = float(row_now['close'].values[0])
                
                # 添加到输出（未来预测没有实际值）
                out['pairs'].append({
                    'name': curr,
                    'pred': pred,
                    'real': None,  # 未来没有实际值
                    'close': close_now,
                    'next_close': None,  # 未来没有下一天的收盘价
                    'correct': self.correct[curr],
                    'total': self.total[curr],
                    'acc': round(self.correct[curr] / self.total[curr], 4) if self.total[curr] > 0 else None
                })
            
            self.index += 1
            return out
        
        # 正常的历史数据预测
        today = self.common_dates[self.index]
        tomorrow = self.common_dates[self.index + 1]
        
        out = {
            'date': today.strftime('%Y-%m-%d'),
            'pairs': [],
            'is_future_prediction': False
        }
        
        for curr in self.currency_dict:
            if curr not in self.all_currency_data or curr not in self.models:
                continue
                
            df = self.all_currency_data[curr]
            row_now = df[df['timestamp'] == today]
            row_next = df[df['timestamp'] == tomorrow]
            
            if row_now.empty or row_next.empty:
                pred = None
                real = None
                close_now = None
                close_next = None
            else:
                # 获取特征和预测
                X = row_now[self.features].values
                pred = int(self.models[curr].predict(X)[0])
                
                # 获取实际值
                close_now = float(row_now['close'].values[0])
                close_next = float(row_next['close'].values[0])
                real = int(close_next > close_now)
                
                # 更新统计
                self.pred_history[curr].append({'date': today, 'pred': pred, 'real': real})
                self.total[curr] += 1
                if pred == real:
                    self.correct[curr] += 1
            
            # 添加到输出
            out['pairs'].append({
                'name': curr,
                'pred': pred,
                'real': real,
                'close': close_now,
                'next_close': close_next,
                'correct': self.correct[curr],
                'total': self.total[curr],
                'acc': round(self.correct[curr] / self.total[curr], 4) if self.total[curr] > 0 else None
            })
        
        self.index += 1
        return out

# 测试代码
if __name__ == "__main__":
    predictor = ForexPredictor()
    print(f"可用的货币对: {list(predictor.currency_dict.keys())}")
    
    # 预测一天
    result = predictor.predict_next_day()
    if result:
        print(f"\n预测日期: {result['date']}")
        for pair in result['pairs']:
            print(f"{pair['name']}: 预测={pair['pred']}, 实际={pair['real']}, 当前价={pair['close']}")