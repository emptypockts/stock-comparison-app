import pandas as pd
import financialUtils as fini
import logging
import os
import requests
from pandas import Series
from datetime import datetime,timedelta
from dotenv import load_dotenv
from typing import Literal
from pymongo.server_api import ServerApi
from pymongo import MongoClient,DESCENDING
load_dotenv()
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['test']
collection = db['rawEdgarCollection']
cik_collection=db['tickerCIK']

def format_currency(value):
    if value:
        return "${:,.2f}".format(value)
    else:
        return 0

def format_number(value):
    return "{:,.0f}".format(value)

def format_ratio(value):
    return "{:.2f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value * 100)
def check_market_cap(row):
    if 'market_cap' in row:
        return int(row['market_cap'] > 2e+09)
    return False

def fetch_5y_data(ticker):
    stock_data=[]
    metrics=[
    'WeightedAverageNumberOfSharesOutstandingBasic',
    'book_value',
    'fcf',
    'EarningsPerShareBasic',
    'EarningsPerShareDiluted',
    'total_debt',
    'PaymentsOfDividendsCommonStock',
    'pb_ratio',
    'pe_ratio',
    'debt_fcf_ratio',
    'dividend_yield',
    'earnings_yield',
    'market_cap',
    'price_close',
    'fcf_cagr'
    ]
    year= datetime.now().year
    for i in range(year-5,year+1):
        cursor=fini.fetch_metric(
            collection=collection,
            ticker=ticker,
            metric=metrics,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False)
        b={}
        if cursor:
            for a in cursor:
                b[a.get('metric')]=a.get('value',0)
                b['ticker']=a.get('ticker',"empty")
                b['entity']=a.get('entity',"empty")
                b['date']=a.get('date')
            stock_data.append(b)

    combined_df= pd.DataFrame(stock_data)
    # Calculate metrics
    combined_df['market_cap_score'] = combined_df.apply(check_market_cap, axis=1)
    if 'pe_ratio' in combined_df.columns:
        combined_df['pe_ratio_score'] = int(combined_df['pe_ratio'].mean() < 15)
    if 'pe_ratio' not in combined_df.columns:
        combined_df['pe_ratio_score']=0
    if 'pb_ratio' in combined_df.columns:
        combined_df['pb_ratio_score'] = int(combined_df['pb_ratio'].mean() < 2)
    if 'pb_ratio' not in combined_df.columns:
        combined_df['pb_ratio_score']=0
    if 'debt_fcf_ratio' in combined_df.columns:
        combined_df['sum_debt_fcf_ratio_score'] = int(combined_df['debt_fcf_ratio'].sum() > 0)
    if 'debt_fcf_ratio' not in combined_df.columns:
        combined_df['sum_debt_fcf_ratio_score'] =0
    if 'earnings_yield' in combined_df.columns:
        combined_df['earnings_yield_score'] = int(combined_df['earnings_yield'].gt(0).all())
        initial_value = combined_df['earnings_yield'].iloc[-1]
        last_value = combined_df['earnings_yield'].iloc[0]
        if not pd.isna(initial_value) and initial_value!=0:
            growth = (last_value - initial_value) / abs(initial_value)
        else:
            growth=0
    # Check if the growth is greater than or equal to 1.3x (130%)
        combined_df['1.3x_earnings_yield_score'] = int (growth >= 1.3)
    if 'earnings_yield' not in combined_df.columns:
        combined_df['1.3x_earnings_yield_score']=0
        combined_df['earnings_yield_score'] =0
    if 'dividend_yield' in combined_df.columns:
        combined_df['dividend_yield_score'] = int(combined_df['dividend_yield'].gt(0).all())
    if 'dividend_yield' not in combined_df.columns:
        combined_df['dividend_yield_score'] =0
    combined_df['total_score'] = combined_df['dividend_yield_score'] + \
        combined_df['earnings_yield_score'] + combined_df['1.3x_earnings_yield_score']\
        + combined_df['sum_debt_fcf_ratio_score'] + combined_df['pb_ratio_score']\
            + combined_df['pe_ratio_score'] + combined_df['market_cap_score']

    # remove $nan for 0
    combined_df=combined_df.fillna(0.001)
    # Formats
    if 'WeightedAverageNumberOfSharesOutstandingBasic' in combined_df.columns:
        combined_df['WeightedAverageNumberOfSharesOutstandingBasic'] = combined_df['WeightedAverageNumberOfSharesOutstandingBasic'].apply(format_number)
    if 'book_value' in combined_df.columns:
        combined_df['book_value'] = combined_df['book_value'].apply(format_currency)
    if 'fcf' in combined_df.columns:
        combined_df['fcf'] = combined_df['fcf'].apply(format_currency)
    if 'EarningsPerShareBasic' in combined_df.columns:
        combined_df['EarningsPerShareBasic'] = combined_df['EarningsPerShareBasic'].apply(format_currency)
    if 'EarningsPerShareDiluted' in combined_df.columns:
        combined_df['EarningsPerShareDiluted'] = combined_df['EarningsPerShareDiluted'].apply(format_currency)
    if 'total_debt' in combined_df.columns:
        combined_df['total_debt'] = combined_df['total_debt'].apply(format_currency)
    if 'PaymentsOfDividendsCommonStock' in combined_df.columns:
        combined_df['PaymentsOfDividendsCommonStock'] = combined_df['PaymentsOfDividendsCommonStock'].apply(format_currency)
    if 'price_close' in combined_df.columns:
        combined_df['price_close'] = combined_df['price_close'].apply(format_currency)
    if 'pb_ratio' in combined_df.columns:    
        combined_df['pb_ratio'] = combined_df['pb_ratio'].apply(format_ratio)
    if 'pe_ratio' in combined_df.columns:
        combined_df['pe_ratio'] = combined_df['pe_ratio'].apply(format_ratio)
    if 'debt_fcf_ratio' in combined_df.columns:
        combined_df['debt_fcf_ratio'] = combined_df['debt_fcf_ratio'].apply(format_ratio)
    if 'dividend_yield' in combined_df.columns:
        combined_df['dividend_yield'] = combined_df['dividend_yield'].apply(format_percentage)
    if 'earnings_yield' in combined_df.columns:
        combined_df['earnings_yield'] = combined_df['earnings_yield'].apply(format_percentage)
    if 'market_cap' in combined_df.columns:
        combined_df['market_cap'] = combined_df['market_cap'].apply(format_currency)

    
    return combined_df
# Example function call
if __name__ == "__main__":
    # tickers=['AXP','MSFT','NVDA']
    tickers= fini.fetch_tickers(collection=cik_collection)
    json_obj=[]
    
    for ticker in tickers:
        response=fetch_5y_data(ticker)
        for idx,e in response.iterrows():
            json_obj.append(dict(e))
    print(json_obj)
    fini.push_StockData(db,json_obj,'StockScore')

            
