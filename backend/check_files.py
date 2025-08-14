import os
import pandas as pd

print("=== 检查文件状态 ===\n")

# 检查当前目录
print(f"当前目录: {os.getcwd()}")
print(f"脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}\n")

# 检查financial_data文件夹
financial_data_path = os.path.join(os.path.dirname(__file__), 'financial_data')
print(f"financial_data文件夹是否存在: {os.path.exists(financial_data_path)}")

if os.path.exists(financial_data_path):
    print(f"financial_data中的文件:")
    for file in os.listdir(financial_data_path):
        if file.endswith('.csv'):
            filepath = os.path.join(financial_data_path, file)
            try:
                df = pd.read_csv(filepath)
                print(f"  - {file}: {len(df)} 行数据")
            except Exception as e:
                print(f"  - {file}: 读取错误 - {e}")

# 检查模型文件
print(f"\n模型文件:")
model_files = [
    'USD_CNY_GradientBoosting.pkl',
    'USD_GBP_GradientBoosting.pkl',
    'CNY_USD_LogisticRegression.pkl',
    'GBP_CNY_LogisticRegression.pkl',
    'GBP_USD_LogisticRegression.pkl',
    'CNY_GBP_RandomForest.pkl'
]

for model in model_files:
    model_path = os.path.join(os.path.dirname(__file__), model)
    exists = os.path.exists(model_path)
    print(f"  - {model}: {'✓ 存在' if exists else '✗ 不存在'}")

# 检查其他必要文件
print(f"\n其他文件:")
other_files = ['news_features.csv', 'forex_data_api.py', 'download_api.py', '11111.py']
for file in other_files:
    filepath = os.path.join(os.path.dirname(__file__), file)
    exists = os.path.exists(filepath)
    print(f"  - {file}: {'✓ 存在' if exists else '✗ 不存在'}")

# 检查gdelt_data文件夹
gdelt_path = os.path.join(os.path.dirname(__file__), '..', 'gdelt_data')
print(f"\ngdelt_data文件夹是否存在: {os.path.exists(gdelt_path)}")
if os.path.exists(gdelt_path):
    gdelt_file = os.path.join(gdelt_path, 'gdelt_data.csv')
    if os.path.exists(gdelt_file):
        try:
            df = pd.read_csv(gdelt_file)
            print(f"  - gdelt_data.csv: {len(df)} 行数据")
        except Exception as e:
            print(f"  - gdelt_data.csv: 读取错误 - {e}")