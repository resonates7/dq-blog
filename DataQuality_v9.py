# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 19:37:25 2021

@author: reson
"""

import os
import sys
import pandas as pd
import numpy as np
import time 
#import datetime
import datetime
import yahoo_fin.stock_info as yf
from pandas.tseries.offsets import YearEnd
api_key=os.environ['EOD_API_TOKEN']


def ValidateStockPrices(source):
    '''
    
    Parameters
    ----------
    Source : input a csv file
    
    Compares price and volume data from EOD database to data from
    the Yahoo finance unofficial api
            
    Returns
    -------
    Data frame listing both data sources side by side along with a comparison
    data frame using pandas .compare function.

    '''
 
    # define empty df to house eod data
    yahoo_df=pd.DataFrame()
    
    for index, row in source.iterrows():
        a=row.tolist()
        #print(a)
        #unpack source 
        ticker, from_date, to_date, interval = a
        
        #convert dates to yahoo finance format
        to_date=int(time.mktime(datetime.datetime.strptime(to_date, "%Y-%m-%d").timetuple()))
        from_date=int(time.mktime(datetime.datetime.strptime(from_date, "%Y-%m-%d").timetuple()))
        
        # fetch data
        query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={from_date}&period2={to_date}&interval={interval}&events=history&includeAdjustedClose=true'
        
        df = pd.read_csv(query_string)
        df['ticker']=ticker
        yahoo_df=yahoo_df.append(df)
        
    
    eod_df=pd.DataFrame()
    
    for index, row in source.iterrows():
        a=row.tolist()
        #print(a)
        # unpack source 
        ticker, from_date, to_date, interval = a
        to_date=datetime.datetime.strptime(to_date, "%Y-%m-%d")
        to_date+=datetime.timedelta(days=-1)
        to_date=to_date.strftime("%Y-%m-%d")
        
        
        # fetch data
        query_string=f'https://eodhistoricaldata.com/api/eod/{ticker}.US?from={from_date}&to={to_date}&period={interval}&api_token={api_key}&fmt=json'
        #print(query_string)
        
        df = pd.read_json(query_string)
        df['ticker']=ticker
        eod_df=eod_df.append(df)
    
    #establish common labels for comparison
    yahoo_df['Date']=pd.to_datetime(yahoo_df['Date'])
    eod_df.set_index(['date', 'ticker'], inplace=True)
    yahoo_df.rename_axis(index={'Index':'date'}, inplace=True)

    yahoo_df=yahoo_df.reset_index()
    yahoo_df.rename(columns={'Date':'date', 'Open':'open', 'High':'high',
                              'Low':'low', 'Close':'close', 'Adj Close':'adjusted_close',
                              'Volume':'volume'}, inplace=True)
    yahoo_df.set_index(['date', 'ticker'], inplace=True) 
    yahoo_df.drop('index', axis=1, inplace=True)
    
    #round values
    yahoo_df=yahoo_df.round(2)
    eod_df=eod_df.round(2)
    #round volumes to thousands
    yahoo_df['volume']=yahoo_df['volume'].round(-3)
    eod_df['volume']=eod_df['volume'].round(-3)
    
    #run comparison
    #TODO Check comparison
    
    comparison=eod_df.compare(yahoo_df)
    #export error reports
    if len(comparison) != 0:
        writer=pd.ExcelWriter(r'C:\Users\reson\Documents\GitHub\100Baggers\Error_Reports\ValStockPriceComparison.xlsx',
                              engine='xlsxwriter')
        comparison.to_excel(writer, sheet_name='Comparison')
        eod_df.to_excel(writer, sheet_name='eod_df')
        yahoo_df.to_excel(writer, sheet_name='yahoo_df')
        writer.save()
        print("Errors detected. Error spreadsheets export to Error_reports folder")
  
   
    
    return eod_df, yahoo_df, comparison
        
def ValidateFinStmt(mapping, source, time_period):
    '''
    
    Parameters
    ----------
    This function uses scrapped data returned by the yahoo_fin API. This 
    doesn't work 100% correctly, but it's very difficult to find a match 
    b/t any published source as I've explained in my blog post.        
    
    INPUT: 
        Mapping: mapping excel file cross referencing EOD Historical Data
        column names to yahoo finance names. 
    
    Compares the Financial statement from seeking alpha to the one from EOD
    Data
   
            
    Returns
    -------
   Data frame listing the differences between the two statements with EOD data
       as self and the seeking alpha statement as other.
   '''

    #create EOD dataframe
    
    eod_df=pd.DataFrame()    
    for index, row in source.iterrows():
        a=row.tolist()
        #print(a)
        # unpack source 
        ticker, from_date, to_date, interval = a            
        
        # fetch data
        query_string=f'https://eodhistoricaldata.com/api/fundamentals/{ticker}.US?api_token={api_key}&filter=Financials::Income_Statement::{time_period}'
        #print(query_string)
        
        df = pd.read_json(query_string)
        df.columns=pd.DatetimeIndex(df.columns)
        df.columns=df.columns.to_period('Y')
        df['ticker']=ticker
        eod_df=eod_df.append(df)
   
    yahoo_df=pd.DataFrame()
    
    for index, row in source.iterrows():
        a=row.tolist()
        #print(a)
        #unpack source 
        ticker, from_date, to_date, interval = a
        
        #convert dates to yahoo finance format
        # to_date=int(time.mktime(datetime.strptime(to_date, "%Y-%m-%d").timetuple()))
        # from_date=int(time.mktime(datetime.strptime(from_date, "%Y-%m-%d").timetuple()))
        
        # fetch data
       
        df = yf.get_income_statement(ticker)
        df.columns=pd.DatetimeIndex(df.columns)
        df.columns=df.columns.to_period('Y')
        df['ticker']=ticker
        yahoo_df=yahoo_df.append(df)
        
        ##establish common labels for comparison
    mapping=pd.read_excel(mapping,header=0, sheet_name='Mapping')
    map_dict=dict(zip(mapping['EOD_name'], mapping['Yahoo_name']))
    eod_df['map name']=eod_df.index.map(map_dict)
    yahoo_df['map name']=yahoo_df.index.map(map_dict)
    
    eod_df = eod_df[eod_df['map name'].notna()]
    yahoo_df = yahoo_df[yahoo_df['map name'].notna()]
    eod_df.drop('map name', axis=1, inplace=True)
    yahoo_df.drop('map name', axis=1, inplace=True)
    yahoo_df=yahoo_df.reset_index()
    eod_df=eod_df.reset_index()
    yahoo_df.rename(columns={'Breakdown':'labels'}, inplace=True)
    eod_df.rename(columns={'index':'labels'}, inplace=True)
    yahoo_df.set_index(['labels', 'ticker'], inplace=True) 
    eod_df.set_index(['labels', 'ticker'], inplace=True) 
    
    #Create a list of differences in the dates b/t the two statements
    a=eod_df.columns#.tolist()
    b=yahoo_df.columns#.tolist()
    b=b.sort_values(ascending=False)
    #c is the difference b/t the two groups
    c=(set(a)-set(b))
    date_diff=list(c)
    # # remove the map name from date diff b/c it is non a number
    # date_diff.remove('map name')
    
    #Now remove the different dates from EOD Data Frame
    #EOD data should have more dates than alpha
    for each in range(len(date_diff)):
        #print(date_diff[each])
        eod_df.drop([date_diff[each]], axis=1, inplace=True)
    
    eod_df=eod_df.apply(pd.to_numeric)
    comparison=eod_df.compare(yahoo_df)
    
    
    if len(comparison) != 0:
       writer=pd.ExcelWriter(r'C:\Users\reson\Documents\GitHub\100Baggers\Error_Reports\ValidateFinStmtComparison.xlsx',
                              engine='xlsxwriter')
       comparison.to_excel(writer, sheet_name='Comparison')
       eod_df.to_excel(writer, sheet_name='eod_df')
       yahoo_df.to_excel(writer, sheet_name='yahoo_df')
       writer.save()
       print("Errors detected. Error spreadsheets export to Error_reports folder")
    

    
    return comparison, eod_df, yahoo_df

# source = pd.read_csv('ticks.txt')
# mapping='Mapping_Yahoo_to_EOD.xlsx'
# eod_df, yahoo_df, comparison = ValidateStockPrices(source)   


def main(script):
    """Tests the functions in this module.

    script: string script name
    """
    mapping='Mapping_Yahoo_to_EOD.xlsx'
    source = pd.read_csv('ticks.txt')
    eod_df, yahoo_df, comparison_price = ValidateStockPrices(source)
    comparison_stmt, eod_df, yahoo_df = ValidateFinStmt(mapping, source, 'yearly')  
    
    assert(len(comparison_stmt) == 0), 'Errors detected in ValidateFinStmt, logs exported'
    #next line won't run if the above errors out
    assert(len(comparison_price) == 0), 'Errors detected in ValidateStockPrices, logs exported'

    print('%s: All tests passed.' % script)


if __name__ == '__main__':
    main(*sys.argv)





