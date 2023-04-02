# %%
import os
import pandas as pd
import numpy as np
import yfinance as yf

# %% Define the event window
event_date = '2021-10-27'
start_date = pd.to_datetime(event_date) - pd.DateOffset(days=30)
end_date = pd.to_datetime(event_date) + pd.DateOffset(days=30)

# %%Load the stock data
stocks_company = ['ACN', 'ATVI', 'ADBE', 'AMZN', 'AXP', 'AAPL', 'ADSK',
                  'BA', 'C', 'NET', 'K', 'DIS', 'EA', 'GME', 'GOOGL', 'INTC', 'IVZ',
                  'JPM', 'MA', 'MTCH', 'MTTR', 'MCD', 'META', 'MSFT', 'MS', 'NKE', 'NVDA',
                  'ORCL', 'PYPL', 'PEP', 'QCOM', 'RBLX', 'CRM', 'SBUX', 'TWLO', 'UAA', 'U',
                  'V', 'WMT', 'WBD']
stocks_event_date = {'ACN': '2022-12-14', 'ATVI': '2022-01-18',
                     'ADBE': '2022-03-15', 'AMZN': '2021-12-02',
                     'AXP': '2022-03-16', 'AAPL': '2021-10-12',
                     'ADSK': '2021-08-10', 'BA': '2021-12-17',
                     'C': '2022-06-22', 'NET': '2021-10-01',
                     'K': '2022-04-04', 'DIS': '2021-11-10',
                     'EA': '', 'GME': '',
                     'GOOGL': '', 'INTC': '',
                     'IVZ': '',  'JPM': '',
                     'MA': '', 'MTCH': '',
                     'MTTR': '', 'MCD': '',
                     'META': '', 'MSFT': '2022-01-18',
                     'MS': '', 'NIKE': '2021-12-13',
                     'NVDA': '', 'ORCL': '',
                     'PYPL': '', 'PEP': '',
                     'QCOM': '', 'RBLX': '2021-08-17',
                     'CRM': '', 'SBUX': '',
                     'TWLO': '', 'UAA': '',
                     'U': '', 'V': '',
                     'WMT': '', 'WBD': ''}
data = yf.download(stocks, start=start_date, end=end_date)
prices_40_company = data['Adj Close']

# %%Change date format as yyyy-mm-dd


def not_use():
    # 讀取包含日期的 CSV 檔案
    file_path = '/Users/liyuen/Desktop/ANAPAPER/stocklist/RUA.csv'
    df = pd.read_csv(file_path)

    # 將日期轉換為指定格式
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y')
    df['Date'] = df['Date'].dt.strftime('%m/%d/%Y')

    # 保存轉換後的 DataFrame 到新的 CSV 檔案
    df.to_csv('RUA_v2.csv', index=False)


def not_use2():
    # 讀取 CSV 檔案
    file_path = './RUA_v2.csv'
    df = pd.read_csv(file_path)

    # 將日期欄位轉換為 datetime 格式，並指定日期格式
    # 因為RUA的檔案是到另外的網站上找的，所以日期格式有問題，故要先指定日期的格式
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

    # 將日期欄位格式化為 "年-月-日"
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

    # 儲存更改後的檔案
    df.to_csv('RUA_V2.csv', index=False)


# %%Load Russell 3000 index data
file_path = './RUA_v2.csv'
df = pd.read_csv(file_path)

# 在這段程式中，prices是一個Pandas DataFrame，裡面包含從Yahoo Finance下載的股票價格資料。
# 該DataFrame以日期作為行索引、以股票代碼作為列索引，以股票價格作為資料。
# 把Russell3000設為每日收盤價
prices = pd.read_csv(file_path, index_col=0, parse_dates=True)
russell3000 = pd.read_csv(file_path, index_col=0, parse_dates=True)


russell3000 = russell3000[' Close']
russell3000_returns = russell3000.pct_change()


# %%
# pct_change() 是Pandas中的一個函數，用於計算數據中相鄰元素的百分比變化。
# 在這個程式碼中，pct_change() 被用來計算Russell 3000指數的收益率。
# 具體來說，它計算了連續兩個交易日的收盤價的百分比變化，然後用這個百分比變化來表示這一天的收益率。
russell3000.columns = ['russell3000']
russell3000_returns = russell3000.pct_change()

# %%
# 檢查russell3000_returns中是否包含許多缺失值
print(russell3000_returns.isnull())
# 發現有缺失值，試著用0填上
df.fillna(0, inplace=True)
print(russell3000_returns)
# 後來發現只有第一筆資料是空值，其原因為他沒有前一天的資料跟他進行計算百分比變化


# %%Calculate the event returns
event_returns = prices_40_company.loc[event_date] / \
    prices_40_company.loc[pd.to_datetime(event_date) - pd.DateOffset(1)]

print(event_returns)

# %%
print(prices_40_company)

# %%
# 檢查event_returns是否包含許多缺失值
print(event_returns.isnull())


# %%Calculate the expected returns
benchmark = russell3000_returns
expected_returns = benchmark.loc[start_date:end_date].mean()

# %%
# 再次檢查event_returns是否包含許多缺失值
print(event_returns.isnull())


# %%Calculate the abnormal returns
abnormal_returns = event_returns - expected_returns

# %%
# 檢查abnormal returns是否包含許多缺失值
print(abnormal_returns.isnull())

# %%Calculate the cumulative abnormal returns
cumulative_abnormal_returns = abnormal_returns.cumsum()

# %%

# 將expected_returns轉換為numpy數據
expected_returns = np.array(expected_returns)

# 將expected_returns轉換為pandas序列
expected_returns = pd.Series(expected_returns)

# 使用 values属性
print('Expected returns (as numpy array):', expected_returns.values)
print('Expected returns (as pandas series):', expected_returns.values)

# 做這個更改是因為原先直接跑的時候發現他說Expected returns是一個浮點數，
# 而浮點數類型中沒有values屬性。
# 所以可以將其轉換為Numpy數組或Pandas序列後再使用values屬性

# %%Print the results
print('Event date:', event_date)
print('Event returns:', event_returns.values)
print('Expected returns:', expected_returns.values)
print('Abnormal returns:', abnormal_returns.values)
print('Cumulative abnormal returns:', cumulative_abnormal_returns.values)


# %%
# 這裡是為了查看檔案的正確路徑


path = '/Users/liyuen/Desktop/ANAPAPER/stocklist'

for root, dirs, files in os.walk(path):
    level = root.replace(path, '').count(os.sep)
    indent = ' ' * 4 * (level)
    print('{}{}/'.format(indent, os.path.basename(root)))
    subindent = ' ' * 4 * (level + 1)
    for file in files:
        print('{}{}'.format(subindent, file))
# %%
