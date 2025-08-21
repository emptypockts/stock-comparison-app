from typing import Literal
from pymongo.collection import Collection,Cursor
from pymongo import errors,DESCENDING,MongoClient
from datetime import datetime,timedelta
import pandas as pd
import requests
from dotenv import load_dotenv
import os
load_dotenv()
KY = os.getenv('TWELVE_API_KY')
URL_BASE = os.getenv('TWELVE_URI')
def fetch_tickers(collection:Collection)->list:
    path = r"C:\\Users\\ejujo\\Downloads\\companyfacts\\"
    files = os.listdir(path)
    nasdaq =pd.read_csv(r"C:\\Users\ejujo\\coding\\nasdaq.csv")
    ciks=[int(e[:-5].lstrip("CIK").lstrip("0"))for e in files]
    tickers=fetch_ticker(ciks,collection)
    stock_list=[]
    for e in tickers:
        if e in nasdaq['ticker'].values:
            stock_list.append(e)
    return stock_list
def get_metric_keys():
 return {
        "RevenueFromContractWithCustomerExcludingAssessedTax":"revenue",
        "RevenueFromContractWithCustomerIncludingAssessedTax":"revenue",
        "Revenues":"revenue",
        "Assets":"assets",
        "AssetsCurrent":"assets",
        "AssetsNoncurrent":"assetsNonCurrent",
        "OtherAssetsCurrent":"assets",
        "OtherAssetsNoncurrent":"assetsNonCurrent",
        "CashAndCashEquivalentsAtCarryingValue":"endCashPosition",
        "Liabilities":"liabilities",
        "NetIncomeLoss":"netIncome",
        "ResearchAndDevelopmentExpense":"rAndD",
        "NetCashProvidedByUsedInOperatingActivities":"operatingCashFlow",
        "PaymentsOfDividends":"dividends",
        "PaymentsOfDividendsCommonStock":"dividends",
        "EntityCommonStockSharesOutstanding":"outstandingShares",
        "StockholdersEquity":"stockholdersEquity",
        "WeightedAverageNumberOfSharesOutstandingBasic":"outstandingShares",
        "BasicSharesOutstanding":"outstandingShares",
        "CommonStockSharesOutstanding":"outstandingShares",
        "EarningsPerShareBasic":"EPS",
        "EarningsPerShareDiluted":"EPSDiluted",
        "CommercialPaper":"CommercialPaper",
        "OtherLiabilitiesCurrent":"LiabilitiesCurrent",
        "OtherLiabilitiesNoncurrent":"LiabilitiesLongTerm",
        "OtherAccruedLiabilitiesCurrent":"LiabilitiesCurrent",
        "LiabilitiesCurrent":"LiabilitiesCurrent",
        "LiabilitiesNoncurrent":"LiabilitiesLongTerm",
        "PaymentsToAcquirePropertyPlantAndEquipment":"capex",
        "NetCashProvidedByUsedInInvestingActivities":"capex2",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest":"StockholdersEquity",
        "CurrentPortionOfLongTermDebt":"ShortTermDebt",
        "ShortTermBorrowings":"ShortTermDebt",
        "ShortTermDebt":"ShortTermDebt",
        "DebtCurrent":"ShortTermDebt",
        "LongTermDebtAndCapitalLeaseObligationsCurrent":"ShortTermDebt",
        "CurrentDebtAndCapitalLeaseObligation":"ShortTermDebt",
        "OtherShortTermBorrowings":"ShortTermDebt",
        "BondsPayableNoncurrent":"LongTermDebt",
        "LongTermBorrowings":"LongTermDebt",
        "MortgageLoansOnRealEstate":"LongTermDebt",
        "LongTermDebtNoncurrent":"LongTermDebt",
        "DebtNoncurrent":"LongTermDebt",
        "LongTermDebtAndCapitalLeaseObligation":"LongTermDebt",
        "LongTermDebt":"LongTermDebt",
        "AccountsPayableTradeCurrent":"LiabilitiesCurrent",
        "InventoryNet":"LiabilitiesCurrent",
        "AccountsPayableCurrent":"LiabilitiesCurrent",
        "CostOfGoodsSold":"LiabilitiesCurrent",
        "LongTermDebtCurrent":"LiabilitiesCurrent",
        "EmployeeRelatedLiabilitiesCurrent":"LiabilitiesCurrent",
        "DividendsPayableCurrent":"LiabilitiesCurrent",
        "AccruedIncomeTaxesCurrent":"LiabilitiesCurrent",
        "PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent":"LiabilitiesLongTerm",
        "OperatingLeaseLiabilityNoncurrent":"LiabilitiesLongTerm",
        "UnrecognizedTaxBenefits":"LiabilitiesLongTerm",
        "DeferredIncomeTaxLiabilitiesNoncurrent":"LiabilitiesLongTerm",
        "OtherNoncurrentLiabilities":"LiabilitiesLongTerm",
        "FinanceLeaseLiabilityNoncurrent":"LiabilitiesLongTerm",
        "DeferredCompensationLiabilities":"LiabilitiesLongTerm",
        "ContingentConsiderationLiabilityNoncurrent":"LiabilitiesLongTerm",
        "DeferredRevenueNoncurrent":"LiabilitiesLongTerm",
        "LiabilitiesNoncurrentExcludingLongTermDebt":"LiabilitiesLongTerm",
        "OtherEmployeeRelatedLiabilitiesNoncurrent":"LiabilitiesLongTerm"
    }

