import logging
import os
import requests
from pandas import Series
from datetime import datetime,timedelta
from dotenv import load_dotenv
from typing import Literal
from pymongo.server_api import ServerApi
from pymongo import MongoClient,DESCENDING
from pymongo.collection import Collection,Cursor
from financialUtils import Transform_Obj_and_Date,fetch_price_fmp,fetch_metric
load_dotenv()
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
KY = os.getenv('TWELVE_API_KY')
URL_BASE = os.getenv('TWELVE_URI')


def compile_stockData(tickers):
    db = client['test']
    collection = db['QtrStockData']
    
    if not isinstance(tickers, list):
        return {}
    stock_info={}
    mode='last'
    for ticker in tickers:
        object = fetch_metric(collection,ticker.upper(),metric=['StockholdersEquity','EntityCommonStockSharesOutstanding','StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'],mode=mode)
        if object:
            
            stock_info[ticker]={
                'ticker':object.get('ticker',''),
                'name':object.get('entity','unknown'),
                'last_filing':object.get('date',''),
                'current_price': fetch_price_fmp(ticker,mode='last')
            }
    return stock_info

# Example function call
if __name__ == "__main__":
    db = client['test']
    collection = db['QtrStockData']
    tickers= ['air','abt']

    stock_info=compile_stockData(tickers)
    print(stock_info)