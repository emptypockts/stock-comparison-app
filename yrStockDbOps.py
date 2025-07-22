from datetime import datetime
import os
import pandas as pd
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from pymongo import MongoClient,UpdateOne
from companyData import fetch_metric,fetch_price_fmp
from financialUtils import (
    get_metric_keys,fetch_ticker,
    serialize_cursor,
    write_object,
    push_StockData,
    swap_temp_prod)
from pymongo.collection import Collection,Cursor
from typing import Literal
import json
load_dotenv()

uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
KY = os.getenv('TWELVE_API_KY')
URL_BASE = os.getenv('TWELVE_URI')

#refresh database with latest companyfacts
def fetch_yearly_data():
    db = client['test']
    collection=db['tickerCIK']
    is_stored=set()
    path = r"C:\\Users\\ejujo\\Downloads\\companyfacts\\"
    files = os.listdir(path)
    yrly_obj = []
    nasdaq =pd.read_csv(r"C:\\Users\ejujo\\coding\\nasdaq.csv")
    metric_keys=get_metric_keys()
    # for file in files:
        # use to debug
    for file in files[:3:]: 
        cik_integer = int(file[:-5].lstrip("CIK").lstrip("0"))
        ticker=fetch_ticker(cik_integer,collection)
        if ticker and ticker in nasdaq['ticker'].values:
            with open(path + file) as f:
                item = json.loads(f.read())
        # Iterate through items in the dataset
                if item and 'entityName' in item and 'facts' in item and 'us-gaap' in item['facts'] and 'cik' in item:
                    for metric_name, key_value in metric_keys.items():
                        # Check if the metric exists in the current item
                        if metric_name in item['facts']['us-gaap']:
                            if 'USD' in item['facts']['us-gaap'][metric_name]['units'] or 'USD/shares' in item['facts']['us-gaap'][metric_name]['units'] or 'shares' in item['facts']['us-gaap'][metric_name]['units']:
                                if metric_name=='EarningsPerShareBasic' or metric_name=='EarningsPerShareDiluted':
                                    metrics = item['facts']['us-gaap'][metric_name]['units']['USD/shares']
                                elif metric_name=='WeightedAverageNumberOfSharesOutstandingBasic' or metric_name=='CommonStockSharesOutstanding':
                                    metrics = item['facts']['us-gaap'][metric_name]['units']['shares']
                                else:
                                    metrics = item['facts']['us-gaap'][metric_name]['units']['USD']
                                for metric in metrics:
                                    # Process only 10-K forms with a frame
                                    endDate=datetime.strptime(metric['end'],'%Y-%m-%d')
                                    if metric['form'] == '10-K' and (endDate.year>2019):
                                        concat_index=(ticker,metric_name,metric['val'],metric['end'])
                                        if concat_index not in is_stored:
                                            is_stored.add(concat_index)
                                            yrly_obj.append({
                                                    'ticker':ticker,
                                                    'entity':item['entityName'],
                                                    'metric':metric_name,
                                                    'value':metric['val'],
                                                    'date':metric['end'],
                                                    'form':metric['form'],
                                                    'fp':metric.get('fp',None),
                                                    'frame':metric.get('frame',None)
                                                    })
    return yrly_obj

#calculate cagr fcf and insert doc
def calculate_historical_growth_rate(first,last,collection:Collection):
    if 'value' not in first and 'value' not in last:
        raise Exception('not enough data to calculate growth. use 5% instead')
    num_years = int(datetime.fromisoformat(last.get('date')).year)-int(datetime.fromisoformat(first.get('date')).year)    
    start_value = first.get('value')
    end_value = last.get('value')
    if start_value <= 0 or end_value <= 0:
        raise Exception('not enough data to calculate growth. use 5% instead')
    
    cagr = (end_value / start_value) ** (1 / num_years) - 1
    new_doc={
            "ticker":last.get('ticker'),
            "entity":last.get('entity','unknown'),
            "metric":"fcf_cagr",
            "value":cagr*100,
            "frame":last.get('frame'),
            "calculated_from":{
                "firstFcf":first.get('value'),
                "lastFcf":last.get('value')
            },
            "date":last.get('date',''),
            "form":last.get('form',''),
            "fp":last.get('fp','')
        }
    return new_doc if new_doc else {}
        
