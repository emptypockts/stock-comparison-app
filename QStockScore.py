from dotenv import load_dotenv
import os
from pymongo.server_api import ServerApi
from pymongo import MongoClient, errors
import json
import pandas as pd
from CIKTickerUpdate import fetch_cik
from math import atan, degrees
import numpy as np
def fetch_Stock_Info(ticker):
    qtr_revenue={}
    revenue_obj=[]
    cik = str(fetch_cik(db,ticker.upper()))
    cik="CIK"+("0"*(10 -len(cik)))+cik
    file = f"C:\\Users\\ejujo\\Downloads\\companyfacts\\{cik}.json"
    seen_frames = set()  # To track unique frames

    with open(file) as f:
        item = json.loads(f.read())
        f.close()
    if 'RevenueFromContractWithCustomerExcludingAssessedTax' in item['facts']['us-gaap']:
        revenues = item['facts']['us-gaap']['RevenueFromContractWithCustomerExcludingAssessedTax']['units']['USD']
        for revenue in revenues:
            if revenue['form'] == '10-Q' and revenue.get('frame') and revenue['frame'] not in seen_frames:
                qtr_revenue = {
                    'ticker': ticker,
                    'value': revenue['val'],
                    'fp': revenue['fp'],
                    'filed': revenue['filed'],
                    'frame': revenue['frame']
                }
                revenue_obj.append(qtr_revenue)
                seen_frames.add(revenue['frame'])  # Mark this frame as processed

    # Process Revenues
    if 'Revenues' in item['facts']['us-gaap']:
        revenues = item['facts']['us-gaap']['Revenues']['units']['USD']
        for revenue in revenues:
            if revenue['form'] == '10-Q' and revenue.get('frame') and revenue['frame'] not in seen_frames:
                qtr_revenue = {
                    'ticker': ticker,
                    'value': revenue['val'],
                    'fp': revenue['fp'],
                    'filed': revenue['filed'],
                    'frame': revenue['frame']
                }
                revenue_obj.append(qtr_revenue)
                seen_frames.add(revenue['frame'])  # Mark this frame as processed

    return revenue_obj


def push_QStockData(db, objects, collection='QtrStockData'):
    load_dotenv()
    try:
        stock_collection = db[collection]
        # Inject the objects into the database
        result = stock_collection.insert_many(objects)
        print(f"jsonData inserted successfully, inserted_ids: {result.inserted_ids}")
    except errors.BulkWriteError as bwe:
        print(f"Bulk write error: {bwe.details}")
    except errors.ConnectionFailure as cf:
        print(f"Connection failure: {cf}")
    except errors.OperationFailure as ofe:
        print(f"Operation failure: {ofe}")
    except Exception as e:
        print(f"An error occurred: {e}")


def pull_QStockData(db, ticker, collection='QtrStockData'):
    QStockData_Collection = db[collection]
    QStockData = QStockData_Collection.find({"ticker": ticker.lower()})

    return QStockData

def RevenueGrowthQtrStockData (df):
    if df.empty:
        print("Empty dataFrame")
        return pd.Series([0.0] * len(df), index=df.index)
    x = np.arange(len(df))
    y=df["value"].values/1e9
    if len(x) < 4 or len(set(y)) == 1:  
        return pd.Series([0.0] * len(df), index=df.index)
    slope = np.polyfit(x,y,1)[0]
    trend = degrees(atan(slope))
    
    return pd.Series([trend] * len(df), index=df.index) 


def pullAllStockData(db,collection='QtrStockData'):
    QStockData_Collection = db[collection]
    QStockData = QStockData_Collection.find()
    return QStockData


def pushMergedRevenueGrowthQtrStockData(db, MergedJsonResponseRevenueGrowthQtrStockData, collection='QtrStockRevTrend'):
    try:
        QtrStockRevTrend_Collection = db[collection]
        result = QtrStockRevTrend_Collection.insert_many(MergedJsonResponseRevenueGrowthQtrStockData)
        print(f"jsonData inserted successfully, inserted_ids: {result.inserted_ids}")
    except errors.BulkWriteError as bwe:
        print(f"Bulk write error: {bwe.details}")
    except errors.ConnectionFailure as cf:
        print(f"Connection failure: {cf}")
    except errors.OperationFailure as ofe:
        print(f"Operation failure: {ofe}")
    except Exception as e:
        print(f"An error occurred: {e}")

def PullProcessMergeRevenueGrowthQtrStockData(db):

    ResponsePullAllStockData = pullAllStockData(db)
    DfResponseRevenueGrowthQtrStockData= pd.DataFrame(ResponsePullAllStockData)
    DfResponseRevenueGrowthQtrStockData['filed']=pd.to_datetime(DfResponseRevenueGrowthQtrStockData['filed'])    
    DfResponseRevenueGrowthQtrStockData= DfResponseRevenueGrowthQtrStockData.sort_values(by=['ticker','frame']).groupby('ticker').tail(4).reset_index(level=0,drop=True)
    DfResponseRevenueGrowthQtrStockData['trend']=round(DfResponseRevenueGrowthQtrStockData.groupby(["ticker"],sort=False).apply(lambda group: RevenueGrowthQtrStockData(group)).reset_index(level=0, drop=True),1)
    DfResponseRevenueGrowthQtrStockData['value']=round((DfResponseRevenueGrowthQtrStockData['value']/1e9),2)
    MergedDfResponseRevenueGrowthQtrStockData = DfResponseRevenueGrowthQtrStockData.groupby('ticker').agg({ 'value': lambda x: ','.join(map(str, x)), 'trend': 'first' }).reset_index()
    MergedJsonResponseRevenueGrowthQtrStockData=MergedDfResponseRevenueGrowthQtrStockData.to_dict(orient='records')
    return MergedJsonResponseRevenueGrowthQtrStockData

def PullQtrStockRevenueTrends(db, page=1,items_per_page=100,collection='QtrStockRevTrend'):
    print("Page",page)
    print("Page size ",items_per_page)
    QtrStockRevTrendCollection = db[collection]

    # Fetch records with pagination
    stocks = QtrStockRevTrendCollection.aggregate([
    {
        '$skip': (page-1)*items_per_page
    }, {
        '$limit': 10000
    }
    ])
    # Group the fetched records by symbol
    grouped_stocks = {}
    for stock in stocks:
        stock['_id'] = str(stock['_id'])  # Convert ObjectId to string
                # Apply formatting to each relevant field
        ticker = stock['ticker']
        value = stock['value']
        trend = stock['trend']
        if ticker not in grouped_stocks:
            grouped_stocks[ticker] = []
        grouped_stocks[ticker].append(stock)
    
    total_tickers = QtrStockRevTrendCollection.distinct("ticker")
    total_tickers_count = len(total_tickers)

    return grouped_stocks,total_tickers_count

if __name__=="__main__":
    uri = os.getenv('MONGODB_URI')
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["test"]
    # tickers = ['CVS']
    # for ticker in tickers:
    #     object=fetch_Stock_Info(ticker)
    #     push_QStockData(db,object)

    
    print("Main function to update revenue trends in DB")
    response =PullProcessMergeRevenueGrowthQtrStockData(db)
    pushMergedRevenueGrowthQtrStockData(db,response)
    

   







