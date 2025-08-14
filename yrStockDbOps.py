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
def fetch_tickers(collection:Collection)->list:
    path = r"C:\\Users\\ejujo\\Downloads\\companyfacts\\"
    files = os.listdir(path)
    nasdaq =pd.read_csv(r"C:\\Users\ejujo\\coding\\nasdaq.csv")
    ciks=[int(e[:-5].lstrip("CIK").lstrip("0"))for e in files]
    tickers=fetch_ticker(ciks,collection)
    return tickers
#refresh database with latest companyfacts
def fetch_yearly_data():
    db = client['test']
    collection=db['tickerCIK']
    is_stored=set()
    path = r"C:\\Users\\ejujo\\Downloads\\companyfacts\\"
    files = os.listdir(path)
    yrly_obj = []
    tickers=[]
    nasdaq =pd.read_csv(r"C:\\Users\ejujo\\coding\\nasdaq.csv")
    metric_keys=get_metric_keys()
    for file in files:
        # use to debug
    # for file in files[:3:]: 
        cik_integer = int(file[:-5].lstrip("CIK").lstrip("0"))
        ticker=fetch_ticker(cik_integer,collection)
        tickers.append(ticker)
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
    return yrly_obj,tickers
#calculate cagr fcf and insert doc
def calculate_historical_growth_rate(first,last,collection:Collection):
    if 'value' not in first and 'value' not in last:
        return {}
    else:
        num_years = int(datetime.fromisoformat(last.get('date')).year)-int(datetime.fromisoformat(first.get('date')).year)    
        start_value = first.get('value',0)
        end_value = last.get('value',0)
        verify_fcf_cagr_cursor=fetch_metric(
        collection=collection,
        ticker=first.get('ticker'),
        metric=['fcf_cagr'],
        mode='last'
        )
        new_doc={'calculated_from':{}}
        if not verify_fcf_cagr_cursor:
            if start_value== 0 or end_value==0 or num_years==0:
                cagr=0
            else:
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
            
    return new_doc if 'value' in new_doc else {}
#calculate fcf and insert doc
def fcf_generate_doc(ticker,collection:Collection):
    cash_metric='NetCashProvidedByUsedInOperatingActivities'
    capex_metric='PaymentsToAcquirePropertyPlantAndEquipment'
    actual_year = datetime.now().year
    new_doc=[]
    for i in range(actual_year-5,actual_year+1):
        
        cash_doc=fetch_metric(collection,ticker,[cash_metric],mode='year',calendar_yr=str(i))
        capex_doc=fetch_metric(collection,ticker,[capex_metric],mode='year',calendar_yr=str(i))
        verify_fcf_cursor=fetch_metric(collection,ticker,['fcf'],mode='year',calendar_yr=str(i))
        if not verify_fcf_cursor:
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
# calculate short term debt
def total_short_term_debt_calc(ticker:str,collection:Collection):
    short_term_debt_metric=['ShortTermDebt']
    short_term_debt_fallback_metric=[
        'ShortTermBorrowings',
        'DebtCurrent',
        'LongTermDebtAndCapitalLeaseObligationsCurrent',
        'LongTermDebtCurrent',
        'CurrentDebtAndCapitalLeaseObligation',
        'CommercialPaper',
        'OtherShortTermBorrowings']
    actual_year = datetime.now().year
    total_short_term_debt_obj=[]
    for i in range(actual_year-5,actual_year+1):
        short_term_debt_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=short_term_debt_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False)
        if not short_term_debt_cursor:
            short_term_debt_fallback_cursor=fetch_metric(
                collection,
                ticker.upper(),
                metric=short_term_debt_fallback_metric,
                mode='year',
                calendar_yr=str(i),
                unique_metric=False
                )
            if short_term_debt_fallback_cursor:
                new_doc={'calculated_from':{}}
                short_term_debt_acc=0
                for a in short_term_debt_fallback_cursor:
                    new_doc['date']=a.get('date','')
                    new_doc['form']=a.get('form','')
                    new_doc['fp']=a.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=a.get('frame','')
                    new_doc['entity']=a.get('entity','')
                    val = a.get('value',0) or 0
                    short_term_debt_acc+=val
                    if a.get('metric') in short_term_debt_fallback_metric:
                        new_doc['calculated_from'][a.get('metric')]=val
                        new_doc['metric']='ShortTermDebt'
                        new_doc['value']=short_term_debt_acc
                if 'value' in new_doc:
                    total_short_term_debt_obj.append(new_doc)
    return total_short_term_debt_obj