#calculate fcf and insert doc
def fcf_generate_doc(ticker,collection:Collection):
    cash_metric='NetCashProvidedByUsedInOperatingActivities'
    capex_metric='PaymentsToAcquirePropertyPlantAndEquipment'
    actual_year = datetime.now().year
    new_doc=[]
    for i in range(actual_year-5,actual_year):
        
        cash_doc=fetch_metric(collection,ticker,[cash_metric],mode='year',calendar_yr=str(i))
        capex_doc=fetch_metric(collection,ticker,[capex_metric],mode='year',calendar_yr=str(i))
        cash = cash_doc.get('value',0) if cash_doc else 0
        raw_capex = capex_doc.get('value',0) if capex_doc else 0
        total_capex=abs(raw_capex)
        fcf = cash-total_capex
        if cash>0:
            new_doc.append({
                "ticker":ticker.upper(),
                "entity":cash_doc.get('entity','unknown'),
                "metric":"fcf",
                "value":fcf,
                "frame":cash_doc.get('frame',''),
                "calculated_from":{
                    "cash_value":cash,
                    "capex_value":total_capex
                },
                "date":cash_doc.get('date',''),
                "form":cash_doc.get('form',''),
                "fp":cash_doc.get('fp','')
            })
                
    return new_doc if new_doc else []

#calculate total debt and insert doc       
def total_debt_calc(ticker,collection:Collection):
    short_term_debt_metric=['ShortTermDebt','ShortTermBorrowings','DebtCurrent','LongTermDebtAndCapitalLeaseObligationsCurrent','CurrentDebtAndCapitalLeaseObligation','CommercialPaper','OtherShortTermBorrowings']
    long_term_debt_metric=['LongTermDebt','BondsPayableNoncurrent','LongTermBorrowings','MortgageLoansOnRealEstate','Noncurrent','DebtNoncurrent','AndCapitalLeaseObligation','LongTermDebtNoncurrent']
    actual_year = datetime.now().year
    total_debt_obj=[]

    for i in range(actual_year-5,actual_year):
        new_doc={'calculated_from':{}}
        short_term_debt = fetch_metric(collection,ticker.upper(),metric=short_term_debt_metric,mode='year',calendar_yr=str(i),unique_metric=False)
        short_acc_debt=0
        long_acc_debt=0
        for e in short_term_debt:  
            short_term_debt_value=e.get('value',0) or 0
            if  e['metric']=='ShortTermDebt':
                new_doc['calculated_from']['short_term_debt']=short_term_debt_value
                new_doc['date']=e.get('date','')
                new_doc['form']=e.get('form','')
                new_doc['fp']=e.get('fp','')
                new_doc['ticker']=ticker.upper()
                new_doc['frame']=e.get('frame','')
                new_doc['entity']=e.get('entity','')
                break
            short_acc_debt+=short_term_debt_value
            if 'short_term_debt' not in new_doc['calculated_from'] and short_acc_debt:
                new_doc['calculated_from']['short_term_debt']=short_acc_debt
                new_doc['date']=e.get('date','')
                new_doc['form']=e.get('form','')
                new_doc['fp']=e.get('fp','')
                new_doc['ticker']=ticker.upper()
                new_doc['frame']=e.get('frame','')
                new_doc['entity']=e.get('entity','')

        long_term_debt =fetch_metric(collection,ticker.upper(),metric=long_term_debt_metric,mode='year',calendar_yr=str(i),unique_metric=False)
        for e in long_term_debt:
            long_term_debt_value=e.get('value',0) or 0
            if e['metric']=='LongTermDebt':
                
                new_doc['calculated_from']['long_term_debt']=long_term_debt_value
                new_doc['date']=e.get('date','')
                new_doc['form']=e.get('form','')
                new_doc['fp']=e.get('fp','')
                new_doc['ticker']=ticker.upper()
                new_doc['frame']=e.get('frame','')
                new_doc['entity']=e.get('entity','')
                break
            long_acc_debt+=long_term_debt_value
            if 'long_term_debt' not in new_doc['calculated_from'] and long_acc_debt:
                new_doc['calculated_from']['long_term_debt']=long_acc_debt
                new_doc['date']=e.get('date','')
                new_doc['form']=e.get('form','')
                new_doc['fp']=e.get('fp','')
                new_doc['ticker']=ticker.upper()
                new_doc['frame']=e.get('frame','')
                new_doc['entity']=e.get('entity','')
        
        short_term=new_doc['calculated_from'].get('short_term_debt',0)
        long_term=new_doc['calculated_from'].get('long_term_debt',0)
        total=short_term+long_term
        if total>0:
            new_doc['value']=total
            new_doc['metric']='total_debt'
            total_debt_obj.append(new_doc)
            
    return total_debt_obj if total_debt_obj else []

