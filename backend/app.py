from flask import Flask, jsonify, request
from flask_cors import CORS
from forex_click_test import ForexPredictor
from download_api import download_gdelt_data
from trading_manager import TradingManager
from datetime import datetime, timedelta
import pandas as pd
import os
import json
import traceback
import subprocess
import sys
import threading
import time
import schedule

app = Flask(__name__)
# 更宽松的CORS设置
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 初始化预测器和交易管理器
predictor = None
trading_manager = None

try:
    predictor = ForexPredictor()
    trading_manager = TradingManager()
    print(f"预测器和交易管理器初始化成功！共有 {len(predictor.common_dates)} 个交易日")
except Exception as e:
    print(f"初始化失败: {str(e)}")
    traceback.print_exc()

# 自动交易函数
def auto_trade_job():
    """自动交易任务"""
    try:
        if not trading_manager or not trading_manager.data['auto_trade_enabled']:
            return
        
        print(f"执行自动交易任务 - {datetime.now()}")
        
        # 1. 更新数据
        script_path = os.path.join(os.path.dirname(__file__), '11111.py')
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            # 2. 重新初始化预测器
            global predictor
            predictor = ForexPredictor()
            
            # 3. 进行预测
            prediction = predictor.predict_next_day()
            
            if prediction and not prediction.get('is_future_prediction', False):
                # 4. 执行交易
                trades = trading_manager.execute_trades(prediction)
                print(f"自动交易完成，执行了 {len(trades)} 笔交易")
            else:
                print("没有可预测的数据或已是未来预测")
        else:
            print(f"自动更新数据失败: {result.stderr}")
            
    except Exception as e:
        print(f"自动交易错误: {str(e)}")
        traceback.print_exc()

