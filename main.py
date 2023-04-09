# %%
import os
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
from sklearn.linear_model import LinearRegression
from scipy.stats import ttest_1samp
from numpy.random import normal
russell3000_file_path = './RUA_new.csv'

stocks_company = ['ACN', 'ATVI', 'ADBE', 'AMZN', 'AXP', 'AAPL', 'ADSK',
                  'BA', 'C', 'NET', 'K', 'DIS', 'EA', 'GME', 'GOOGL', 'INTC', 'IVZ',
                  'JPM', 'MA', 'MTCH', 'MTTR', 'MCD', 'META', 'MSFT', 'MS', 'NKE', 'NVDA',
                  'ORCL', 'PYPL', 'PEP', 'QCOM', 'RBLX', 'CRM', 'SBUX', 'TWLO', 'UAA', 'U',
                  'V', 'WMT', 'WBD']

stocks_event_date = {'ACN': '2022-12-14', 'ATVI': '2022-01-18',
                     'ADBE': '2022-03-15', 'AMZN': '2021-12-02',
                     'AXP': '2022-03-16', 'AAPL': '2022-01-27',
                     'ADSK': '2021-08-10', 'BA': '2021-12-17',
                     'C': '2022-06-22', 'NET': '2021-10-01',
                     'K': '2022-04-04', 'DIS': '2021-11-10',
                     'EA': '2023-01-31', 'GME': '2021-10-26',
                     'GOOGL': '2022-01-05', 'INTC': '2021-12-14',
                     'IVZ': '2022-08-22',  'JPM': '2022-02-15',
                     'MA': '2023-02-22', 'MTCH': '2021-11-05',
                     'MTTR': '2022-01-21', 'MCD': '2022-02-10',
                     'META': '2021-10-28', 'MSFT': '2022-01-18',
                     'MS': '2021-11-17', 'NKE': '2021-12-13',
                     'NVDA': '2021-04-12', 'ORCL': '2022-10-18',
                     'PYPL': '2022-10-26', 'PEP': '2021-12-10',
                     'QCOM': '2022-03-21', 'RBLX': '2022-11-01',
                     'CRM': '2022-06-09', 'SBUX': '2022-09-12',
                     'TWLO': '2022-04-05', 'UAA': '2021-12-22',
                     'U': '2021-11-09', 'V': '2021-08-23',
                     'WMT': '2022-09-26', 'WBD': '2022-10-26'}

stocks_company_total_data = {}

IT_COMPANY = []
NON_IT_CONPANY = []

ESTIMATION_DAY = 201
ESTIMATION_DATE_LEN = 314
OFFSET_DAY = 19
EVENT_STUDY_TOTAL_DAY = 22
EVENT_NUMVER = 40


def process_string_time_to_datetime(date: str):
    temp = date.split('-')
    event_date = datetime.datetime(int(temp[0]), int(temp[1]), int(temp[2]))
    return event_date


def compute_estimation_data(event_start_date):
    event_start_date = process_string_time_to_datetime(event_start_date)
    # ESTIMATION_DATE_LEN = ESTIMATION_DAY + 3 + 100
    # +3是為讓評估資料結束日期不等於事件日開始日期， +80 是為了扣掉假日的緩沖期
    estimation_start_date = compute_difference(
        event_start_date, ESTIMATION_DATE_LEN)

    estimation_end_date = compute_difference(event_start_date, 3)

    return estimation_start_date, estimation_end_date


def compute_start_date_and_end_date(date, offset):
    start_date = date + datetime.timedelta(days=-offset)
    start_date = start_date.strftime("%Y-%m-%d")

    end_date = date + datetime.timedelta(days=offset)
    end_date = end_date.strftime("%Y-%m-%d")
    return start_date, end_date


def compute_difference(date, difference):
    difference_date = date + datetime.timedelta(days=-difference)
    difference_date = difference_date.strftime("%Y-%m-%d")

    return difference_date


def standardization(data, mu, sigma):
    return (data - mu) / sigma


def interval_data(data, start_date, end_date, event_date, interval):
    if len(data.loc[start_date:event_date]) > (interval+1):
        decrease = len(data.loc[start_date:event_date]) - (interval+1)
        data = data.iloc[decrease:]

    if len(data.loc[event_date:end_date]) > interval:
        decrease = len(data.loc[event_date:end_date]) - interval
        data = data.iloc[:-decrease]

    if len(data) != (interval * 2):
        print(len(data))
        raise ("資料長度不正確")
    return data


