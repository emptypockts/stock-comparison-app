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
    path = r"C:\\Users\\ejujo\\Downloads\\companyfacts\\"
    files = os.listdir(path)
    qtr_obj = []
    nasdaq =pd.read_csv(r"C:\\Users\ejujo\\coding\\nasdaq.csv")
    metric_keys = {
    'RevenueFromContractWithCustomerExcludingAssessedTax': 'revenue',#revenue
    'RevenueFromContractWithCustomerIncludingAssessedTax':'revenue', #revenue
    'Revenues': 'revenue', #revenue
    'Assets': 'assets',#assets
    'CashAndCashEquivalentsAtCarryingValue':'end_cash_postion', #cash
    'Liabilities':'liabilities', #total liabilities
    'NetIncomeLoss':'netIncome', #net_income #return on assets = net_income / assets
    'ResearchAndDevelopmentExpense':'R&D', #rd
    'NetCashProvidedByUsedInOperatingActivities':'operatingCashFlow', #fcf =NetCashProvidedByUsedInOperatingActivities- PaymentsToAcquirePropertyPlantAndEquipment
    'PaymentsOfDividends':'dividends', #dividends
    'EntityCommonStockSharesOutstanding':'OutstandingShares', #outstandingshares
    'EarningsPerShareBasic':'EPS',
    'EarningsPerShareDiluted':'EPS_diluted',
    'CommercialPaper':'CommercialPaper',
    'OtherLiabilitiesCurrent':'OtherLiabilitiesCurrent', #total debt = OtherLiabilitiesCurrent+ OtherLiabilitiesNonCurrent +LiabilitiesCurrent +LiabilitiesNoncurrent
    'OtherLiabilitiesNoncurrent':'OtherLiabilitiesNoncurrent', #total debt = OtherLiabilitiesCurrent+ OtherLiabilitiesNonCurrent +LiabilitiesCurrent +LiabilitiesNoncurrent
    'LiabilitiesCurrent':'LiabilitiesCurrent', #total debt = OtherLiabilitiesCurrent+ OtherLiabilitiesNonCurrent +LiabilitiesCurrent +LiabilitiesNoncurrent
    'LiabilitiesNoncurrent':'LiabilitiesNoncurrent', #total debt = OtherLiabilitiesCurrent+ OtherLiabilitiesNonCurrent +LiabilitiesCurrent +LiabilitiesNoncurrent
    'PaymentsToAcquirePropertyPlantAndEquipment':'capex',
    'NetCashProvidedByUsedInInvestingActivities':'capex2'
    }
    for file in files:
        # use to debug
    # for file in files[:3:]: 
        cik_integer = int(file[:-5].lstrip("CIK").lstrip("0"))
        ticker=fetch_ticker(db,cik_integer)
        if ticker and ticker in nasdaq['ticker'].values:
            with open(path + file) as f:
                item = json.loads(f.read())

        # Iterate through items in the dataset
                if item and 'entityName' in item and 'facts' in item and 'us-gaap' in item['facts'] and 'cik' in item:
                    for metric_name, key_value in metric_keys.items():
                        # Check if the metric exists in the current item
                        if metric_name in item['facts']['us-gaap']:
                            if 'USD' in item['facts']['us-gaap'][metric_name]['units'] or 'USD/shares' in item['facts']['us-gaap'][metric_name]['units']:
                                if metric_name=='EarningsPerShareBasic' or metric_name=='EarningsPerShareDiluted':
                                    metrics = item['facts']['us-gaap'][metric_name]['units']['USD/shares']
                                else:
                                    metrics = item['facts']['us-gaap'][metric_name]['units']['USD']
                                for metric in metrics:
                                    # Process only 10-Q forms with a frame
                                    endDate=datetime.strptime(metric['end'],'%Y-%m-%d')
                                    if metric['form'] == '10-Q' and (endDate.year>2023)  :
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


