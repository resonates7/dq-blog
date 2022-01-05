# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 16:30:09 2021

@author: reson

This code is from this YouTube vid showing how to access yahoo fiance api
https://www.youtube.com/watch?v=NjEc7PB0TxQ


"""

import time
import datetime
import pandas as pd

ticker = 'TSLA'
period1 = int(time.mktime(datetime.datetime(2021, 12, 1, 23, 59).timetuple()))
period2 = int(time.mktime(datetime.datetime(2021, 12, 14, 23, 59).timetuple()))
interval = '1d' # 1d, 1m

query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'

df_yahoo = pd.read_csv(query_string)
# print(df)
#df.to_csv('AAPL.csv')
df_yahoo['Date']=pd.to_datetime(df_yahoo['Date'])






