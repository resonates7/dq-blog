# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 14:56:56 2021

@author: reson
"""

import os
import pandas as pd
import numpy as np
from eod import EodHistoricalData
from random import randint
from datetime import datetime
import time
api_key=os.environ['EOD_API_TOKEN']
free_api_key='OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX'

ticker='AAPL'
from_date='2021-09-01'
to_date='2021-09-14'
interval='d'



'''
These are old query strings

#query_string=f'https://eodhistoricaldata.com/api/eod/{ticker}.US?from={from_date}&to={to_date}&period={interval}&api_token={api_key}'
query_string=f'https://eodhistoricaldata.com/api/eod/{ticker}.US?from={from_date}&to={to_date}&period={interval}&api_token={api_key}&fmt=json'
query_string='http://eodhistoricaldata.com/api/fundamentals/AAPL.US?api_token=OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX&filter=General::Code,General,Earnings&fmt=json'


df = pd.read_json(query_string)
'''

#query string for fundamental data
query_string=f'https://eodhistoricaldata.com/api/fundamentals/{ticker}.US?api_token={api_key}&filter=Financials::Income_Statement::yearly'

print('QUERY STRING =\n\n',query_string)
df = pd.read_json(query_string)

print(api_key)
