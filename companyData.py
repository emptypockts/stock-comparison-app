import logging
import dotenv
import os
import requests
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from pymongo import MongoClient
load_dotenv()
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
FPM_KY = os.getenv('FMP_API')
FPM_URL_BASE = os.getenv('FMP_URI')


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
def fetch_metric(collection,ticker=str,metric=str,fallback_metric=None)->int:

    query = {
            "ticker":ticker,
            "metric":{"$in":[metric,fallback_metric]}
        }    
    
    latest_doc = collection.find_one(query,sort=[("date",-1)])

    return latest_doc

def fetch_price_fmp(ticker):
    FPM_URL = f"{FPM_URL_BASE}?symbol={ticker.upper()}&apikey={FPM_KY}"
    response = requests.get(FPM_URL)
    try:
        price = response.json()[0]['price']
    except:
        price = 0
    return price

def compile_stockData(tickers):
    db = client['test']
    collection = db['QtrStockData']
    
    if not isinstance(tickers, list):
        logger.error("Input `tickers` must be a list.")
        return {}
    stock_info=[]
    for ticker in tickers:
        object = fetch_metric(collection,ticker.upper(),'StockholdersEquity','EntityCommonStockSharesOutstanding')
        stock_info.append(
        {
            'ticker':object.get('ticker',''),
            'name':object.get('entity','unknown'),
            'last_filing':object.get('date',''),
            'current_price': fetch_price_fmp(ticker)
        })
    
    

    
    return stock_info




# Example function call
if __name__ == "__main__":
    db = client['test']
    collection = db['QtrStockData']
    tickers= ['intc','rost']

    stock_info=compile_stockData(tickers)
    print(stock_info)
    # stock_data=[]
    # for ticker in tickers:
    #     try:
    #         response = fetch_metric(collection,ticker.upper(),'StockholdersEquity','EntityCommonStockSharesOutstanding')
    #         stock_data.append(response)
    #     except Exception as e:
    #         print(str(e))
    # print(stock_data)