def fetch_dei_info():
    path = f"C:\\Users\\ejujo\\Downloads\\companyfacts\\"
    files = os.listdir(path)
    qtr_obj = []

    


    # for file in files[:3:]:
    for file in files:
        cik_integer = int(file[:-5].lstrip("CIK").lstrip("0"))
        ticker=fetch_ticker(db,cik_integer)
        if ticker:
            with open(path + file) as f:
                item = json.loads(f.read())



        # Iterate through items in the dataset
            if item and 'entityName' in item and 'facts' in item and 'dei' in item['facts'] and 'cik' in item:
                outstanding_shares_map = {}
                if 'dei' in item['facts']:
                    if 'EntityCommonStockSharesOutstanding' in item['facts']['dei']:
                        outstanding_data = item['facts']['dei']['EntityCommonStockSharesOutstanding']
                        if 'shares' in outstanding_data['units']:
                            for share in outstanding_data['units']['shares']:
                                endDate=datetime.strptime(share['end'],'%Y-%m-%d')
                                if share['form']=='10-Q' and (endDate.year>2022):
                                    print(ticker)
                                    qtr_obj.append({
                                    'ticker':ticker,
                                    'metric':'outstandingShares',
                                    'value':share['val'],
                                    'date':share['end'],
                                    'form':share['form'],
                                    'fp':share.get('fp',None),
                                    'frame':share.get('frame',None),
                                    })


                                    
    return qtr_obj


def push_QStockData(db, objects, collection):
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
    y=df['maxRev'].apply(lambda x:x['output'])
    if len(x) < 3 or len(set(y)) == 1: 
        return pd.Series([0.0] * len(df), index=df.index)
        
    else:
        refQ= y.iloc[0].item()
        lastQ = y[-1:].item()
        percentIncrease=0
        if refQ>0:
            percentIncrease = ((lastQ-refQ)/refQ)*100

        return pd.Series([percentIncrease] * len(df), index=df.index) 
    
        

def pullAllStockData(db,skip,limit_size=10000,collection='QtrStockData'):
    QStockData_Collection = db[collection]
    QStockData = QStockData_Collection.aggregate([
 {
        '$match': {
            # 'ticker':{'$in':['CVS','MSFT']},
            'metric': {
                '$in': [
                    'Revenues', 
                    'RevenueFromContractWithCustomerExcludingAssessedTax',
                    'RevenueFromContractWithCustomerIncludingAssessedTax'
                ]
            },
            'frame':{'$ne':None},
        }
    }, {
        '$group': {
            '_id': {
                'ticker': '$ticker', 
                'date': '$date', 
                'form': '$form', 
                'fp': '$fp', 
                'frame': '$frame'
            }, 
            'maxRev': {
                '$max': {
                    'output': '$value'
                }
            }
        }
    }, {
        '$skip':skip*limit_size
        },{
        
        '$limit':limit_size
        },
    {
        '$project': {
            '_id': 0, 
            'ticker': '$_id.ticker', 
            'date': '$_id.date', 
            'maxRev': 1
        }
    }
])
    
    return QStockData


def pushMergedRevenueGrowthQtrStockData(db, MergedJsonResponseRevenueGrowthQtrStockData, collection):
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

def PullProcessMergeRevenueGrowthQtrStockData(db,skip,limit_size):

    ResponsePullAllStockData = pullAllStockData(db,skip,limit_size)
    DfResponseRevenueGrowthQtrStockData= pd.DataFrame(ResponsePullAllStockData)
    if DfResponseRevenueGrowthQtrStockData.empty:
        print('object is empty')
        return None
    DfResponseRevenueGrowthQtrStockData['filed']=pd.to_datetime(DfResponseRevenueGrowthQtrStockData['date'])    
    DfResponseRevenueGrowthQtrStockData= DfResponseRevenueGrowthQtrStockData.sort_values(by=['ticker','date']).groupby('ticker').tail(4).reset_index(level=0,drop=True)
    DfResponseRevenueGrowthQtrStockData['trend']=round(DfResponseRevenueGrowthQtrStockData.groupby(["ticker"],sort=False).apply(lambda group: RevenueGrowthQtrStockData(group)).reset_index(level=0, drop=True),1)
    DfResponseRevenueGrowthQtrStockData['value']=round((DfResponseRevenueGrowthQtrStockData['maxRev'].apply(lambda x:x['output']/1e6)),2)
    MergedDfResponseRevenueGrowthQtrStockData=DfResponseRevenueGrowthQtrStockData.groupby('ticker').filter(lambda group:group['value'].sum()!=0)
    MergedDfResponseRevenueGrowthQtrStockData = MergedDfResponseRevenueGrowthQtrStockData.groupby('ticker').agg({ 'value': lambda x: ','.join(map(str, x)), 'trend': 'first' }).reset_index()
    MergedJsonResponseRevenueGrowthQtrStockData=MergedDfResponseRevenueGrowthQtrStockData.to_dict(orient='records')

    return MergedJsonResponseRevenueGrowthQtrStockData