def market_cap_calc(ticker,shares_cursor:Cursor):
    prices_series=fetch_price_fmp(ticker,mode='5y')
    market_cap_list=[]
    for e in shares_cursor:
        if datetime.fromisoformat(e.get('date','')).year in prices_series.index:
            result=float(e.get('value',0)*prices_series['close'][pd.to_datetime(e.get('date',0)).year])
            new_doc={
                
                'ticker':e.get('ticker',''),
                'entity':e.get('entity',''),
                'metric':'market_cap',
                'value':result,
                'date':e.get('date',''),
                'form':e.get('form',''),
                'fp':e.get('fp',''),
                'frame':e.get('frame',''),
                'calculated_from':{
                    'price_close':float(prices_series['close'][pd.to_datetime(e.get('date',0)).year]),
                    'WeightedAverageNumberOfSharesOutstandingBasic':e.get('value',0)
                }
            }
            market_cap_list.append(new_doc)
    return market_cap_list
def total_assets_calc(ticker,collection:Collection):
    assets_metric=['Assets']
    fallback_metric=['AssetsCurrent','OtherAssetsCurrent','AssetsNonCurrent','OtherAssetsNonCurrent']
    actual_year = datetime.now().year
    total_assets_obj=[]

    for i in range(actual_year-5,actual_year):
        new_doc={'calculated_from':{}}
        current_assets_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=assets_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False)
        if current_assets_cursor:
            break
        else:
            fallback_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=fallback_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False
        )
            if fallback_cursor:
                assets_acc=0
                for a in fallback_cursor:
                    new_doc['date']=a.get('date','')
                    new_doc['form']=a.get('form','')
                    new_doc['fp']=a.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=a.get('frame','')
                    new_doc['entity']=a.get('entity','')
                    val=a.get('value',0) or 0
                    assets_acc+=val
                    if a.get('metric') in fallback_metric:
                        new_doc['calculated_from'][a.get('metric')]=val
                        new_doc['metric']='Assets'
                        new_doc['value']=assets_acc
            total_assets_obj.append(new_doc)
    return total_assets_obj

def current_liabilities_calc(ticker:str,collection:Collection):
    # Current Liabilities = Accounts Payable + Short-Term Debt + Accrued Expenses + Other Current Liabilities
    # taxonomy https://xbrl.us/wp-content/uploads/2015/03/PreparersGuide.pdf
    # Total Current Liabilities is LiabilitiesCurrent 
    # long term liabilities =Long-Term Debt + Deferred Tax Liabilities + Pension Liabilities + Other Long-Term Liabilities
    # Long-Term Debt is LongTermDebtNoncurrent 
    # Other Long-Term Liabilities is OtherLiabilitiesNoncurrent
    # total_liabilities=long term liabilities+Current Liabilities
    # Total Liabilities is Liabilities
    new_doc={'calculated_from':{}}
    total_liabilities_metric=['Liabilities']
    fallback_liabilities_metric=['LiabilitiesCurrent']
    current_liabilities_metrics=[
        'LongTermDebtCurrent',
        'AccountsPayableTradeCurrent',
        'EmployeeRelatedLiabilitiesCurrent',
        'OtherAccruedLiabilitiesCurrent',
        'DividendsPayableCurrent',
        'AccruedIncomeTaxesCurrent'
        ]
    actual_year = datetime.now().year
    total_current_liabilities_obj=[]
    for i in range(actual_year-5,actual_year):
        liabilities_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=total_liabilities_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False)
        if liabilities_cursor:
            print(f"total liability for year {i} already exists")
        else:
            fallback_liabilities_cursor=fetch_metric(
                collection,
                ticker.upper(),
                metric=fallback_liabilities_metric,
                mode='year',
                calendar_yr=str(i),
                unique_metric=False
                )
            if fallback_liabilities_cursor:
                print(f"current liability for year {i} already exists")
            else:
                current_liabilities_cursor=fetch_metric(
                collection,ticker.upper(),
                metric=current_liabilities_metrics,
                mode='year',
                calendar_yr=str(i),
                unique_metric=False)
                if current_liabilities_cursor:
                    current_liabilities_acc=0
                    
                    for a in current_liabilities_cursor:
                        new_doc['date']=a.get('date','')
                        new_doc['form']=a.get('form','')
                        new_doc['fp']=a.get('fp','')
                        new_doc['ticker']=ticker.upper()
                        new_doc['frame']=a.get('frame','')
                        new_doc['entity']=a.get('entity','')
                        val = a.get('value',0) or 0
                        current_liabilities_acc+=val
                        if a.get('metric') in current_liabilities_metrics:
                            new_doc['calculated_from'][a.get('metric')]=val
                        new_doc['metric']='LiabilitiesCurrent'
                        new_doc['value']=current_liabilities_acc
                    total_current_liabilities_obj.append(new_doc)
    return total_current_liabilities_obj