def total_long_term_debt_calc(ticker,collection:Collection):
    long_term_debt_metric=['LongTermDebt']
    long_term_debt_fallback_metric=[
        'BondsPayableNoncurrent',
        'LongTermBorrowings',
        'MortgageLoansOnRealEstate',
        'DebtNoncurrent',
        'AndCapitalLeaseObligation',
        'LongTermDebtNoncurrent',
        'LongTermDebtCurrent']
    actual_year = datetime.now().year
    total_long_term_debt_obj=[]
    for i in range(actual_year-5,actual_year+1):
        long_term_debt_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=long_term_debt_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False)
        if not long_term_debt_cursor:
            long_term_debt_fallback_cursor=fetch_metric(
                collection,
                ticker.upper(),
                metric=long_term_debt_fallback_metric,
                mode='year',
                calendar_yr=str(i),
                unique_metric=False
                )
            if long_term_debt_fallback_cursor:
                new_doc={'calculated_from':{}}
                long_term_debt_acc=0
                for a in long_term_debt_fallback_cursor:
                    new_doc['date']=a.get('date','')
                    new_doc['form']=a.get('form','')
                    new_doc['fp']=a.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=a.get('frame','')
                    new_doc['entity']=a.get('entity','')
                    val = a.get('value',0) or 0
                    if a['metric']=='LongTermDebtCurrent'or \
                        a['metric']=='LongTermDebtAndCapitalLeaseObligationsCurrent':
                        val=val*-1
                    long_term_debt_acc+=val
                    if a.get('metric') in long_term_debt_fallback_metric:
                        new_doc['calculated_from'][a.get('metric')]=val
                        new_doc['metric']='LongTermDebt'
                        new_doc['value']=long_term_debt_acc
                if 'value' in new_doc:
                    total_long_term_debt_obj.append(new_doc)
    return total_long_term_debt_obj
#calculate total debt and insert doc       
def total_debt_calc(ticker,collection:Collection):
    total_debt_metrics=['LongTermDebt','ShortTermDebt','total_debt']
    total_debt_obj=[]
    actual_year = datetime.now().year
    for i in range(actual_year-5,actual_year+1):
        new_doc={'calculated_from':{}}
        total_debt_acc=0
        total_debt_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=total_debt_metrics,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False)
        if total_debt_cursor:
            for a in total_debt_cursor:
                if a['metric']=="total_debt":
                    break
                else:
                    new_doc['date']=a.get('date','')
                    new_doc['form']=a.get('form','')
                    new_doc['fp']=a.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=a.get('frame','')
                    new_doc['entity']=a.get('entity','')
                    val = a.get('value',0)
                    if val>0:
                        total_debt_acc+=val
                        new_doc['calculated_from'][a.get('metric')]=val
                    new_doc['metric']='total_debt'
                    new_doc['value']=total_debt_acc
                if 'value' in new_doc:
                    total_debt_obj.append(new_doc)
    return total_debt_obj