def PullQtrStockRevenueTrends(db, page=1,items_per_page=100,collection='QtrStockRevTrend'):
    print("Page",page)
    print("Page size ",items_per_page)
    QtrStockRevTrendCollection = db[collection]
# 
    # Fetch records with pagination
    stocks = QtrStockRevTrendCollection.aggregate([
        {
        '$lookup': {
            'from': 'StockScore', 
            'localField': 'ticker', 
            'foreignField': 'Symbol', 
            'let': {
                'tickerSymbol': '$ticker'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$eq': [
                                '$Symbol', '$$tickerSymbol'
                            ]
                        }
                    },
                    
                },
                {'$limit':1},
                  {
                    '$project': {
                        '_id': 0, 
                        'totalScore': '$Total Score'
                    }
                }
            ], 
            'as': 'result'
        }
    }, {
        '$addFields': {
            'scoreList': {
                '$map': {
                    'input': '$result', 
                    'as': 'element', 
                    'in': {
                        '$toString': '$$element.totalScore'
                    }
                }
            }
        }
    }, {
        '$addFields': {
            'valueScore': {
                '$reduce': {
                    'input': '$scoreList', 
                    'initialValue': '', 
                    'in': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$$value', ''
                                ]
                            }, '$$this', {
                                '$concat': [
                                    '$$value', ',', '$$this'
                                ]
                            }
                        ]
                    }
                }
            }
        }
    }, {
        '$project': {
            'ticker': 1, 
            'value': 1, 
            'valueScore': 1, 
            'trend': 1
        }
    },
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

def CountAggRecordPipeline(db, collection='QtrStockData'):
    QStockData_Collection = db[collection]
    QstockData=QStockData_Collection.aggregate([
 {
        '$match': {
            'metric': {
                '$in': [
                    'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax'
                ]
            },
            'frame':{
                '$ne':None
                }
        }
    }, {
        '$group': {
            '_id': {
                'ticker': '$ticker', 
                'date': '$date', 
                'form': '$form', 
                'fp': '$fp', 
                'frame': '$frame'
            }, 
            'maxRev': {
                '$max': {
                    'output': '$value'
                }
            }
        }
    },{
        '$count': 'totalRecords'
}
])
    resultObj = list(QstockData)
    return resultObj[0]['totalRecords'] if resultObj else 0

if __name__=="__main__":
    uri = os.getenv('MONGODB_URI')
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["test"]
    tickers = ['CVS','ROST']
    collectionSize=CountAggRecordPipeline(db)
    limit_size=10000
    skip=0
    # # Flow to update stock info from json files  (GAAP)
    # object = fetch_Stock_Info()
    # push_QStockData(db,object,collection='QtrStockData')
    
    # Flow to update stock info from json files (IFRS)
    # # Flow to update stock info from json files (DEI)
    # object=fetch_dei_info()
    # push_QStockData(db,object,collection='QtrDeiStockData')
    
    # print(object)
    
    # print("Main function to update revenue trends in DB")
   
    # for skip in range((collectionSize//limit_size)+1):
    #     # print(skip,collectionSize)
    #     response =PullProcessMergeRevenueGrowthQtrStockData(db,skip,limit_size)
    #     # print(response)
    #     pushMergedRevenueGrowthQtrStockData(db,response,collection='QtrStockRevTrend')
    
    # test PullQtrStockRevenueTrends
    # grouped_stocks,total_symbols = PullQtrStockRevenueTrends(db,1,100)
    # print(grouped_stocks)
    # print(total_symbols)