# %%
import os
import pandas as pd
import numpy as np
import yfinance as yf
import datetime


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
                     'MS': '', 'NKE': '2021-12-13',
                     'NVDA': '', 'ORCL': '',
                     'PYPL': '', 'PEP': '',
                     'QCOM': '', 'RBLX': '2021-08-17',
                     'CRM': '', 'SBUX': '',
                     'TWLO': '', 'UAA': '',
                     'U': '', 'V': '',
                     'WMT': '', 'WBD': ''}


IT_COMPANY = []
NON_IT_CONPANY = []


OFFSET_DAY = 19
EVENT_STUDY_TOTAL_DAY = 21


def process_string_time_to_datetime(date: str):
    temp = date.split('-')
    event_date = datetime.datetime(int(temp[0]), int(temp[1]), int(temp[2]))
    return event_date


def compute_start_date_and_end_date(date, offset):
    start_date = date + datetime.timedelta(days=-offset)
    start_date = start_date.strftime("%Y-%m-%d")

    end_date = date + datetime.timedelta(days=offset)
    end_date = end_date.strftime("%Y-%m-%d")
    return start_date, end_date


def compute_difference(date, difference):
    difference_date = date + datetime.timedelta(days=difference)
    difference_date = difference_date.strftime("%Y-%m-%d")

    return difference_date


def standardization(data, mu, sigma):
    return (data - mu) / sigma


def interval_data(data, start_date, end_date, event_date, interval):
    if len(data.loc[start_date:event_date]) > interval:
        decrease = len(data.loc[start_date:event_date]) - interval
        data = data.iloc[decrease:]

    if len(data.loc[event_date:end_date]) > interval:
        decrease = len(data.loc[event_date:end_date]) - interval
        data = data.iloc[:-decrease]

    if len(data) != (interval * 2 - 1):
        print(len(data))
        raise ("資料長度不正確")
    return data


def main():
    # 讀取全部 russell3000資料 ，預期正常的報酬

    russell3000_file_path = './RUA_v2.csv'
    russell3000 = pd.read_csv(russell3000_file_path,
                              index_col=0, parse_dates=True)
    russell3000_close = russell3000[' Close']
    russell3000_returns = russell3000_close.pct_change()
    temp = russell3000.index.tolist()
    # 撈取每家公司的資料
    # print(len(stocks_company))
    # print(len(stocks_event_date))
    for stocks in stocks_company:
        if stocks_event_date[stocks] == "":
            continue

        # 根據事件日，前後10天，找出收盤資料
        event_date = stocks_event_date[stocks]
        event_datetime = process_string_time_to_datetime(event_date)
        start_date, end_date = compute_start_date_and_end_date(
            event_datetime, OFFSET_DAY)

        data = yf.download(stocks, start=start_date, end=end_date)

        data = interval_data(data, start_date, end_date, event_date, 11)

        if len(data) != 21:
            print(len(data))
            raise ("資料長度不正確")

        # 算取公司的實際報酬
        data = data['Close']
        data = data.pct_change()

        # 算出異常報酬
        end_date_temp = process_string_time_to_datetime(end_date)
        russell3000_temp = russell3000_returns.loc[start_date:compute_difference(
            end_date_temp, -1)]
        abnormal = data - russell3000_temp
        abnormal.fillna(0, inplace=True)

        print("")

        # 算出累積異常報酬
        accumulation_abnormal = abnormal.sum()
        print(f"{stocks} 累積異常報酬: {accumulation_abnormal}")

        # 算出累積平均異常報酬
        abnormal_numpy = abnormal.to_numpy()[1:]
        accumulation_abnormal_mean = abnormal_numpy.mean()

        # 標準化異常報酬

        standard_deviation_abnormal = abnormal_numpy.std()
        standardization_abnormal = []
        for data in abnormal_numpy:
            temp = standardization(
                data, accumulation_abnormal_mean, standard_deviation_abnormal)
            standardization_abnormal.append(temp)

        # 標準化平均異常報酬
        total = 0
        for it in standardization_abnormal:
            total += it
        standardization_abnormal_mean = total / len(standardization_abnormal)
        pass

        # T 檢定 (傳統法)

        # T 檢定 (標準殘插法)

        # 無母數檢定

    pass


def test():
    pass


if __name__ == '__main__':
    main()