def fetch_ticker(cik:list,collection:Collection):
    query={
        'cik_str':
        {"$in":cik}
    }
    
    
    ticker=collection.find(
        query
    )
    if collection.count_documents(query)>0:
        tickers=[e['ticker'] for e in ticker] 
        return tickers
    else:
        return []
    
def fetch_cik(ticker,collection):
    filter={
        'ticker':ticker.upper()
    }
    project={
    'cik_str': 1, 
    '_id': 0
    }
    
    cik=collection.find_one(
        filter=filter,
        projection=project
    )
    if cik:
        return cik['cik_str'] 
    else:
        return None
    
def Transform_Obj_and_Date(Object):
    import pandas as pd
    index = pd.to_datetime(Object.index)
    Object_df = pd.DataFrame(Object, index=index,columns=[Object.name])
    Object_df.index = Object_df.index.year
    Object_df.index.name = 'Date'
    Object_df[Object.name] = Object_df[Object.name].astype(float)
    try:
        Object_df = Object_df.drop(2019)
    except:
        return Object_df
    return Object_df

def serialize_cursor(cursor:Cursor,key:str,value:str,series_name:str,index_name:str=None):
    index=[]
    values=[]
    for e in cursor:
        index.append(e.get(key,''))
        values.append(e.get(value,''))
    return pd.Series(data=values,index=index,name=series_name)

def write_object(collection:Collection,object,mode:Literal['one','many']='one'):
    try:
        if mode=='one':
            collection.insert_one(object)
        elif mode=='many':
            collection.insert_many(object)
    except Exception as e:
        print('error updating collection: ',str(e))

def push_StockData(db, objects, collection:str,ordered_mode:bool=True,index_list:list=[]):
    today = datetime.now().strftime("%m_%d_%y_%H_%M_%S")
    prod_collection = collection
    temp_collection = f"temp_{collection}"
    bakcup_collection= f"{prod_collection}_{today}"
    if temp_collection in db.list_collection_names():
        db.drop_collection(temp_collection)
    try:
        stock_collection = db[temp_collection]
        # Inject the objects into the database
        if index_list:
            for i in index_list:
                stock_collection.create_index(i["fields"],unique=i.get('unique',True))
        result = stock_collection.insert_many(objects,ordered=ordered_mode)
        assert stock_collection.count_documents({})>0
        db[prod_collection].rename(bakcup_collection)
        db[temp_collection].rename(prod_collection)
    except errors.BulkWriteError as bwe:
        print(f"Bulk write error: {bwe.details}")
    except errors.ConnectionFailure as cf:
        print(f"Connection failure: {cf}")
    except errors.OperationFailure as ofe:
        print(f"Operation failure: {ofe}")
    except Exception as e:
        print(f"An error occurred: {e}")

def swap_temp_prod(db,collection):
    today = datetime.now().strftime("%m_%d_%y_%H_%M_%S")
    prod_collection = collection
    temp_collection = f"temp_{collection}"
    bakcup_collection= f"{prod_collection}_{today}"
    try:
        db[prod_collection].rename(bakcup_collection)
        db[temp_collection].rename(prod_collection)
        db.drop_collection(temp_collection)
        print('temp to prod swap done successfully')
    except errors.BulkWriteError as bwe:
        print(f"Bulk write error: {bwe.details}")
    except errors.ConnectionFailure as cf:
        print(f"Connection failure: {cf}")
    except errors.OperationFailure as ofe:
        print(f"Operation failure: {ofe}")

def create_index(db):
    try:
        # db['aiTasks']
        # db['QtrStockData']
        # db['QtrStockRevTrend']
        # db['RefreshToken']
        # db['StockScore']
        # db['tickerCIK']
        # db['User']
        db['QtrDeiStockData'].create_index([("ticker", 1), ("metric", 1), ("date", -1)])

    except Exception as e:
        print('error creating collection',str(e))