def main():
    # 讀取全部 russell3000資料 ，預期正常的報酬

    russell3000 = pd.read_csv(russell3000_file_path,
                              index_col=0, parse_dates=True)
    russell3000_close = russell3000['Close']
    russell3000_returns = russell3000_close.pct_change()
    #temp = russell3000.index.tolist()
    # 撈取每家公司的資料
    # print(len(stocks_company))
    # print(len(stocks_event_date))
    for stocks in stocks_company:
        if stocks_event_date[stocks] == "":
            continue
        total_calculate_data = {}

        # 根據事件日，前後10天，找出收盤資料
        event_date = stocks_event_date[stocks]
        event_datetime = process_string_time_to_datetime(event_date)
        start_date, end_date = compute_start_date_and_end_date(
            event_datetime, OFFSET_DAY)

        data = yf.download(stocks, start=start_date, end=end_date)

        data = interval_data(data, start_date, end_date, event_date, 11)

        if len(data) != EVENT_STUDY_TOTAL_DAY:
            print(len(data))
            raise ("資料長度不正確")

        # 利用線性回歸模型，與估計期為兩百天的資料，找出投資報酬率的預測值
        estimation_start_date, estimation_end_date = compute_estimation_data(
            start_date)
        x_estimation_data = yf.download(stocks, start=estimation_start_date,
                                        end=estimation_end_date)

        print(len(x_estimation_data))
        if len(x_estimation_data) < ESTIMATION_DAY:
            raise("資料長度不足")
        x_estimation_data = x_estimation_data.iloc[(
            len(x_estimation_data)-ESTIMATION_DAY):]
        if len(x_estimation_data) != ESTIMATION_DAY:
            raise('資料長度錯誤')

        x_estimation_data = x_estimation_data['Close']
        x_estimation_data = x_estimation_data.pct_change()
        x_estimation_data = x_estimation_data.to_numpy()[1:]
        x_estimation_data = x_estimation_data.reshape(
            len(x_estimation_data), 1)

        y_estimation_data = russell3000_returns.loc[estimation_start_date:estimation_end_date]
        y_estimation_data = y_estimation_data.iloc[(
            len(y_estimation_data)-ESTIMATION_DAY):]
        y_estimation_data = y_estimation_data.to_numpy()[1:]
        if len(y_estimation_data) != ESTIMATION_DAY-1:
            raise("資料長度錯誤")
        y_estimation_data = y_estimation_data.reshape(
            len(y_estimation_data), 1)

        model = LinearRegression()
        model.fit(x_estimation_data, y_estimation_data)

        # 算取公司的實際報酬
        data = data['Close']
        data = data.pct_change()
        data = data.iloc[1:]
        data_numpy = data.to_numpy()

        # 算出異常報酬
        data_start_day = data.index.to_list()[0]
        data_end_day = data.index.to_list()[-1]
        russell3000_x = russell3000_returns.loc[data_start_day:data_end_day]
        russell3000_x = russell3000_x.to_numpy()
        russell3000_predict = model.predict(
            russell3000_x.reshape(len(russell3000_x), 1))
        russell3000_predict = russell3000_predict.reshape(
            russell3000_predict.shape[0])
        abnormal = data_numpy - russell3000_predict
        total_calculate_data["abnormal"] = abnormal

        # 算出累積異常報酬
        accumulation_abnormal = []
        for it in abnormal:
            if len(accumulation_abnormal) == 0:
                accumulation_abnormal.append(it)
            else:
                accumulation_abnormal.append(accumulation_abnormal[-1]+it)

        total_calculate_data["accumulation_abnormal"] = accumulation_abnormal
        print(f"{stocks} 累積異常報酬: {accumulation_abnormal}")

        # 算出累積平均異常報酬
        accumulation_abnormal_mean = abnormal.mean()
        total_calculate_data['accumulation_abnormal_mean'] = accumulation_abnormal_mean

        # 標準化異常報酬

        standard_deviation_abnormal = abnormal.std()
        total_calculate_data['standard_deviation_abnormal'] = standard_deviation_abnormal
        standardization_abnormal = []
        for data in abnormal:
            temp = standardization(
                data, accumulation_abnormal_mean, standard_deviation_abnormal)
            standardization_abnormal.append(temp)
        total_calculate_data['standardization_abnormal'] = standardization_abnormal

        # 標準化平均異常報酬
        total = 0
        for it in standardization_abnormal:
            total += it
        standardization_abnormal_mean = total / len(standardization_abnormal)
        total_calculate_data['standardization_abnormal_mean'] = standardization_abnormal_mean
        pass

        # T 檢定 (傳統法)
        temp = []

        sample = normal(150, 10, 20)
        t_stat, p_value = ttest_1samp(sample, popmean=155)
        print("T-statistic value: ", t_stat)
        print("P-Value: ", p_value)
        for it in russell3000_predict:
            t_stat, p_value = ttest_1samp(abnormal, popmean=it)
            temp.append([t_stat, p_value])
        print('')

        # T 檢定 (標準殘插法)

        # 無母數檢定

        stocks_company_total_data[stocks] = total_calculate_data
    pass


def test():
    pass


if __name__ == '__main__':
    main()

# %%
