import logging
import os
import requests
from dotenv import load_dotenv
from typing import Literal
from pymongo.server_api import ServerApi
from pymongo import MongoClient,DESCENDING
load_dotenv()
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
KY = os.getenv('TWELVE_API_KY')
URL_BASE = os.getenv('TWELVE_URI')

def fetch_metric(
        collection,
        ticker=str,
        metric=list,
        mode:Literal["last","all","year","first"]="all",
        frame:str= None,
        unique_metric:bool=True
        )->object:

    query = {
            "ticker":ticker.upper(),
            "metric":{"$in":metric}
        }    
    if mode =='last' and unique_metric:
        last_doc = collection.find_one(query,sort=[("date",-1)])
        return last_doc if last_doc else {}
    elif mode=='last' and not unique_metric:
        last_doc = collection.find(query).sort("date",DESCENDING)
        return last_doc if last_doc else {}
    if mode =='first' and unique_metric:
        first_doc = collection.find_one(query,sort=[("date",1)])
        return first_doc if first_doc else {}
    elif mode=='first'and not unique_metric:
        first_doc = collection.find(query).sort("date",DESCENDING)
        return first_doc if first_doc else {}
    elif mode=='all':
        return collection.find(query).sort("date",DESCENDING)
    elif mode=='year'and unique_metric:

        if not frame:
            raise ValueError('year most be provided in the format CY and yyyy for example CY2024')
        query['frame']={'$regex':f'^{frame}'}
        year_doc=collection.find_one(query,sort=[("date",-1)])
        return year_doc if year_doc else {}
    elif mode=='year' and not unique_metric:
        if not frame:
            raise ValueError('year most be provided in the format CY and yyyy for example CY2024')
        query['frame']={'$regex':f'^{frame}'}
        year_doc=collection.find(query).sort("date",DESCENDING)
        return year_doc if year_doc else {}
    
    return []

def fetch_price_fmp(ticker):
    URL = f"{URL_BASE}?symbol={ticker.upper()}&apikey={KY}&source=docs"
    
    response = requests.get(URL)
    try:
        price = float(response.json()['price'])
    except Exception as e:
        print(str(e))
        price = 0
    return price

def compile_stockData(tickers):
    db = client['test']
    collection = db['QtrStockData']
    
    if not isinstance(tickers, list):
        return {}
    stock_info={}
    mode='last'
    for ticker in tickers:
        object = fetch_metric(collection,ticker.upper(),metric=['StockholdersEquity','EntityCommonStockSharesOutstanding'],mode=mode)
        if object:
            
            stock_info[ticker]={
                'ticker':object.get('ticker',''),
                'name':object.get('entity','unknown'),
                'last_filing':object.get('date',''),
                'current_price': fetch_price_fmp(ticker)
            }
    return stock_info

# Example function call
if __name__ == "__main__":
    db = client['test']
    collection = db['QtrStockData']
    tickers= ['intc','rost']

    stock_info=compile_stockData(tickers)
    print(stock_info)