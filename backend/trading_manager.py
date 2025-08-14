import json
import os
from datetime import datetime
import pandas as pd

class TradingManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.base_dir, 'trading_data.json')
        self.trades_file = os.path.join(self.base_dir, 'trade_history.csv')
        self.load_data()
    
    def load_data(self):
        """加载交易数据和设置"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            # 默认设置
            self.data = {
                'initial_balance': 10000,  # 初始资金
                'base_currency': 'USD',  # 基础货币
                'currency_holdings': {  # 各货币持有量
                    'USD': 10000,
                    'CNY': 0,
                    'GBP': 0
                },
                'currency_allocations': {  # 各货币对分配比例
                    'USD_CNY': 16.67,
                    'USD_GBP': 16.67,
                    'CNY_USD': 16.67,
                    'GBP_CNY': 16.67,
                    'GBP_USD': 16.67,
                    'CNY_GBP': 16.67
                },
                'reverse_models': [],  # 需要反向的模型
                'auto_trade_enabled': False,  # 是否启用自动交易
                'auto_trade_time': '09:00',  # 自动交易时间
                'last_prediction_date': None,  # 最后预测日期
                'total_profit': 0,  # 总盈亏
                'win_rate': 0,  # 胜率
                'total_trades': 0,  # 总交易次数
                'winning_trades': 0,  # 盈利次数
                'trade_history': [],  # 交易历史
                'accuracy_history': {}  # 各货币对的准确率历史
            }
            self.save_data()
    
    def save_data(self):
        """保存交易数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def update_settings(self, settings):
        """更新交易设置"""
        # 检查是否需要更新货币持有量
        need_update_holdings = False
        
        # 如果改变了基础货币
        if 'base_currency' in settings and settings['base_currency'] != self.data.get('base_currency'):
            need_update_holdings = True
            self.data['base_currency'] = settings['base_currency']
        
        # 如果改变了初始资金
        if 'initial_balance' in settings and settings['initial_balance'] != self.data.get('initial_balance'):
            need_update_holdings = True
            self.data['initial_balance'] = settings['initial_balance']
        
        # 如果需要更新持有量（只在没有交易历史时更新）
        if need_update_holdings and self.data['total_trades'] == 0:
            base_curr = self.data['base_currency']
            initial_balance = self.data['initial_balance']
            self.data['currency_holdings'] = {
                'USD': initial_balance if base_curr == 'USD' else 0,
                'CNY': initial_balance if base_curr == 'CNY' else 0,
                'GBP': initial_balance if base_curr == 'GBP' else 0
            }
        
        # 更新其他设置
        for key, value in settings.items():
            if key not in ['base_currency', 'initial_balance']:  # 这些已经处理过了
                self.data[key] = value
        
        self.save_data()
    
    def toggle_reverse(self, currency_pair):
        """切换反向交易"""
        if currency_pair in self.data['reverse_models']:
            self.data['reverse_models'].remove(currency_pair)
        else:
            self.data['reverse_models'].append(currency_pair)
        self.save_data()
        return currency_pair in self.data['reverse_models']
    
    def get_currency_from_pair(self, pair):
        """从货币对获取货币信息"""
        parts = pair.split('_')
        return parts[0], parts[1]
    
    def calculate_portfolio_value(self, current_prices):
        """计算投资组合总价值（以基础货币计）"""
        total_value = 0
        base_curr = self.data['base_currency']
        
        for currency, amount in self.data['currency_holdings'].items():
            if currency == base_curr:
                total_value += amount
            else:
                # 需要找到合适的汇率转换
                if amount > 0:
                    # 尝试直接汇率
                    pair = f"{currency}_{base_curr}"
                    if pair in current_prices and current_prices[pair] > 0:
                        total_value += amount * current_prices[pair]
                    else:
                        # 尝试反向汇率
                        pair_reverse = f"{base_curr}_{currency}"
                        if pair_reverse in current_prices and current_prices[pair_reverse] > 0:
                            total_value += amount / current_prices[pair_reverse]
        
        return total_value
    
    def get_min_trades_for_confidence(self):
        """获取建立信心所需的最小交易次数"""
        return 10  # 至少需要10次交易才能建立对准确率的信心
    
    def calculate_trade_amount(self, pair, allocation, portfolio_value, accuracy, total_trades):
        """计算交易金额"""
        # 基础交易金额
        base_amount = portfolio_value * (allocation / 100)
        
        # 如果交易次数太少，使用保守策略
        min_trades = self.get_min_trades_for_confidence()
        if total_trades < min_trades:
            # 初始阶段，每次只交易很小的比例
            confidence_factor = 0.1  # 只交易10%的分配金额
        else:
            # 根据准确率调整交易金额
            if accuracy < 0.55:
                confidence_factor = 0.3  # 准确率低于55%，交易30%
            elif accuracy < 0.6:
                confidence_factor = 0.5  # 准确率55-60%，交易50%
            elif accuracy < 0.7:
                confidence_factor = 0.8  # 准确率60-70%，交易80%
            else:
                confidence_factor = 1.0  # 准确率70%以上，全额交易
        
        return base_amount * confidence_factor
    
    def execute_trades(self, predictions):
        """执行交易"""
        trades = []
        date = predictions['date']
        
        # 获取当前价格
        current_prices = {}
        for pair_data in predictions['pairs']:
            if pair_data['close']:
                current_prices[pair_data['name']] = pair_data['close']
        
        # 计算组合总价值
        portfolio_value = self.calculate_portfolio_value(current_prices)
        
        # 打印调试信息
        print(f"当前持仓: {self.data['currency_holdings']}")
        print(f"组合总价值: {portfolio_value} {self.data['base_currency']}")
        
        for pair_data in predictions['pairs']:
            pair = pair_data['name']
            if pair not in self.data['currency_allocations']:
                continue
            
            # 获取货币对信息
            from_curr, to_curr = self.get_currency_from_pair(pair)
            
            # 获取该货币对的历史准确率
            if pair not in self.data['accuracy_history']:
                self.data['accuracy_history'][pair] = {
                    'correct': 0,
                    'total': 0,
                    'rate': 0.5  # 初始假设50%准确率
                }
            
            accuracy_info = self.data['accuracy_history'][pair]
            accuracy = accuracy_info['rate']
            total_trades = accuracy_info['total']
            
            # 获取分配比例和计算交易金额
            allocation = self.data['currency_allocations'][pair]
            trade_amount = self.calculate_trade_amount(pair, allocation, portfolio_value, accuracy, total_trades)
            
            # 获取预测值
            prediction = pair_data['pred']
            
            # 检查是否需要反向（手动设置的反向）
            if pair in self.data['reverse_models']:
                prediction = 1 - prediction if prediction in [0, 1] else prediction
            
            # 如果准确率低于50%且有足够的历史数据，自动反向
            if accuracy < 0.5 and total_trades >= self.get_min_trades_for_confidence():
                prediction = 1 - prediction if prediction in [0, 1] else prediction
                print(f"{pair} 准确率低于50% ({accuracy*100:.1f}%)，自动反向交易")
            
            # 获取当前价格
            current_price = pair_data['close']
            
            if current_price and prediction is not None and trade_amount > 0:
                # 限制每次交易不超过当前持有货币的30%
                max_trade_ratio = 0.3
                
                if prediction == 1:  # 预测上涨，买入 to_curr
                    # 需要 from_curr 来买入 to_curr
                    available_from = self.data['currency_holdings'].get(from_curr, 0)
                    max_trade_from = available_from * max_trade_ratio
                    
                    # 以基础货币计算的交易金额需要转换为from_curr
                    if from_curr == self.data['base_currency']:
                        required_from_curr = min(trade_amount, max_trade_from)
                    else:
                        # 需要将基础货币金额转换为from_curr
                        conversion_pair = f"{self.data['base_currency']}_{from_curr}"
                        if conversion_pair in current_prices:
                            required_from_curr = min(trade_amount * current_prices[conversion_pair], max_trade_from)
                        else:
                            conversion_pair_reverse = f"{from_curr}_{self.data['base_currency']}"
                            if conversion_pair_reverse in current_prices and current_prices[conversion_pair_reverse] > 0:
                                required_from_curr = min(trade_amount / current_prices[conversion_pair_reverse], max_trade_from)
                            else:
                                continue
                    
                    if required_from_curr > 0.01 and available_from >= required_from_curr:
                        # 执行买入
                        bought_amount = required_from_curr * current_price
                        self.data['currency_holdings'][from_curr] -= required_from_curr
                        self.data['currency_holdings'][to_curr] = self.data['currency_holdings'].get(to_curr, 0) + bought_amount
                        
                        trade = {
                            'date': date,
                            'pair': pair,
                            'prediction': 'BUY',
                            'from_currency': from_curr,
                            'to_currency': to_curr,
                            'amount': required_from_curr,
                            'price': current_price,
                            'received': bought_amount,
                            'accuracy': accuracy,
                            'is_reversed': pair in self.data['reverse_models'] or (accuracy < 0.5 and total_trades >= self.get_min_trades_for_confidence())
                        }
                        trades.append(trade)
                        
                else:  # 预测下跌，卖出 to_curr
                    # 实际上是买入 from_curr，卖出 to_curr
                    available_to = self.data['currency_holdings'].get(to_curr, 0)
                    max_trade_to = available_to * max_trade_ratio
                    
                    # 以基础货币计算的交易金额需要转换为to_curr
                    if to_curr == self.data['base_currency']:
                        required_to_curr = min(trade_amount, max_trade_to)
                    else:
                        # 需要将基础货币金额转换为to_curr
                        conversion_pair = f"{self.data['base_currency']}_{to_curr}"
                        if conversion_pair in current_prices:
                            required_to_curr = min(trade_amount * current_prices[conversion_pair], max_trade_to)
                        else:
                            conversion_pair_reverse = f"{to_curr}_{self.data['base_currency']}"
                            if conversion_pair_reverse in current_prices and current_prices[conversion_pair_reverse] > 0:
                                required_to_curr = min(trade_amount / current_prices[conversion_pair_reverse], max_trade_to)
                            else:
                                continue
                    
                    if required_to_curr > 0.01 and available_to >= required_to_curr:
                        # 执行卖出（买入from_curr）
                        received_amount = required_to_curr / current_price if current_price > 0 else 0
                        self.data['currency_holdings'][to_curr] -= required_to_curr
                        self.data['currency_holdings'][from_curr] = self.data['currency_holdings'].get(from_curr, 0) + received_amount
                        
                        trade = {
                            'date': date,
                            'pair': pair,
                            'prediction': 'SELL',
                            'from_currency': to_curr,
                            'to_currency': from_curr,
                            'amount': required_to_curr,
                            'price': current_price,
                            'received': received_amount,
                            'accuracy': accuracy,
                            'is_reversed': pair in self.data['reverse_models'] or (accuracy < 0.5 and total_trades >= self.get_min_trades_for_confidence())
                        }
                        trades.append(trade)
        
        # 保存交易记录
        if trades:
            self.save_trades(trades)
            self.data['trade_history'].extend(trades)
            self.data['total_trades'] += len(trades)
        
        # 计算新的组合价值和盈亏
        new_portfolio_value = self.calculate_portfolio_value(current_prices)
        initial_value = self.data['initial_balance']
        self.data['total_profit'] = new_portfolio_value - initial_value
        
        # 更新每个货币对的准确率（如果有实际结果）
        for pair_data in predictions['pairs']:
            if not predictions.get('is_future_prediction', False) and pair_data.get('pred') is not None and pair_data.get('real') is not None:
                pair = pair_data['name']
                if pair not in self.data['accuracy_history']:
                    self.data['accuracy_history'][pair] = {
                        'correct': 0,
                        'total': 0,
                        'rate': 0.5
                    }
                
                # 原始预测（未经过任何反向）
                original_pred = pair_data['pred']
                
                # 检查是否需要反向（手动反向）
                if pair in self.data['reverse_models']:
                    original_pred = 1 - original_pred if original_pred in [0, 1] else original_pred
                
                # 更新准确率（基于原始模型的准确率，不考虑自动反向）
                self.data['accuracy_history'][pair]['total'] += 1
                if pair_data['pred'] == pair_data['real']:  # 使用原始预测值
                    self.data['accuracy_history'][pair]['correct'] += 1
                
                # 计算新的准确率
                total = self.data['accuracy_history'][pair]['total']
                correct = self.data['accuracy_history'][pair]['correct']
                self.data['accuracy_history'][pair]['rate'] = correct / total if total > 0 else 0.5
        
        # 更新总体胜率
        total_correct = sum(info['correct'] for info in self.data['accuracy_history'].values())
        total_predictions = sum(info['total'] for info in self.data['accuracy_history'].values())
        self.data['win_rate'] = total_correct / total_predictions if total_predictions > 0 else 0
        
        self.data['last_prediction_date'] = date
        self.save_data()
        
        print(f"交易后持仓: {self.data['currency_holdings']}")
        print(f"执行了 {len(trades)} 笔交易")
        
        return trades
    
    def save_trades(self, trades):
        """保存交易记录到CSV"""
        df_new = pd.DataFrame(trades)
        
        if os.path.exists(self.trades_file):
            df_existing = pd.read_csv(self.trades_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(self.trades_file, index=False)
    
    def get_performance_stats(self):
        """获取性能统计"""
        # 获取当前汇率（简化处理）
        current_prices = {}
        
        # 计算当前组合价值
        current_value = self.calculate_portfolio_value(current_prices) if current_prices else sum(self.data['currency_holdings'].values())
        
        return {
            'total_profit': self.data['total_profit'],
            'win_rate': self.data['win_rate'] * 100,
            'total_trades': self.data['total_trades'],
            'winning_trades': sum(info['correct'] for info in self.data['accuracy_history'].values()),
            'currency_holdings': self.data['currency_holdings'],
            'portfolio_value': current_value,
            'base_currency': self.data['base_currency'],
            'initial_balance': self.data['initial_balance'],
            'accuracy_history': self.data['accuracy_history']
        }
    
    def reset_portfolio(self):
        """重置投资组合"""
        base_curr = self.data['base_currency']
        initial_balance = self.data['initial_balance']
        
        # 重置货币持有量
        self.data['currency_holdings'] = {
            'USD': initial_balance if base_curr == 'USD' else 0,
            'CNY': initial_balance if base_curr == 'CNY' else 0,
            'GBP': initial_balance if base_curr == 'GBP' else 0
        }
        
        # 重置统计数据
        self.data['total_profit'] = 0
        self.data['win_rate'] = 0
        self.data['total_trades'] = 0
        self.data['winning_trades'] = 0
        self.data['trade_history'] = []
        self.data['accuracy_history'] = {}
        
        self.save_data()