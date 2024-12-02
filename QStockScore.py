from dotenv import load_dotenv
import os
from pymongo.server_api import ServerApi
from pymongo import MongoClient, errors
import json
import pandas as pd
from CIKTickerUpdate import fetch_cik,fetch_ticker
from math import atan, degrees
import numpy as np
from datetime import datetime

def fetch_Stock_Info():
    path = f"C:\\Users\\ejujo\\Downloads\\companyfacts\\"
    files = os.listdir(path)
    qtr_obj = []


<<<<<<< HEAD
=======
    
>>>>>>> 443ab7512e6da3ce0db3f3f2801aaebbc554c82e
    # Define the metrics to process and their corresponding keys
    metric_keys = {
        'RevenueFromContractWithCustomerExcludingAssessedTax': 'revenue',
        'Revenues': 'revenue',
        'Assets': 'assets',
        'CashAndCashEquivalentsAtCarryingValue':'cash',
        'Liabilities':'liabilities',
        'NetIncomeLoss':'netIncome',
        'ResearchAndDevelopmentExpense':'R&D',
        'NetCashProvidedByUsedInOperatingActivities':'operatingCashFlow',
        'PaymentsOfDividends':'dividends'

    }

    for file in files:
        cik_integer = int(file[:-5].lstrip("CIK").lstrip("0"))
        ticker=fetch_ticker(db,cik_integer)
        if ticker:
            with open(path + file) as f:
                item = json.loads(f.read())



        # Iterate through items in the dataset
            if item and 'entityName' in item and 'facts' in item and 'us-gaap' in item['facts'] and 'cik' in item:
                for metric_name, key_name in metric_keys.items():
                    # Check if the metric exists in the current item
                    if metric_name in item['facts']['us-gaap']:
                        if 'USD' in item['facts']['us-gaap'][metric_name]['units']:
                            metrics = item['facts']['us-gaap'][metric_name]['units']['USD']
                            for metric in metrics:
                                # Process only 10-Q forms with a frame
                                endDate=datetime.strptime(metric['end'],'%Y-%m-%d')
                                if metric['form'] == '10-Q' and (endDate.year>2022)  :
                                    qtr_obj.append({
                                            'ticker':ticker,
                                            'metric':metric_name,
                                            'value':metric['val'],
                                            'date':metric['end'],
                                            'form':metric['form'],
                                            'fp':metric.get('fp',None),
                                            'frame':metric.get('frame',None)
                                            })
                                    
                                    
    # Convert the deduplicated frames into a list
    return qtr_obj


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
    DfResponseRevenueGrowthQtrStockData['filed']=pd.to_datetime(DfResponseRevenueGrowthQtrStockData['date'])    
    DfResponseRevenueGrowthQtrStockData= DfResponseRevenueGrowthQtrStockData.sort_values(by=['ticker','date']).groupby('ticker').tail(4).reset_index(level=0,drop=True)
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
        '$sort' :{'trend':-1}
        },{
        '$skip': (page-1)*items_per_page
        },{
        '$limit': items_per_page
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
    
    # Flow to update stock info from json files
    object=fetch_Stock_Info()
    push_QStockData(db,object)

    
    # print("Main function to update revenue trends in DB")
    # response =PullProcessMergeRevenueGrowthQtrStockData(db)
    # pushMergedRevenueGrowthQtrStockData(db,response)
    