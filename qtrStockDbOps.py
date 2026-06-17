from dotenv import load_dotenv
import os
from pymongo import MongoClient, errors,UpdateOne
from pymongo.collection import Collection
import json
import pandas as pd
from financialUtils import get_metric_keys,fetch_ticker,push_StockData,swap_temp_prod,prepare_collection_backup
import numpy as np
from datetime import datetime
load_dotenv
# join qtr rev trend table with stock score 
def aggregateScoreToQtrRevTrend(collection:Collection,batch_size=1000):
    
    stocks = collection.aggregate([
    {
        '$lookup':{
            'from':'StockScore',
            'localField':'ticker',
            'foreignField':'ticker',
            'let':{'ticker':'$ticker'},
            'pipeline':[
                {
                    '$match':{
                        '$expr':{'$eq':['$ticker','$$ticker']}
                    }
                },
                {
                    '$project':{
                        '_id':0,
                        'score':'$score',
                        'sector': '$sector'
                    }
                }
            ],
            'as':'result'
        }
    }

    ])
    
    jsonObject=[]
    for item in stocks:
        jsonObject.append(
            UpdateOne(
            {"ticker":item["ticker"]},
            {
                "$set":{
                    "score":(',').join(str(score["score"]) for score in item["result"]),
                    "sector":item["result"][0]["sector"] if item["result"] else None
                }
            },
            upsert=False
        )
        )
    jsonObject_len = len(jsonObject)
    if jsonObject:
        for idx in range(0,jsonObject_len,batch_size):
            print(f"pushing batch: {idx//batch_size} of: {jsonObject_len//batch_size}.")
            collection.bulk_write(jsonObject[idx:idx+batch_size])
        print('push completed successfully')
def fetch_Stock_Info():
    current_date = datetime.today()
    collection=db['tickerCIK']
    env = os.getenv('ENV')
    if os.getenv('ENV')=='dev':
        path=r'/Users/jjmr86/Downloads/companyfacts/'
        nasdaq =pd.read_csv(r"/Users/jjmr86/Downloads/nasdaq.csv")
    else:
        path = r"/home/jjmr86/quarterly_stock_ops/companyfacts/"
        nasdaq =pd.read_csv(r"/home/jjmr86/quarterly_stock_ops/nasdaq.csv")
    
    files = os.listdir(path)
    metric_keys =get_metric_keys()
    nasdaq_tickers = set(nasdaq["ticker"].astype(str))
    for file in files:
        # use to debug
    # for file in files[-5::]:
        cik_integer = [int(file[:-5].lstrip("CIK").lstrip("0"))]
        tickers=fetch_ticker(cik_integer,collection)
        valid_tickers = [t for t in tickers if t in nasdaq_tickers]
        if valid_tickers:
            for ticker in valid_tickers:
                with open(path + file) as f:
                    item = json.load(f)
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
                                        end = metric.get('end')
                                        if not end:
                                            continue
                                        endDate=int(end[:4])
                                        if metric['form'] == '10-Q' and (endDate>2023)  :
                                            yield{                                           
                                                'ticker':ticker,
                                                'entity':item['entityName'],
                                                'metric':metric_name,
                                                'value':metric['val'],
                                                'date':metric['end'],
                                                'form':metric['form'],
                                                'fp':metric.get('fp',None),
                                                'frame':metric.get('frame',None),
                                                'date_start':metric.get('start',None),
                                                'accn':metric['accn'],
                                                'fy':metric['fy'],
                                                'filed':metric['filed']
                                                    }
                                        if metric['form']=='10-K' and (endDate>2023) and metric_name =='Revenues':
                                            yield{
                                                'ticker':ticker,
                                                'entity':item['entityName'],
                                                'metric':metric_name,
                                                'value':metric['val'],
                                                'date':metric['end'],
                                                'form':metric['form'],
                                                'fp':metric.get('fp',None),
                                                'frame':metric.get('frame',None),
                                                'date_start':metric.get('start',None),
                                                'accn':metric['accn'],
                                                'fy':metric['fy'],
                                                'filed':metric['filed']
                                            }