def market_cap_calc(ticker,collection:Collection):
    market_cap_metric=[
        'WeightedAverageNumberOfSharesOutstandingBasic',
        'market_cap']
    market_cap_obj=[]
    price_5y=[]
    actual_year = datetime.now().year
    for i in range(actual_year-5,actual_year+1):
        market_cap_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=market_cap_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False
        )
        if market_cap_cursor:
            for e in market_cap_cursor:
                if e['metric']=='market_cap':
                    break
                else:
                    prices_series=fetch_price_fmp(ticker,mode='5y')
                    if not 'close' in price_5y:
                        price_5y=pd.Series(0)
                        if datetime.fromisoformat(e.get('date','')).year in prices_series.index:
                            shares=e.get('value',0)
                            price_close=prices_series['close'][pd.to_datetime(e.get('date',0)).year]
                            result=float(shares*price_close)
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
                                    'price_close':price_close,
                                    'WeightedAverageNumberOfSharesOutstandingBasic':shares
                                }
                            }
                            if 'value' in new_doc:
                                if new_doc['value']!=0:
                                    market_cap_obj.append(new_doc)
    return market_cap_obj
def total_assets_calc(ticker,collection:Collection):
    assets_metric=['Assets']
    assets_fallback_metric=['AssetsCurrent','OtherAssetsCurrent','AssetsNonCurrent','OtherAssetsNonCurrent']
    actual_year = datetime.now().year
    total_assets_obj=[]

    for i in range(actual_year-5,actual_year+1):
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
            metric=assets_fallback_metric,
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
                    if a.get('metric') in assets_fallback_metric:
                        new_doc['calculated_from'][a.get('metric')]=val
                        new_doc['metric']='Assets'
                        new_doc['value']=assets_acc
            if 'value' in new_doc:
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
    for i in range(actual_year-5,actual_year+1):
        liabilities_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=total_liabilities_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False)
        if not liabilities_cursor:
            fallback_liabilities_cursor=fetch_metric(
                collection,
                ticker.upper(),
                metric=fallback_liabilities_metric,
                mode='year',
                calendar_yr=str(i),
                unique_metric=False
                )
            if not fallback_liabilities_cursor:
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
                    if 'value' in new_doc:
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
    for i in range(actual_year-5,actual_year+1):
        new_doc={'calculated_from':{}}
        liabilities_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=total_liabilities_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False
        )
        if not liabilities_cursor:
            fallback_liabilities_cursor=fetch_metric(
                collection,
                ticker.upper(),
                metric=fallback_liabilities_metric,
                mode='year',
                calendar_yr=str(i),
                unique_metric=False
            )
            if not fallback_liabilities_cursor:
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
                    if 'value' in new_doc:
                        total_long_term_liabilities_obj.append(new_doc)
    return(total_long_term_liabilities_obj)                       
def total_liabilities_calc(ticker:str,collection:Collection):
    total_liabilities_metric=['Liabilities']
    fallback_total_liabilities_metric=['LiabilitiesNoncurrent','LiabilitiesCurrent']
    actual_year = datetime.now().year
    total_liabilities_obj=[]
    for i in range(actual_year-5,actual_year+1):
        new_doc={'calculated_from':{}}
        total_liabilities_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=total_liabilities_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False
        )
        if not total_liabilities_cursor:

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
                if 'value' in new_doc:
                    total_liabilities_obj.append(new_doc)
    return total_liabilities_obj
def book_value_calc(ticker:str,collection:Collection):
    book_value_metrics=['Liabilities','Assets','book_value']
    actual_year = datetime.now().year
    book_value_obj=[]
    for i in range(actual_year-5,actual_year+1):
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
                if a['metric']=='book_value':
                    break
                else:
                    new_doc['date']=a.get('date','')
                    new_doc['form']=a.get('form','')
                    new_doc['fp']=a.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=a.get('frame','')
                    new_doc['entity']=a.get('entity','')
                    val = a.get('value',0) or 0
                    if a.get('metric') in book_value_metrics:
                        new_doc['calculated_from'][a.get('metric')]=val
                assets_val=new_doc['calculated_from'].get('Assets',0)
                liabilities_val=new_doc['calculated_from'].get('Liabilities',0)
                new_doc['metric']='book_value'
                new_doc['value']=assets_val-liabilities_val
                if 'value' in new_doc:
                    book_value_obj.append(new_doc)
    return book_value_obj
