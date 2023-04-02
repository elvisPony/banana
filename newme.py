#
import pandas_datareader.data as web
import pandas as pd

# 定義需要研究的公司和每家公司的事件日
tickers = ['ACN','ATVI','ADBE','AMZN','AXP','AAPL','ADSK',
          'BA','C','NET','K','DIS','EA','GME','GOOGL','INTC','IVZ',
           'JPM','MA','MTCH','MTTR','MCD','META','MSFT','MS','NKE','NVDA',
            'ORCL','PYPL','PEP','QCOM','RBLX','CRM','SBUX','TWLO','UAA','U',
             'V','WMT','WBD'] # 代表要研究的40家公司

event_dates = {'ACN': '2022-12-14', 'ATVI': '2022-01-18', 'ADBE': '2022-03-15', 'AMZN': '2021-12-02', 
               'AXP': '2022-03-16', 'AAPL': '2021-10-12', 'ADSK': '2021-08-10', 'BA': '2021-12-17', 'C': '2022-06-22', 
               'NET': '2021-10-01', 'K': '', 'DIS': '', 'EA': '', 'GME': '', 'GOOGL': '', 'INTC': '', 'IVZ': '',
                'JPM': '', 'MA': '', 'MTCH': '', 'MTTR': '', 'MCD': '', 'META': '', 'MSFT': '2022-01-18', 
                'MS': '', 'NIKE': '2021-12-13', 'NVDA': '', 'ORCL': '', 
                'PYPL': '', 'PEP': '', 'QCOM': '', 'RBLX': '2021-08-17', 'CRM': '', 'SBUX': '', 'TWLO': '', 
                'UAA': '', 'U': '', 'V': '', 'WMT': '', 'WBD': ''} # 每家公司的事件日

# 獲取羅素3000指數的收益率數據
start_date = '2000-01-01'
end_date = '2022-03-01'
R3000 = web.DataReader('^RUA', 'yahoo', start_date, end_date)['Adj Close']
R3000_return = R3000.pct_change().dropna() # 計算收益率並刪除缺失值

# 獲取每家公司的股票價格數據，並計算每家公司的超額收益率
all_returns = pd.DataFrame()
for ticker in tickers:
    event_date = event_dates[ticker]
    stock_data = web.DataReader(ticker, 'yahoo', event_date, end_date)['Adj Close']
    stock_return = stock_data.pct_change().dropna()
    exc_return = stock_return - R3000_return
    all_returns[ticker] = exc_return
    
# 確保每家公司的收益率數據長度相同
min_len = min([len(all_returns[ticker]) for ticker in tickers])
all_returns = all_returns.iloc[-min_len:]

# 保存每家公司的超額收益率數據
all_returns.to_csv('company_returns.csv')
