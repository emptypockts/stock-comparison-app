from financialUtils import fetch_price_fmp,fetch_metric
import pandas as pd
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
def fetch_stock_price_data(ticker,collection=None):
    db=client['test']
    collection=db['rawEdgarCollection']
    data = fetch_price_fmp(collection=collection,ticker=ticker,mode='5y')
    return data

if __name__ == "__main__":
    

    price = []
    
    tickers = ['axp','intc']  # Example ticker
    for ticker in tickers:
        stock=fetch_stock_price_data(ticker)
        price.append({ticker:{str(e['date']):e['value'] for e in stock if e}})
    print(price)
    
