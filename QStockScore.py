from dotenv import load_dotenv
import os
from pymongo.server_api import ServerApi
from pymongo import MongoClient, errors
import json
import pandas as pd
from CIKTickerUpdate import fetch_cik,fetch_ticker
from math import atan, degrees
import numpy as np
def fetch_Stock_Info():
    qtr_revenue={}
    revenue_obj=[]
    path = f"C:\\Users\\ejujo\\Downloads\\companyfacts\\"
    files = os.listdir(path)
    seen_frames = {}  # Dictionary to track the highest value for each frame per ticker
    revenue_obj = []  # Final list of deduplicated revenue objects

    for file in files:
        cik_integer = int(file[:-5].lstrip("CIK").lstrip("0"))
        ticker=fetch_ticker(cik_integer)
        with open(path + file) as f:
            item = json.loads(f.read())

        if item and 'entityName' in item and 'facts' in item and 'us-gaap' in item['facts'] and 'cik' in item:
            # Process RevenueFromContractWithCustomerExcludingAssessedTax
            if 'RevenueFromContractWithCustomerExcludingAssessedTax' in item['facts']['us-gaap']:
                if 'USD' in item['facts']['us-gaap']['RevenueFromContractWithCustomerExcludingAssessedTax']['units']:
                    revenues = item['facts']['us-gaap']['RevenueFromContractWithCustomerExcludingAssessedTax']['units']['USD']
                    for revenue in revenues:
                        if revenue['form'] == '10-Q' and revenue.get('frame'):
                            frame_key = (revenue['frame'], file[:-5])  # Frame and ticker as key
                            if frame_key not in seen_frames or revenue['val'] > seen_frames[frame_key]['value']:
                                # Update the record if it's a new frame or has a higher value
                                seen_frames[frame_key] = {
                                    'cik': item['cik'],
                                    'value': revenue['val'],
                                    'fp': revenue['fp'],
                                    'filed': revenue['filed'],
                                    'frame': revenue['frame'],
                                    'ticker': ticker
                                }

            # Process Revenues
            if 'Revenues' in item['facts']['us-gaap']:
                if 'USD' in item['facts']['us-gaap']['Revenues']['units']:
                    revenues = item['facts']['us-gaap']['Revenues']['units']['USD']
                    for revenue in revenues:
                        if revenue['form'] == '10-Q' and revenue.get('frame'):
                            frame_key = (revenue['frame'], file[:-5])  # Frame and ticker as key
                            if frame_key not in seen_frames or revenue['val'] > seen_frames[frame_key]['value']:
                                # Update the record if it's a new frame or has a higher value
                                seen_frames[frame_key] = {
                                    'cik': item['cik'],
                                    'value': revenue['val'],
                                    'fp': revenue['fp'],
                                    'filed': revenue['filed'],
                                    'frame': revenue['frame'],
                                    'ticker': ticker
                                }

    # Convert the deduplicated frames into a list
    revenue_obj = list(seen_frames.values())
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
    tickers = ['CVS','ROST']
    object=[]
    # Flow to update stock info from json files
    # object.extend(fetch_Stock_Info())
    # push_QStockData(db,object)

    
    # print("Main function to update revenue trends in DB")
    response =PullProcessMergeRevenueGrowthQtrStockData(db)
    pushMergedRevenueGrowthQtrStockData(db,response)
    