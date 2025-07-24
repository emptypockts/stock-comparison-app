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

def format_currency(value):
    return "${:,.2f}".format(value)

def format_number(value):
    return "{:,.0f}".format(value)

def format_ratio(value):
    return "{:.2f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value * 100)
def check_market_cap(row):
    return int(row['market_cap'] > 2e+09)


def fetch_5y_data(ticker):
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
    'market_cap'
    ]
    price_5y=fini.fetch_price_fmp(ticker,mode='5y')
    cursor=fini.fetch_metric(
        collection=collection,
        ticker=ticker,
        metric=metrics,
        mode='all',
        unique_metric=False)
    b={}
    for a in cursor:
        year =datetime.fromisoformat(a.get('date')).year
        pps=float(price_5y['close'].get(year))
        b[a.get('metric')]=a.get('value')
        b['ticker']=a.get('ticker')
        b['entity']=a.get('entity')
        b['date']=a.get('date')
        b['price_per_share']=pps
        object.append(b)

    combined_df= pd.DataFrame(object)

    # Calculate metrics
    combined_df['market_cap_score'] = combined_df.apply(check_market_cap, axis=1)
    combined_df['pe_ratio_score'] = int(combined_df['pe_ratio'].mean() < 15)
    combined_df['pb_ratio_score'] = int(combined_df['pb_ratio'].mean() < 2)
    combined_df['sum_debt_fcf_ratio_score'] = int(combined_df['debt_fcf_ratio'].sum() > 0)
    combined_df['earnings_yield_score'] = int(combined_df['earnings_yield'].gt(0).all())
    initial_value = combined_df['earnings_yield'].iloc[-1]
    last_value = combined_df['earnings_yield'].iloc[0]
    growth = (last_value - initial_value) / abs(initial_value)
    # Check if the growth is greater than or equal to 1.3x (130%)
    combined_df['1.3x_earnings_yield_score'] = (growth >= 1.3).astype(int)
    combined_df['dividend_yield_score'] = int(combined_df['dividend_yield'].gt(0).all())
    combined_df['total_score'] = combined_df['dividend_yield_score'] + \
        combined_df['earnings_yield_score'] + combined_df['1.3x_earnings_yield_score']\
              + combined_df['sum_debt_fcf_ratio_score'] + combined_df['pb_ratio_score']\
                  + combined_df['pe_ratio_score'] + combined_df['market_cap_score']

    # remove $nan for 0
    combined_df=combined_df.fillna(0.01)
    # Formats
    combined_df['WeightedAverageNumberOfSharesOutstandingBasic'] = combined_df['WeightedAverageNumberOfSharesOutstandingBasic'].apply(format_number)
    combined_df['book_value'] = combined_df['book_value'].apply(format_currency)
    combined_df['fcf'] = combined_df['fcf'].apply(format_currency)
    combined_df['EarningsPerShareBasic'] = combined_df['EarningsPerShareBasic'].apply(format_currency)
    combined_df['EarningsPerShareDiluted'] = combined_df['EarningsPerShareDiluted'].apply(format_currency)
    combined_df['total_debt'] = combined_df['total_debt'].apply(format_currency)
    combined_df['PaymentsOfDividendsCommonStock'] = combined_df['PaymentsOfDividendsCommonStock'].apply(format_currency)
    combined_df['price_per_share'] = combined_df['price_per_share'].apply(format_currency)
    combined_df['pb_ratio'] = combined_df['pb_ratio'].apply(format_ratio)
    combined_df['pe_ratio'] = combined_df['pe_ratio'].apply(format_ratio)
    combined_df['debt_fcf_ratio'] = combined_df['debt_fcf_ratio'].apply(format_ratio)
    combined_df['dividend_yield'] = combined_df['dividend_yield'].apply(format_percentage)
    combined_df['earnings_yield'] = combined_df['earnings_yield'].apply(format_percentage)
    combined_df['market_cap'] = combined_df['market_cap'].apply(format_currency)
    
    return combined_df
# Example function call
if __name__ == "__main__":
 
    tickers = ['abt','air']
    object=[]
    
    for ticker in tickers:
        response=fetch_5y_data(ticker)
        print(response)
            
