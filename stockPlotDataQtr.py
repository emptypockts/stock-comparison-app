from pymongo import MongoClient,DESCENDING
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime,timedelta
import requests
load_dotenv()
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
API = os.getenv('ALPHA_VANTAGE_API_KEY')
db = client["test"]

def fetch_historic_stock_price(ticker):
    startDate = datetime.today().date() - timedelta(weeks=260)
    endDate = datetime.today().date()
    qtr_Obj={}
    try:
        if not API:
            raise EnvironmentError("ALPHA key not found in environment variables.")
        
        url=f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={ticker}&apikey={API}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)  
        jsonObj = response.json()
    except:
        print("Error trying to fetch data")
    qtr_Obj={key_date:key_value['4. close'] for key_date,key_value in jsonObj['Monthly Adjusted Time Series'].items()}

    return qtr_Obj

def db_4qtr_data_fetch(db,ticker,collection='QtrStockData'):
    collection_QtrStockData=db[collection]

    Object = collection_QtrStockData.aggregate(
        [
    {
        '$match': {
            'ticker': ticker.upper(), 
            'frame': {
                '$ne': None, 
                # '$not': {
                #     '$regex': 'I$'
                # }
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
        key:f"{round((item/Assets.get(key,0))*100,1)}%" for key,item in net_income.items()
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
    
    tickers = ['COF']  # Replace with your desired ticker
    all_data = []
    

    # all_data = [fetch_5y_data(ticker)for ticker in tickers]
    all_data={
        ticker:{
        'financial_data':fetch_4qtr_data(ticker)    
        }for ticker in tickers
    }
    print(all_data)
        
    
    
    



    

    