def long_term_liabilities_calc(ticker:str,collection:Collection):
    total_liabilities_metric=['Liabilities']
    fallback_liabilities_metric=['LiabilitiesNoncurrent']
    long_term_liabilities_metrics=[
    "LongTermDebtNoncurrent",
    "PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent",
    "OperatingLeaseLiabilityNoncurrent",
    "DeferredIncomeTaxLiabilitiesNoncurrent",
    "OtherLiabilitiesNoncurrent",
    "FinanceLeaseLiabilityNoncurrent",
    "DeferredCompensationLiabilities",
    "ContingentConsiderationLiabilityNoncurrent",
    "DeferredRevenueNoncurrent",
    "LiabilitiesNoncurrentExcludingLongTermDebt",
    "OtherEmployeeRelatedLiabilitiesNoncurrent"
    ]
    actual_year = datetime.now().year
    total_long_term_liabilities_obj=[]
    for i in range(actual_year-5,actual_year):
        new_doc={'calculated_from':{}}
        liabilities_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=total_liabilities_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False
        )
        if liabilities_cursor:
            print(f"total liability for year {i} already exists")
        else:
            fallback_liabilities_cursor=fetch_metric(
                collection,
                ticker.upper(),
                metric=fallback_liabilities_metric,
                mode='year',
                calendar_yr=str(i),
                unique_metric=False
            )
            if fallback_liabilities_cursor:
                print(f"long term liability for year {i} already exists")
            else:
                long_term_liabilities_cursor=fetch_metric(
                    collection,
                    ticker.upper(),
                    metric=long_term_liabilities_metrics,
                    mode='year',
                    calendar_yr=str(i),
                    unique_metric=False
                )
                if long_term_liabilities_cursor:
                    long_term_liabilities_acc=0
                    
                    for a in long_term_liabilities_cursor:
                        new_doc['date']=a.get('date','')
                        new_doc['form']=a.get('form','')
                        new_doc['fp']=a.get('fp','')
                        new_doc['ticker']=ticker.upper()
                        new_doc['frame']=a.get('frame','')
                        new_doc['entity']=a.get('entity','')
                        val = a.get('value',0) or 0
                        long_term_liabilities_acc+=val
                        if a.get('metric') in long_term_liabilities_metrics:
                            new_doc['calculated_from'][a.get('metric','')]=val
                            new_doc['metric']='LiabilitiesNoncurrent' 
                            new_doc['value']=long_term_liabilities_acc
                    total_long_term_liabilities_obj.append(new_doc)
    return(total_long_term_liabilities_obj)                       

def total_liabilities_calc(ticker:str,collection:Collection):
    total_liabilities_metric=['Liabilities']
    fallback_total_liabilities_metric=['LiabilitiesNoncurrent','LiabilitiesCurrent']
    actual_year = datetime.now().year
    total_liabilities_obj=[]
    for i in range(actual_year-5,actual_year):
        new_doc={'calculated_from':{}}
        total_liabilities_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=total_liabilities_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False
        )
        if total_liabilities_cursor:
            print(f"total liability for year {i} already exists")
        else:
            fallback_total_liabilities_cursor=fetch_metric(
                collection,
                ticker.upper(),
                metric=fallback_total_liabilities_metric,
                mode='year',
                calendar_yr=str(i),
                unique_metric=False
            )
            if fallback_total_liabilities_cursor:
                total_liabilities_acc=0
                for a in fallback_total_liabilities_cursor:
                    new_doc['date']=a.get('date','')
                    new_doc['form']=a.get('form','')
                    new_doc['fp']=a.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=a.get('frame','')
                    new_doc['entity']=a.get('entity','')
                    val = a.get('value',0) or 0
                    total_liabilities_acc+=val
                    
                    if a.get('metric') in fallback_total_liabilities_metric:
                        new_doc['calculated_from'][a.get('metric')]=val
                        new_doc['metric']='Liabilities'
                        new_doc['value']=total_liabilities_acc
                total_liabilities_obj.append(new_doc)
    return total_liabilities_obj