def pb_ratio_calc(ticker:str,collection:Collection):
    pb_ratio_metrics=['book_value','market_cap','pb_ratio']
    actual_year=datetime.now().year
    pb_ratio_obj=[]
    for i in range(actual_year-5,actual_year+1):
        new_doc={'calculated_from':{}}
        pb_ratio_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=pb_ratio_metrics,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False
        )
        if pb_ratio_cursor:
            for a in pb_ratio_cursor:
                if a['metric']=='pb_ratio':
                    break
                else:
                    new_doc['date']=a.get('date','')
                    new_doc['form']=a.get('form','')
                    new_doc['fp']=a.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=a.get('frame','')
                    new_doc['entity']=a.get('entity','')
                    val = a.get('value',0) or 0
                    if a.get('metric') in pb_ratio_metrics and val>0:
                        new_doc['calculated_from'][a.get('metric')]=val
                market_cap=new_doc['calculated_from'].get('market_cap',0)
                book_value=new_doc['calculated_from'].get('book_value',0)
                if market_cap >0 and book_value!=0:
                    new_doc['metric']='pb_ratio'
                    new_doc['value']=market_cap/book_value
                    if 'value' in new_doc:
                        pb_ratio_obj.append(new_doc)
    return pb_ratio_obj
def pe_ratio_calc(ticker:str,collection:Collection):
    pe_ratio_metrics=['EarningsPerShareDiluted']
    verify_pe_ratio_metric=['pe_ratio']
    actual_year=datetime.now().year
    price_5y=[]
    missing_years=[]
    for b in (actual_year-5,actual_year+1):    
        verify_pe_ratio_cursor=fetch_metric(
            collection,
            ticker,
            metric=verify_pe_ratio_metric,
            mode='year',
            calendar_yr=str(b),
            unique_metric=True
        )
        if not verify_pe_ratio_cursor:
            missing_years.append(b)
            price_5y= fetch_price_fmp(ticker,mode='5y')
    pe_ratio_obj=[]
    if not 'close' in price_5y:
        price_5y=pd.Series(0)
    for i in range(actual_year-5,actual_year+1):
        if i in missing_years:
            new_doc={'calculated_from':{}}
            pe_ratio_dict=fetch_metric(
                collection,
                ticker.upper(),
                metric=pe_ratio_metrics,
                mode='year',
                calendar_yr=str(i),
                unique_metric=True
            )
            if pe_ratio_dict:
                new_doc['date']=pe_ratio_dict.get('date','')
                new_doc['form']=pe_ratio_dict.get('form','')
                new_doc['fp']=pe_ratio_dict.get('fp','')
                new_doc['ticker']=ticker.upper()
                new_doc['frame']=pe_ratio_dict.get('frame','')
                new_doc['entity']=pe_ratio_dict.get('entity','')
                val = pe_ratio_dict.get('value',0) or 0
                if pe_ratio_dict.get('metric') in pe_ratio_metrics and val>0 and 'close' in price_5y:
                    price_close=float(price_5y['close'].get(i))
                    new_doc['calculated_from'][pe_ratio_dict.get('metric')]=val
                    new_doc['calculated_from']['close']=price_close

            eps_diluted=new_doc['calculated_from'].get('EarningsPerShareDiluted',0)
            pps=new_doc['calculated_from'].get('close',0)
            if eps_diluted !=0 and pps>0:
                new_doc['metric']='pe_ratio'
                new_doc['value']=pps/eps_diluted
                if 'value' in new_doc:
                    pe_ratio_obj.append(new_doc)
    return pe_ratio_obj