# 启动自动交易调度器
def run_scheduler():
    """运行调度器"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

# 启动调度器线程
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# 添加一个简单的测试路由
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'status': 'ok', 'message': '服务器正在运行'})

@app.route('/api/currencies', methods=['GET'])
def get_currencies():
    """获取可用的货币对列表"""
    try:
        if predictor is None:
            return jsonify({'error': '预测器未初始化'}), 500
        
        currencies = list(predictor.currency_dict.keys())
        return jsonify(currencies)
    except Exception as e:
        print(f"获取货币对列表错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-forex-data', methods=['POST'])
def update_forex_data():
    """更新汇率和国债数据"""
    try:
        print("开始更新汇率和国债数据...")
        
        # 运行11111.py文件
        script_path = os.path.join(os.path.dirname(__file__), '11111.py')
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            # 重新初始化预测器以加载新数据
            global predictor
            predictor = ForexPredictor()
            
            # 解析输出信息
            output_lines = result.stdout.strip().split('\n')
            message = '\n'.join(output_lines)
            
            return jsonify({
                'success': True, 
                'message': message,
                'total_dates': len(predictor.common_dates) if predictor else 0
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or '更新失败'
            }), 500
            
    except Exception as e:
        print(f"更新汇率数据错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict-next', methods=['GET'])
def predict_next():
    """预测下一天"""
    try:
        if predictor is None:
            return jsonify({'error': '预测器未初始化'}), 500
        
        result = predictor.predict_next_day()
        
        if result is None:
            return jsonify({'finished': True, 'message': '已全部预测完毕'})
        
        # 如果启用了交易，执行交易
        if trading_manager and not result.get('is_future_prediction', False):
            trades = trading_manager.execute_trades(result)
            result['trades'] = trades
            result['performance'] = trading_manager.get_performance_stats()
        
        return jsonify(result)
    except Exception as e:
        print(f"预测错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict-multiple', methods=['POST'])
def predict_multiple():
    """预测多天"""
    try:
        if predictor is None:
            return jsonify({'error': '预测器未初始化'}), 500
        
        data = request.json
        days = data.get('days', 1)
        
        results = []
        all_trades = []
        
        for i in range(days):
            result = predictor.predict_next_day()
            if result is None:
                break
            
            # 执行交易
            if trading_manager and not result.get('is_future_prediction', False):
                trades = trading_manager.execute_trades(result)
                result['trades'] = trades
                all_trades.extend(trades)
            
            results.append(result)
        
        # 获取最终性能统计
        performance = trading_manager.get_performance_stats() if trading_manager else None
        
        return jsonify({
            'results': results, 
            'count': len(results),
            'total_trades': len(all_trades),
            'performance': performance
        })
    except Exception as e:
        print(f"批量预测错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """重置预测器"""
    try:
        if predictor is None:
            return jsonify({'error': '预测器未初始化'}), 500
        
        predictor.reset()
        
        # 询问是否也重置交易数据
        reset_trades = request.json.get('reset_trades', False)
        if reset_trades and trading_manager:
            trading_manager.data['positions'] = {}
            trading_manager.data['total_profit'] = 0
            trading_manager.data['win_rate'] = 0
            trading_manager.data['total_trades'] = 0
            trading_manager.data['winning_trades'] = 0
            trading_manager.data['current_balance'] = trading_manager.data['initial_balance']
            trading_manager.save_data()
        
        return jsonify({'success': True, 'message': '已重置'})
    except Exception as e:
        print(f"重置错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/settings', methods=['GET', 'POST'])
def trading_settings():
    """获取或更新交易设置"""
    try:
        if not trading_manager:
            return jsonify({'error': '交易管理器未初始化'}), 500
        
        if request.method == 'GET':
            return jsonify(trading_manager.data)
        else:
            # 更新设置
            settings = request.json
            
            # 如果更新了自动交易时间，重新设置调度器
            if 'auto_trade_time' in settings:
                schedule.clear()
                if settings.get('auto_trade_enabled', False):
                    schedule.every().day.at(settings['auto_trade_time']).do(auto_trade_job)
            
            trading_manager.update_settings(settings)
            return jsonify({'success': True, 'message': '设置已更新'})
            
    except Exception as e:
        print(f"交易设置错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/toggle-reverse/<currency>', methods=['POST'])
def toggle_reverse(currency):
    """切换反向交易"""
    try:
        if not trading_manager:
            return jsonify({'error': '交易管理器未初始化'}), 500
        
        is_reversed = trading_manager.toggle_reverse(currency)
        return jsonify({
            'success': True,
            'currency': currency,
            'is_reversed': is_reversed
        })
        
    except Exception as e:
        print(f"切换反向交易错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/history')
def get_trade_history():
    """获取交易历史"""
    try:
        trades_file = os.path.join(app.root_path, 'trade_history.csv')
        
        if not os.path.exists(trades_file):
            return jsonify([])  # 如果文件不存在，返回空数组
        
        # 读取CSV文件
        df = pd.read_csv(trades_file)
        
        # 转换为字典列表
        trades = df.to_dict('records')
        
        return jsonify(trades)
    except Exception as e:
        print(f"读取交易历史错误: {str(e)}")
        return jsonify([])  # 出错时返回空数组而不是错误

@app.route('/api/trading/reset-portfolio', methods=['POST'])
def reset_portfolio():
    """重置投资组合"""
    try:
        if not trading_manager:
            return jsonify({'error': '交易管理器未初始化'}), 500
        
        trading_manager.reset_portfolio()
        return jsonify({'success': True, 'message': '投资组合已重置'})
        
    except Exception as e:
        print(f"重置投资组合错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-gdelt', methods=['POST'])
def download_gdelt():
    """下载GDELT数据"""
    try:
        data = request.json
        date = data.get('date')
        
        if not date:
            return jsonify({'error': '请提供日期'}), 400
        
        # 转换日期格式为YYYYMMDD
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_str = date_obj.strftime('%Y%m%d')
        except:
            return jsonify({'error': '日期格式错误，请使用YYYY-MM-DD格式'}), 400
        
        print(f"下载GDELT数据请求: date={date_str}")
        
        # 调用下载函数
        success, message = download_gdelt_data(date_str)
        
        if success:
            # 重新初始化预测器以加载新数据
            global predictor
            predictor = ForexPredictor()
            return jsonify({
                'success': True, 
                'message': message,
                'total_dates': len(predictor.common_dates) if predictor else 0
            })
        else:
            return jsonify({'error': message}), 500
            
    except Exception as e:
        print(f"下载GDELT数据错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    try:
        if predictor is None:
            return jsonify({
                'initialized': False,
                'error': '预测器未初始化'
            })
        
        status = {
            'initialized': True,
            'current_index': predictor.index,
            'total_dates': len(predictor.common_dates),
            'date_range': {
                'start': predictor.common_dates[0].strftime('%Y-%m-%d') if predictor.common_dates else None,
                'end': predictor.common_dates[-1].strftime('%Y-%m-%d') if predictor.common_dates else None
            },
            'currencies': list(predictor.currency_dict.keys()),
            'accuracy': {},
            'trading': trading_manager.get_performance_stats() if trading_manager else None
        }
        
        # 添加每个货币对的准确率
        for curr in predictor.currency_dict:
            if predictor.total[curr] > 0:
                status['accuracy'][curr] = {
                    'correct': predictor.correct[curr],
                    'total': predictor.total[curr],
                    'rate': round(predictor.correct[curr] / predictor.total[curr], 4),
                    'is_reversed': curr in trading_manager.data['reverse_models'] if trading_manager else False
                }
        
        return jsonify(status)
    except Exception as e:
        print(f"获取状态错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-latest-data', methods=['GET'])
def get_latest_data():
    """获取最新的数据日期和值"""
    try:
        result = {
            'forex': {},
            'bonds': {},
            'latest_date': None
        }
        
        # 检查汇率数据
        forex_pairs = ['USD_CNY', 'USD_GBP', 'CNY_USD', 'GBP_CNY', 'GBP_USD', 'CNY_GBP']
        latest_dates = []
        
        for pair in forex_pairs:
            filename = os.path.join(os.path.dirname(__file__), 'financial_data', f"{pair.lower()}.csv")
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                if not df.empty:
                    # 获取最新的数据
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.sort_values('timestamp')
                    latest_row = df.iloc[-1]
                    
                    result['forex'][pair] = {
                        'value': float(latest_row['close']),
                        'date': latest_row['timestamp'].strftime('%Y-%m-%d')
                    }
                    latest_dates.append(latest_row['timestamp'])
        
        # 检查国债数据
        bond_map = {'CN': 'china_bond_simple.csv', 'US': 'us_bond_simple.csv', 'UK': 'uk_bond_simple.csv'}
        for country, filename in bond_map.items():
            filepath = os.path.join(os.path.dirname(__file__), 'financial_data', filename)
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.sort_values('timestamp')
                    latest_row = df.iloc[-1]
                    
                    result['bonds'][country] = {
                        'value': float(latest_row['close']),
                        'date': latest_row['timestamp'].strftime('%Y-%m-%d')
                    }
        
        # 找出最新的日期
        if latest_dates:
            result['latest_date'] = max(latest_dates).strftime('%Y-%m-%d')
        
        return jsonify(result)
        
    except Exception as e:
        print(f"获取最新数据错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-historical-data', methods=['POST'])
def add_historical_data():
    """添加历史数据"""
    try:
        data = request.json
        date = data.get('date')
        
        if not date:
            return jsonify({'error': '请提供日期'}), 400
        
        # 保存汇率数据
        forex_data = data.get('forex', {})
        bonds_data = data.get('bonds', {})
        news_data = data.get('news', {})
        
        base_dir = os.path.dirname(__file__)
        
        # 保存汇率
        for pair, value in forex_data.items():
            filepath = os.path.join(base_dir, 'financial_data', f"{pair.lower()}.csv")
            df_new = pd.DataFrame([{'timestamp': date, 'close': value}])
            
            if os.path.exists(filepath):
                df_existing = pd.read_csv(filepath)
                df_existing = df_existing[df_existing['timestamp'] != date]
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_combined = df_new
            
            df_combined.to_csv(filepath, index=False)
        
        # 保存国债数据
        bond_files = {'CN': 'china_bond_simple.csv', 'US': 'us_bond_simple.csv', 'UK': 'uk_bond_simple.csv'}
        for country, value in bonds_data.items():
            if country in bond_files:
                filepath = os.path.join(base_dir, 'financial_data', bond_files[country])
                df_new = pd.DataFrame([{'timestamp': date, 'close': value}])
                
                if os.path.exists(filepath):
                    df_existing = pd.read_csv(filepath)
                    df_existing = df_existing[df_existing['timestamp'] != date]
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                else:
                    df_combined = df_new
                
                df_combined.to_csv(filepath, index=False)
        
        # 保存新闻数据到 gdelt_data.csv
        if news_data:
            gdelt_file = os.path.join(base_dir, '..', 'gdelt_data', 'gdelt_data.csv')
            news_rows = []
            
            for country, data in news_data.items():
                news_rows.append({
                    'day': date.replace('-', ''),
                    'country': country,
                    'news_count': data.get('count', 0),
                    'avg_tone': data.get('tone', 0)
                })
            
            df_news = pd.DataFrame(news_rows)
            
            if os.path.exists(gdelt_file):
                df_existing = pd.read_csv(gdelt_file)
                # 删除相同日期的旧数据
                df_existing = df_existing[df_existing['day'] != date.replace('-', '')]
                df_combined = pd.concat([df_existing, df_news], ignore_index=True)
            else:
                df_combined = df_news
            
            df_combined.to_csv(gdelt_file, index=False)
        
        # 重新初始化预测器
        global predictor
        predictor = ForexPredictor()
        
        return jsonify({'success': True, 'message': '数据已保存'})
        
    except Exception as e:
        print(f"添加历史数据错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-historical-data', methods=['GET'])
def get_historical_data():
    """获取特定日期的历史数据"""
    try:
        date = request.args.get('date')
        if not date:
            return jsonify({'error': '请提供日期'}), 400
        
        result = {
            'exists': False,
            'forex': {},
            'bonds': {},
            'news': {}
        }
        
        base_dir = os.path.dirname(__file__)
        
        # 检查汇率数据
        forex_pairs = ['USD_CNY', 'USD_GBP', 'CNY_USD', 'GBP_CNY', 'GBP_USD', 'CNY_GBP']
        for pair in forex_pairs:
            filepath = os.path.join(base_dir, 'financial_data', f"{pair.lower()}.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                row = df[df['timestamp'] == date]
                if not row.empty:
                    result['forex'][pair] = float(row.iloc[0]['close'])
                    result['exists'] = True
        
        # 检查国债数据
        bond_files = {'CN': 'china_bond_simple.csv', 'US': 'us_bond_simple.csv', 'UK': 'uk_bond_simple.csv'}
        for country, filename in bond_files.items():
            filepath = os.path.join(base_dir, 'financial_data', filename)
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                row = df[df['timestamp'] == date]
                if not row.empty:
                    result['bonds'][country] = float(row.iloc[0]['close'])
        
        # 检查新闻数据
        gdelt_file = os.path.join(base_dir, '..', 'gdelt_data', 'gdelt_data.csv')
        if os.path.exists(gdelt_file):
            df = pd.read_csv(gdelt_file)
            day_str = date.replace('-', '')
            day_data = df[df['day'].astype(str) == day_str]
            
            for _, row in day_data.iterrows():
                country = row['country']
                result['news'][country] = {
                    'count': int(row['news_count']),
                    'tone': float(row['avg_tone'])
                }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"获取历史数据错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-data-dates', methods=['GET'])
def get_data_dates():
    """获取所有有数据的日期"""
    try:
        all_dates = set()
        base_dir = os.path.dirname(__file__)
        
        # 检查所有汇率文件
        forex_pairs = ['USD_CNY', 'USD_GBP', 'CNY_USD', 'GBP_CNY', 'GBP_USD', 'CNY_GBP']
        for pair in forex_pairs:
            filepath = os.path.join(base_dir, 'financial_data', f"{pair.lower()}.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                all_dates.update(df['timestamp'].tolist())
        
        # 排序日期
        sorted_dates = sorted(list(all_dates))
        
        # 检查每个日期的数据完整性
        result = []
        for date in sorted_dates:
            date_info = {'date': date, 'complete': True}
            
            # 检查是否所有货币对都有数据
            for pair in forex_pairs:
                filepath = os.path.join(base_dir, 'financial_data', f"{pair.lower()}.csv")
                if os.path.exists(filepath):
                    df = pd.read_csv(filepath)
                    if df[df['timestamp'] == date].empty:
                        date_info['complete'] = False
                        break
                else:
                    date_info['complete'] = False
                    break
            
            result.append(date_info)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"获取数据日期错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 如果启用了自动交易，设置调度任务
    if trading_manager and trading_manager.data['auto_trade_enabled']:
        schedule.every().day.at(trading_manager.data['auto_trade_time']).do(auto_trade_job)
    
    print("启动Flask服务器...")
    print(f"预测器状态: {'已初始化' if predictor else '未初始化'}")
    print(f"交易管理器状态: {'已初始化' if trading_manager else '未初始化'}")
    
    if predictor:
        print(f"可用货币对: {list(predictor.currency_dict.keys())}")
        print(f"数据日期范围: {predictor.common_dates[0]} 到 {predictor.common_dates[-1]}" if predictor.common_dates else "无数据")
    
    app.run(debug=True, port=5001)