def book_value_calc(ticker:str,collection:Collection):
    book_value_metrics=['Liabilities','Assets']
    actual_year = datetime.now().year
    book_value_obj=[]
    for i in range(actual_year-5,actual_year):
        new_doc={'calculated_from':{}}
        book_value_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=book_value_metrics,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False
        )
        if book_value_cursor:
            book_value_acc=0
            for a in book_value_cursor:
                new_doc['date']=a.get('date','')
                new_doc['form']=a.get('form','')
                new_doc['fp']=a.get('fp','')
                new_doc['ticker']=ticker.upper()
                new_doc['frame']=a.get('frame','')
                new_doc['entity']=a.get('entity','')
                val = a.get('value',0) or 0
                if a.get('metric') in book_value_metrics:
                    new_doc['calculated_from'][a.get('metric')]=val
            assets_val=new_doc['calculated_from'].get('Assets')
            liabilities_val=new_doc['calculated_from'].get('Liabilities')
            new_doc['metric']='book_value'
            new_doc['value']=assets_val-liabilities_val
            book_value_obj.append(new_doc)
    return book_value_obj






if __name__=='__main__':
# write the raw edgar db

    db = client['test']
    edgar_collection = db['rawEdgarCollection']
    #line for testing functions
    tickers=['abt','air']
# define metrics
    outstanding_shares_metric=['WeightedAverageNumberOfSharesOutstandingBasic','BasicSharesOutstanding','CommonStockSharesOutstanding']
    fcf_metric=['fcf']
    fcf_cagr_metric=['fcf_cagr']
    dividends_metric=['PaymentsOfDividends','PaymentsOfDividendsCommonStock']
    stock_holders_equity_metric=['StockholdersEquity','StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest']
    basic_eps_metric=['EarningsPerShareBasic']
    diluted_eps_metric=['EarningsPerShareDiluted']
    short_term_debt_metric=['ShortTermBorrowings','ShortTermDebt','CurrentPortionOfLongTermDebt','CurrentDebtAndCapitalLeaseObligation','DebtCurrent']
    long_term_debt_metric=['LongTermDebtNoncurrent','LongTermBorrowings','LongTermDebt','DebtNoncurrent','LongTermDebtAndCapitalLeaseObligation']
# # # fetch companyfacts and create the rawEdgarCollection
#     object= fetch_yearly_data()
#     index_params=[{
#         "fields":[("ticker",1),("metric",1),("date",1),("value",1)],
#         "unique":True
#     }]
#     push_StockData(
#         db,
#         object,
#         collection='rawEdgarCollection',
#         ordered_mode=False,
#         index_list=index_params
#         )

    for ticker in tickers:
# # calculate total debt and write it on rawEdgarCollection
#         total_debt_object=total_debt_calc(ticker,edgar_collection)
#         if total_debt_object:
#             write_object(edgar_collection,total_debt_object,mode='many')
# # calculate free cash flow
#         fcf_object= fcf_generate_doc(ticker,edgar_collection)
#         if fcf_object:
#             write_object(edgar_collection,fcf_object,mode='many')
# # extract first and last fcf to calculate cagr
#         first_fcf=fetch_metric(edgar_collection,ticker,metric=fcf_metric,mode='first')
#         last_fcf=fetch_metric(edgar_collection,ticker,metric=fcf_metric,mode='last')
#         cagr_obj=calculate_historical_growth_rate(first_fcf,last_fcf,edgar_collection)
#         if cagr_obj:
#             write_object(edgar_collection,cagr_obj)
# # get price and shares for last 5y and calculate market cap
#         all_avg_shares=fetch_metric(edgar_collection,ticker.upper(),metric=outstanding_shares_metric,mode='all')
#         stock_price_df=fetch_price_fmp(ticker,mode='5y')
#         market_cap_obj=market_cap_calc(ticker,all_avg_shares)
#         if market_cap_obj:
#             write_object(edgar_collection,market_cap_obj,mode='many')

# # calculate total assets
#         total_assets_obj=total_assets_calc(ticker,edgar_collection)
#         if total_assets_obj:
#             print(total_assets_obj)
#             write_object(edgar_collection,total_assets_obj,mode='many')


# # calculate total current liabilities
#         current_liabilities_obj=current_liabilities_calc(ticker,edgar_collection)
#         if current_liabilities_obj:
#             write_object(edgar_collection,current_liabilities_obj,mode='many')
        
# # calculate long term liabilities
#         long_term_liabilities_obj=long_term_liabilities_calc(ticker,edgar_collection)
#         if long_term_liabilities_obj:
#             write_object(edgar_collection,long_term_liabilities_obj,mode='many')
# # calculate total liabilities
        # total_liabilities_obj=total_liabilities_calc(ticker,edgar_collection)
        # if total_liabilities_obj:
        #     write_object(edgar_collection,total_liabilities_obj,mode='many')
# calculate book value
        book_value_obj=book_value_calc(ticker,edgar_collection)
        if book_value_obj:
            print(book_value_obj)
            # write_object(edgar_collection,book_value_obj,mode='many')
            

        
    