def debt_fcf_ratio_calc(ticker:str,collection:Collection):
    debt_fcf_ratio_metrics=['total_debt','fcf','debt_fcf_ratio']
    actual_year=datetime.now().year
    debt_fcf_ratio_obj=[]
    for i in range(actual_year-5,actual_year+1):
        new_doc={'calculated_from':{}}
        debt_fcf_ratio_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=debt_fcf_ratio_metrics,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False
        )
        if debt_fcf_ratio_cursor:
            for a in debt_fcf_ratio_cursor:
                if a['metric']=='debt_fcf_ratio':
                    break
                else:
                    new_doc['date']=a.get('date','')
                    new_doc['form']=a.get('form','')
                    new_doc['fp']=a.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=a.get('frame','')
                    new_doc['entity']=a.get('entity','')
                    val = a.get('value',0) or 0
                    if a.get('metric') in debt_fcf_ratio_metrics and val>0:
                        new_doc['calculated_from'][a.get('metric')]=val
                total_debt=new_doc['calculated_from'].get('total_debt',0)
                fcf=new_doc['calculated_from'].get('fcf',0)
                if total_debt !=0 and fcf!=0:
                    new_doc['metric']='debt_fcf_ratio'
                    new_doc['value']=total_debt/fcf
                    if 'value' in new_doc:
                        debt_fcf_ratio_obj.append(new_doc)
    return(debt_fcf_ratio_obj)
def earnings_yield_calc(ticker:str,collection:Collection):
    actual_year=datetime.now().year
    earnings_yield_metric=['EarningsPerShareDiluted']
    verify_earnings_yield_metric=['earnings_yield']
    missing_years=[]
    earnings_yield_obj=[]
    for b in range(actual_year-5,actual_year+1):
        verify_earnings_yield_cursor=fetch_metric(
            collection,
            ticker,
            metric=verify_earnings_yield_metric,
            mode='year',
            calendar_yr=str(b),
            unique_metric=True
        )
        if not verify_earnings_yield_cursor:
            missing_years.append(b),
            price_5y= fetch_price_fmp(ticker,mode='5y')
    
    if not 'close' in price_5y:
        price_5y=pd.Series(0)

    for i in range(actual_year-5,actual_year+1):
        new_doc={'calculated_from':{}}
        earnings_yield_dict=fetch_metric(
            collection,
            ticker.upper(),
            metric=earnings_yield_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=True
        )
        if earnings_yield_dict and i in missing_years:
            new_doc['date']=earnings_yield_dict.get('date','')
            new_doc['form']=earnings_yield_dict.get('form','')
            new_doc['fp']=earnings_yield_dict.get('fp','')
            new_doc['ticker']=ticker.upper()
            new_doc['frame']=earnings_yield_dict.get('frame','')
            new_doc['entity']=earnings_yield_dict.get('entity','')
            val = earnings_yield_dict.get('value',0) or 0
            if earnings_yield_dict.get('metric') in earnings_yield_metric and val>0:
                if not 'close' in price_5y:
                    pps=0
                else:    
                    pps=float(price_5y['close'].get(i,0))
                    new_doc['calculated_from'][earnings_yield_dict.get('metric')]=val
                    new_doc['calculated_from']['close']=pps
                    
                    new_doc['metric']='earnings_yield'
                    if pps!=0:
                        new_doc['value']=(val/pps)
                if 'value' in new_doc:
                    earnings_yield_obj.append(new_doc)

    return(earnings_yield_obj)
