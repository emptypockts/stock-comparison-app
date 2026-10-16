from pymongo import MongoClient,DESCENDING
import certifi
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime,timedelta
from eacsa_logger import setup_logging, get_logger
import yfinance as yf
from typing import Any
setup_logging()
logger = get_logger(__name__)
load_dotenv()
uri = os.getenv('MONGODB_URI')
# client = MongoClient(uri, server_api=ServerApi('1'),tls=True,tlsCaFile=certifi.where())
client = MongoClient(uri)

API = os.getenv('ALPHA_VANTAGE_API_KEY')
db = client["test"]


def fetch_historic_stock_price(ticker: str) -> dict[str, Any]:
    """
    Receives a ticker, fetches the monthly adjusted closing prices
    for the last 5 years and returns a date-keyed dict of closing prices.
    Uses yfinance as a free, no-key-required data source.
    """
    start_date = datetime.today().date() - timedelta(weeks=260)
    end_date = datetime.today().date()
    try:
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval="1mo",
            auto_adjust=True,
            progress=False,
        )
        if data.empty:
            logger.warning(f"No historical price data returned for {ticker}.")
            return {}
        qtr_obj = {
            str(date.date()): str(round(float(close), 4))
            for date, close in zip(data.index, data["Close"].squeeze())
        }
        return qtr_obj
    except Exception as e:
        logger.error(f"Error fetching historic stock price for {ticker}: {e}")
        return {}

def db_4qtr_data_fetch(db,ticker,collection='QtrStockData'):
    collection_QtrStockData=db[collection]

    Object = collection_QtrStockData.aggregate(
        [
    {
        '$match': {
            'ticker': ticker.upper(), 
            'frame': {
                '$ne': None, 
            },
            'fp':{
                '$regex':'^Q'
            }
        }
    }, {
        '$sort': {
            'date': 1
        }
    }
    ]
    )
    return Object

def db_4qtr_dei_data_fetch(db,ticker,collection='QtrDeiStockData'):
    collection_QtrStockData=db[collection]

    Object = collection_QtrStockData.aggregate(
        [
    {
        '$match': {
            'ticker': ticker.upper(), 
            'frame': {
                '$ne': None, 
            }
        }
    }, {
        '$sort': {
            'date': 1
        }
    }
    ]
    )
    return Object


def fetch_4qtr_data(ticker)->dict:
    gaapObj = db_4qtr_data_fetch(db,ticker)
    deiObj=db_4qtr_dei_data_fetch(db,ticker)
    net_income=[]
    OtherLiabilitiesCurrent=[]
    OtherLiabilitiesNoncurrent=[]
    LiabilitiesCurrent=[]
    LiabilitiesNoncurrent=[]
    metrics=[]
    for obj in gaapObj:
        obj['_id']=str(obj['_id'])
        metrics.append(obj)
    metricObj={}
    for metric in metrics:
        metricName = metric['metric']
        date_value = {metric['date']:metric['value']}
        if metricName not in metricObj:
            metricObj[metricName]={}
        metricObj[metricName].update(date_value)
    deiMetrics=[]
    for obj in deiObj:
        obj['_id']=str(obj['_id'])
        deiMetrics.append(obj)

    for deiMetric in deiMetrics:
        metricName = deiMetric['metric']
        date_value = {deiMetric['date']:deiMetric['value']}
        if metricName not in metricObj:
            metricObj[metricName]={}
        metricObj[metricName].update(date_value)


    net_income = metricObj.get('NetIncomeLoss',{})
    Assets = metricObj.get('Assets',{})
    return_on_assets={'return_on_assets':{}}

    return_on_assets['return_on_assets'].update({
        key:f"{round((item/Assets.get(key,0))*100,1)}%" for key,item in net_income.items() if (assets:=Assets.get(key))
    })

    total_revenue = {
        'total_revenue':
        metricObj.get('Revenues',metricObj.get('RevenueFromContractWithCustomerExcludingAssessedTax',0))
    }
    
#fcf =NetCashProvidedByUsedInOperatingActivities- PaymentsToAcquirePropertyPlantAndEquipment
    NetCashProvidedByUsedInOperatingActivities = metricObj.get('NetCashProvidedByUsedInOperatingActivities',{})
    PaymentsToAcquirePropertyPlantAndEquipment = metricObj.get('PaymentsToAcquirePropertyPlantAndEquipment',{})
    fcf={'fcf':{}}

    fcf['fcf'].update({
        key:(item-PaymentsToAcquirePropertyPlantAndEquipment.get(key,0)) for key,item in NetCashProvidedByUsedInOperatingActivities.items()
    })

    OtherLiabilitiesNoncurrent = metricObj.get('OtherLiabilitiesNoncurrent',{})
    OtherLiabilitiesCurrent = metricObj.get('OtherLiabilitiesCurrent',{})
    LiabilitiesCurrent = metricObj.get('LiabilitiesCurrent',{})
    LiabilitiesNoncurrent = metricObj.get('LiabilitiesNoncurrent',{})
    total_debt={'total_debt':{}}
    total_debt['total_debt'].update({
        key:
        (
            item+OtherLiabilitiesNoncurrent.get(key,0)+OtherLiabilitiesCurrent.get(key,0)+LiabilitiesNoncurrent.get(key,0)) 
            for key,item in LiabilitiesCurrent.items()
    })
    metricObj.update(return_on_assets)
    metricObj.update(total_revenue)
    metricObj.update(fcf)
    metricObj.update(total_debt)
    


    return metricObj

# Example function call
if __name__ == "__main__":
    
    tickers = ['KO']  # Replace with your desired ticker
    all_data = []
    

    # all_data = [fetch_5y_data(ticker)for ticker in tickers]
    all_data={
        ticker:{
        'financial_data':fetch_4qtr_data(ticker)    
        }for ticker in tickers
    }
    print(all_data)
        
    
    
    



    

    