def fetch_dei_info():
    path = f"/home/jjmr86/quarterly_stock_ops/companyfacts/"
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
def pullAllStockData(collection:Collection,skip,limit_size=10000,):
    
    QStockData = collection.aggregate([
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
def pushMergedRevenueGrowthQtrStockData(MergedJsonResponseRevenueGrowthQtrStockData, collection:Collection):
    try:
        
        result = collection.insert_many(MergedJsonResponseRevenueGrowthQtrStockData)
        print(f"jsonData inserted successfully, inserted_ids (first 10): {result.inserted_ids[0:10]}")
    except errors.BulkWriteError as bwe:
        print(f"Bulk write error: {bwe.details}")
    except errors.ConnectionFailure as cf:
        print(f"Connection failure: {cf}")
    except errors.OperationFailure as ofe:
        print(f"Operation failure: {ofe}")
    except Exception as e:
        print(f"An error occurred: {e}")
def PullProcessMergeRevenueGrowthQtrStockData(collection,skip,limit_size):

    ResponsePullAllStockData = pullAllStockData(collection,skip,limit_size,)
    DfResponseRevenueGrowthQtrStockData= pd.DataFrame(ResponsePullAllStockData)
    if DfResponseRevenueGrowthQtrStockData.empty:
        print('object is empty')
        return None
    DfResponseRevenueGrowthQtrStockData['filed']=pd.to_datetime(DfResponseRevenueGrowthQtrStockData['date'])    
    DfResponseRevenueGrowthQtrStockData= DfResponseRevenueGrowthQtrStockData.sort_values(by=['ticker','date']).groupby('ticker').tail(4).reset_index(level=0,drop=True)
    DfResponseRevenueGrowthQtrStockData['trend']=(
        DfResponseRevenueGrowthQtrStockData
        .groupby(["ticker"],sort=False)
        .apply(lambda group: RevenueGrowthQtrStockData(group),include_groups=False)
        .reset_index(level=0, drop=True)
        .round(1)
    )
    DfResponseRevenueGrowthQtrStockData['value']=round((DfResponseRevenueGrowthQtrStockData['maxRev'].apply(lambda x:x['output']/1e9)),2)
    MergedDfResponseRevenueGrowthQtrStockData = DfResponseRevenueGrowthQtrStockData.groupby('ticker').agg({ 'value': lambda x: ','.join(map(str, x)), 'trend': 'first' }).reset_index()
    MergedJsonResponseRevenueGrowthQtrStockData=MergedDfResponseRevenueGrowthQtrStockData.to_dict(orient='records')
    return MergedJsonResponseRevenueGrowthQtrStockData
def PullQtrStockRevenueTrends(collection:Collection,page=1,items_per_page=100):
    print("Page",page)
    print("Page size ",items_per_page)
    
    # Fetch records with pagination
    stocks = collection.aggregate([

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
    
    total_tickers = collection.distinct("ticker")
    total_tickers_count = len(total_tickers)

    return grouped_stocks,total_tickers_count
def CountAggRecordPipeline(collection:Collection):
    
    QstockData=collection.aggregate([
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
    # client = MongoClient(uri, server_api=ServerApi('1'),tls=True,tlsCaFile=certifi.where())
    client = MongoClient(uri)

    db = client["test"]
    # tickers = ['CVS','ROST']
    collectionSize=CountAggRecordPipeline(db['QtrStockData'])
    batch_size=5000
    skip=0
    #go to this link to download the company facts https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip
   
    # # Flow to update stock info from json files  (GAAP)
    if os.getenv('ENV')=='devs':
        from bson import json_util
        with open ('/Users/jjmr86/Downloads/test.QtrStockData.json','r') as f:
            stock_object = json_util.loads(f.read())
    else:
        stock_object = fetch_Stock_Info()


    prepare_collection_backup(db,collection_name='QtrStockData')
    push_StockData(db,stock_object,collection='QtrStockData',batch_size=batch_size)    


    # # function to update main revenue trends per quarter in the db   
    
    response =PullProcessMergeRevenueGrowthQtrStockData(db['QtrStockData'],skip,batch_size)
    
    prepare_collection_backup(db,collection_name='QtrStockRevTrend')
    pushMergedRevenueGrowthQtrStockData(response,db['QtrStockRevTrend'])    
    # join the qtr stock rev trend with the stock value score
    aggregateScoreToQtrRevTrend(db['QtrStockRevTrend'])

    # create index for each collection
    # create_index(db)
    
        
    