def dividends_yield_calc(ticker:str,collection:Collection):
    dividends_yield_metric=['PaymentsOfDividendsCommonStock','market_cap']
    verify_dividend_yield_metric=['dividend_yield']
    actual_year=datetime.now().year
    dividends_yield_obj=[]
    price_5y=[]
    missing_years=[]
    for b in range(actual_year-5,actual_year+1):
        verify_dividend_yield_cursor=fetch_metric(
            collection,
            ticker,
            metric=verify_dividend_yield_metric,
            mode='year',
            calendar_yr=str(b),
            unique_metric=True
        )
        if verify_dividend_yield_cursor:
            missing_years.append(b)
            price_5y= fetch_price_fmp(ticker,mode='5y')

    if not 'close' in price_5y:
        price_5y=pd.Series(0)    
    for i in range(actual_year-5,actual_year+1):
        new_doc={'calculated_from':{}}
        dividends_yield_cursor=fetch_metric(
            collection,
            ticker.upper(),
            metric=dividends_yield_metric,
            mode='year',
            calendar_yr=str(i),
            unique_metric=False
        )
        if dividends_yield_cursor:
            for a in dividends_yield_cursor and i in missing_years:
                new_doc['date']=a.get('date','')
                new_doc['form']=a.get('form','')
                new_doc['fp']=a.get('fp','')
                new_doc['ticker']=ticker.upper()
                new_doc['frame']=a.get('frame','')
                new_doc['entity']=a.get('entity','')
                val = a.get('value',0) or 0
                if a.get('metric') in dividends_yield_metric and val>0:
                    new_doc['calculated_from'][a.get('metric')]=val
            market_cap=new_doc['calculated_from'].get('market_cap',0)
            dividends=new_doc['calculated_from'].get('PaymentsOfDividendsCommonStock',0)
            if market_cap >0 and dividends!=0:
                new_doc['metric']='dividend_yield'
                new_doc['value']=dividends/market_cap
                if 'value' in new_doc:
                    dividends_yield_obj.append(new_doc)
    return(dividends_yield_obj)
if __name__=='__main__':
# write the raw edgar db

    db = client['test']
    edgar_collection = db['rawEdgarCollection']
    cik_collection=db['tickerCIK']
    #line for testing functions
    # tickers=['abt','air']
# define metrics
    fcf_metric=['fcf']
    fcf_cagr_metric=['fcf_cagr']
    dividends_metric=['PaymentsOfDividends','PaymentsOfDividendsCommonStock']
    stock_holders_equity_metric=['StockholdersEquity','StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest']
    basic_eps_metric=['EarningsPerShareBasic']
    diluted_eps_metric=['EarningsPerShareDiluted']
    short_term_debt_metric=['ShortTermBorrowings','ShortTermDebt','CurrentPortionOfLongTermDebt','CurrentDebtAndCapitalLeaseObligation','DebtCurrent']
    long_term_debt_metric=['LongTermDebtNoncurrent','LongTermBorrowings','LongTermDebt','DebtNoncurrent','LongTermDebtAndCapitalLeaseObligation']
# # # fetch companyfacts and create the rawEdgarCollection
    # object,tickers= fetch_yearly_data()
    # index_params=[{
    #     "fields":[("ticker",1),("metric",1),("date",1),("value",1)],
    #     "unique":True
    # }]
    # push_StockData(
    #     db,
    #     object,
    #     collection='rawEdgarCollection',
    #     ordered_mode=False,
    #     index_list=index_params
    #     )
    tickers = fetch_tickers(cik_collection)
    # tickers=['MOV']
    for ticker in tickers:
# # calculate short term debt
#         short_term_debt_obj=total_short_term_debt_calc(ticker,edgar_collection)
#         if short_term_debt_obj:
#             print('writing short term_debt',ticker)
#             write_object(edgar_collection,short_term_debt_obj,mode='many')
# # calculate long term debt
#         long_term_debt_obj=total_long_term_debt_calc(ticker,edgar_collection)
#         if long_term_debt_obj:
#             print('writing long_term_debt',ticker)
#             write_object(edgar_collection,long_term_debt_obj,mode='many')
# # calculate total debt and write it on rawEdgarCollection
#         total_debt_object=total_debt_calc(ticker,edgar_collection)
#         if total_debt_object:
#             print('writing total_debt_obj',ticker)
#             write_object(edgar_collection,total_debt_object,mode='many')
# # calculate free cash flow
#         fcf_object= fcf_generate_doc(ticker,edgar_collection)
#         if fcf_object:
#             print('writing fcf',ticker)
#             write_object(edgar_collection,fcf_object,mode='many')
# # extract first and last fcf to calculate cagr
#         first_fcf=fetch_metric(edgar_collection,ticker,metric=fcf_metric,mode='first')
#         last_fcf=fetch_metric(edgar_collection,ticker,metric=fcf_metric,mode='last')
#         if first_fcf and last_fcf:
            