def fetch_price_fmp(
        collection:Collection,
        ticker,
        mode:Literal["last","5y","calendar_yr"]="last",
        calendar_yr:int=None,
        maintenance:bool=False
        ):
    import calendar
    import time
    import json
    if mode=='last':
        URL = f"{URL_BASE}/price?symbol={ticker.upper()}&apikey={KY}&source=docs"
        response = requests.get(URL)
        try:
            price = float(response.json()['price'])
        except Exception as e:
            print('error: ',str(e))
            price = 0
        return price
    elif mode=='5y':
        years_list=[]
        end_date = datetime.now().date()
        start_date = end_date-timedelta(days=365*5)
        for i in range(start_date.year,end_date.year):
            years_list.append(i)
        query={
            "ticker":ticker.upper(),
            "metric":"price_close",
            "date":{
                "$in":years_list
            }
        }
        cursor= collection.find(query).sort("date",DESCENDING)
        collection_count=collection.count_documents(query)
        price_series=[]
        if collection_count!=len(years_list) and maintenance==True:
            print(f"doc count {collection_count} not matching list of years {years_list}")
            years_cursor=[]
            for a in cursor:
                years_cursor.append(a.get('date'))
                a.pop("_id")
                price_series.append(a)
            missing_years=list(set(years_list)-set(years_cursor))
            print('missing years are ',missing_years)
            for year in missing_years:
                missing_start_date=str(year)+'-12-30'
                missing_end_date=str(year)+'-12-31'
                URL = f"{URL_BASE}/time_series?start_date={missing_start_date}&end_date={missing_end_date}\
                    &symbol={ticker.upper()}&interval=1day&apikey={KY}"
                response = requests.get(URL)
                time.sleep(7.5)
                try:
                    historic_stock_prices = response.json()
                    if 'code' in historic_stock_prices:
                        print("code error",historic_stock_prices)
                        return pd.Series(0)
                    if 'values' in historic_stock_prices:      
                        values= historic_stock_prices['values']
                        price_object={}
                        for e in values:
                            price_object['ticker']=historic_stock_prices['meta'].get('symbol')
                            price_object['date']=datetime.fromisoformat(e.get('datetime')).year
                            price_object['metric']='price_close'
                            price_object['value']=float(e.get('close'))
                        if price_object:
                            write_object(collection,price_object)
                            price_series.append(price_object)
                except Exception as e:
                    print(f"error calling api: {str(e)}")
        else:
            price_series=list(cursor)  
        return price_series
                
                            

    elif mode=='calendar_yr':
        if calendar_yr==datetime.now().year:
            URL = f"{URL_BASE}/price?symbol={ticker.upper()}&apikey={KY}&source=docs"
            response = requests.get(URL)
            time.sleep(7.5)
            try:
                price = float(response.json()['price'])
            except Exception as e:
                print('error: ',str(e))
                price = 0
            return price
        else:
            start_date = datetime(year=calendar_yr,month=12,day=30).date()
            end_date=datetime(year=calendar_yr,month=12,day=31).date()
            URL = f"{URL_BASE}/time_series?start_date={start_date}&end_date={end_date}&symbol={ticker.upper()}&interval=1day&apikey={KY}"
            response = requests.get(URL)
            # time.sleep(7.5)
            print('status code',response.status_code)
            print('ticker',ticker)
            try:
                historic_stock_prices = response.json()
                if 'code' in historic_stock_prices:
                    return pd.Series(0)
                if 'values' in historic_stock_prices:      
                    values= historic_stock_prices['values']
                    date=[]
                    close=[]
                    for e in values:
                        date.append(datetime.fromisoformat(e.get('datetime','')))
                        close.append(float(e.get('close','')))
                    stock_price=pd.Series(data=close,index=date,name='close')
                    stock_price.index.name='date'
                    df= Transform_Obj_and_Date(stock_price)
                    if df is None:
                        return pd.Series(0)
                    else:
                        return df


            except Exception as e:
                print(f"error calling api: {str(e)}")

def fetch_metric(
        collection:Collection,
        ticker:str,
        metric:list,
        mode:Literal["last","all","year","first"]="all",
        calendar_yr:str=None,
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
        return last_doc if collection.count_documents(query)>0 else {}
    if mode =='first' and unique_metric:
        first_doc = collection.find_one(query,sort=[("date",1)])
        return first_doc if first_doc else {}
    elif mode=='first'and not unique_metric:
        first_doc = collection.find(query).sort("date",DESCENDING)
        return first_doc if collection.count_documents(query)>0 else {}
    elif mode=='all':
        return collection.find(query).sort("date",DESCENDING) if collection.count_documents(query)>0 else {}
    elif mode=='year'and unique_metric:
        if not calendar_yr or len(calendar_yr)!=4:
            raise ValueError('year most be provided in format yyyy for example 2024')
        query['$or']=[
            {
                "date":int(calendar_yr)
            },
            {
                "date":{
                    "$regex":f"^{calendar_yr}"
                }
            }
        ]
        year_doc=collection.find_one(query,sort=[("date",-1)])
        return year_doc if year_doc else {}
    elif mode=='year' and not unique_metric:
        if not calendar_yr or len(calendar_yr)!=4:
            raise ValueError('year most be provided in format yyyy for example 2024')
        query['$or']=[
            {
                "date":int(calendar_yr)
            },
            {
                "date":{
                    "$regex":f"^{calendar_yr}"
                }
            }
        ]
        year_doc=collection.find(query).sort("date",DESCENDING)
        return year_doc if collection.count_documents(query)>0 else {}
        

    return []




if __name__=="__main__":
        current_y=datetime.now().year
        for i in range(current_y-5,current_y+1):
            price=fetch_price_fmp('MSFT',mode='calendar_yr',calendar_yr=i)
            print(price)