#             cagr_obj=calculate_historical_growth_rate(first_fcf,last_fcf,edgar_collection)
#         else:
#             cagr_obj={}
#         if cagr_obj:
#             print('writing fcf_cagr',ticker)
#             write_object(edgar_collection,cagr_obj)
# # get price and shares for last 5y and calculate market cap
#         market_cap_obj=market_cap_calc(ticker,edgar_collection)
#         if market_cap_obj:
#             print('writing markeT_cap',ticker)
#             write_object(edgar_collection,market_cap_obj,mode='many')

# # calculate total assets
#         total_assets_obj=total_assets_calc(ticker,edgar_collection)
#         if total_assets_obj:
#             print('writing assets',ticker)
#             write_object(edgar_collection,total_assets_obj,mode='many')


# # calculate total current liabilities
#         current_liabilities_obj=current_liabilities_calc(ticker,edgar_collection)
#         if current_liabilities_obj:
#             print('writing current_liab',ticker)
#             write_object(edgar_collection,current_liabilities_obj,mode='many')
        
# # calculate long term liabilities
#         long_term_liabilities_obj=long_term_liabilities_calc(ticker,edgar_collection)
#         if long_term_liabilities_obj:
#             print('writing long_term_liab',ticker)
#             write_object(edgar_collection,long_term_liabilities_obj,mode='many')
# # calculate total liabilities
#         total_liabilities_obj=total_liabilities_calc(ticker,edgar_collection)
#         if total_liabilities_obj:
#             print('writing liab',ticker)
#             write_object(edgar_collection,total_liabilities_obj,mode='many')
# # calculate book value
#         book_value_obj=book_value_calc(ticker,edgar_collection)
#         if book_value_obj:
#             print('writing book_v',ticker)
#             write_object(edgar_collection,book_value_obj,mode='many')
            
# # calculate pb_ratio
#         pb_ratio_obj=pb_ratio_calc(ticker,edgar_collection)
#         if pb_ratio_obj:
#             print('writing pb_ratio',ticker)
#             write_object(edgar_collection,pb_ratio_obj,mode='many')
# # calculate pe_ratio
#         pe_ratio_obj=pe_ratio_calc(ticker,edgar_collection)
#         if pe_ratio_obj:
#             print('writing pe_ratio',ticker)
#             write_object(edgar_collection,pe_ratio_obj,mode='many')
# # calculate debt to fcf ratio
#             debt_fcf_ratio_obj=debt_fcf_ratio_calc(ticker,edgar_collection)
#             if debt_fcf_ratio_obj:
#                 print('writing debt_fcf_ratio',ticker)
#                 write_object(edgar_collection,debt_fcf_ratio_obj,mode='many')
# # calculate earnings yield to pps ratio
#             earning_yield_obj=earnings_yield_calc(ticker,edgar_collection)
#             if earning_yield_obj:
#                 print('writing earnings_yeild',ticker)
#                 write_object(edgar_collection,earning_yield_obj,mode='many')
# # calculate dividend yields
#             dividends_yield_obj=dividends_yield_calc(ticker,edgar_collection)
#             if dividends_yield_obj:
#                 print('writing dividends_yield',ticker)
#                 write_object(edgar_collection,dividends_yield_obj,mode='many')

# get stock price
            price_obj=fetch_price_fmp(edgar_collection,ticker,mode='5y')
            print(price_obj)
