from datetime import datetime
import os
import pandas as pd
from CIKTickerUpdate import fetch_cik,fetch_ticker
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from pymongo import MongoClient,UpdateOne
from qtrStockDbOps import push_StockData
from companyData import fetch_metric
import json
load_dotenv()

uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
KY = os.getenv('TWELVE_API_KY')
URL_BASE = os.getenv('TWELVE_URI')

def fetch_yearly_data():
    db = client['test']
    path = r"C:\\Users\\ejujo\\Downloads\\companyfacts\\"
    files = os.listdir(path)
    yrly_obj = []
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
    'PaymentsOfDividendsCommonStock':'dividends',
    'EntityCommonStockSharesOutstanding':'OutstandingShares', #outstandingshares,
    'StockholdersEquity':'StockholdersEquity',
    'WeightedAverageNumberOfSharesOutstandingBasic':'OutstandingShares',
    'EarningsPerShareBasic':'EPS',
    'EarningsPerShareDiluted':'EPS_diluted',
    'CommercialPaper':'CommercialPaper',
    'OtherLiabilitiesCurrent':'OtherLiabilitiesCurrent', 
    'OtherLiabilitiesNoncurrent':'OtherLiabilitiesNoncurrent',
    'LiabilitiesCurrent':'LiabilitiesCurrent', 
    'LiabilitiesNoncurrent':'LiabilitiesNoncurrent',#Total Debt =CurrentPortionOfLongTermDebt+ LongTermDebtNoncurrent(+ FinanceLeaseObligations, optional)
    'PaymentsToAcquirePropertyPlantAndEquipment':'capex',
    'NetCashProvidedByUsedInInvestingActivities':'capex2',
    'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest':'StockholdersEquity',
    'CurrentPortionOfLongTermDebt':'ShortTermDebt',
    'ShortTermBorrowings':'ShortTermDebt',
    'ShortTermDebt':'ShortTermDebt',
    'DebtCurrent':'ShortTermDebt',
    'LongTermDebtAndCapitalLeaseObligationsCurrent':'ShortTermDebt',
    'CurrentDebtAndCapitalLeaseObligation':'ShortTermDebt',
    'CommercialPaper':'ShortTermDebt',
    'OtherShortTermBorrowings':'ShortTermDebt',
    'BondsPayableNoncurrent':'LongTermDebt',
    'LongTermBorrowings':'LongTermDebt',
    'MortgageLoansOnRealEstate':'LongTermDebt',
    'LongTermDebtNoncurrent':'LongTermDebt',
    'DebtNoncurrent':'LongTermDebt',
    'LongTermDebtAndCapitalLeaseObligation':'LongTermDebt',
    'LongTermDebt':'LongTermDebt'
    }
    # for file in files:
        # use to debug
    for file in files[:3:]: 
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
                            if 'USD' in item['facts']['us-gaap'][metric_name]['units'] or 'USD/shares' in item['facts']['us-gaap'][metric_name]['units'] or 'shares' in item['facts']['us-gaap'][metric_name]['units']:
                                if metric_name=='EarningsPerShareBasic' or metric_name=='EarningsPerShareDiluted':
                                    metrics = item['facts']['us-gaap'][metric_name]['units']['USD/shares']
                                elif metric_name=='WeightedAverageNumberOfSharesOutstandingBasic':
                                    metrics = item['facts']['us-gaap'][metric_name]['units']['shares']
                                else:
                                    metrics = item['facts']['us-gaap'][metric_name]['units']['USD']
                                for metric in metrics:
                                    # Process only 10-K forms with a frame
                                    endDate=datetime.strptime(metric['end'],'%Y-%m-%d')
                                    if metric['form'] == '10-K' and (endDate.year>2020) and 'frame' in metric:
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


def calculate_historical_growth_rate(first,last):
    db = client['test']
    collection = db['StockScore']
    if 'value' not in first and 'value' not in last:
        raise Exception('not enough data to calculate growth. use 5% instead')
    num_years = int(last.get('frame').replace('CY',''))-int(first.get('frame').replace('CY',''))    
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
    if new_doc:
        collection.insert_one(new_doc)

def fcf_generate_doc(tickers):
    db = client['test']
    collection = db['StockScore']
    cash_metric='NetCashProvidedByUsedInOperatingActivities'
    capex_metric='PaymentsToAcquirePropertyPlantAndEquipment'
    actual_year = datetime.now().year
    
    for i in range(actual_year-4,actual_year):
        frame =f"CY{i}"
        for ticker in tickers:
            cash_doc=fetch_metric(collection,ticker,[cash_metric],mode='year',frame=f"CY{i}")
            capex_doc=fetch_metric(collection,ticker,[capex_metric],mode='year',frame=f"CY{i}")
            cash = cash_doc.get('value',0) if cash_doc else 0
            raw_capex = capex_doc.get('value',0) if capex_doc else 0
            total_capex=abs(raw_capex)
            fcf = cash-total_capex
            if cash>0:
                new_doc={
                    "ticker":ticker.upper(),
                    "entity":cash_doc.get('entity','unknown'),
                    "metric":"fcf",
                    "value":fcf,
                    "frame":frame,
                    "calculated_from":{
                        "cash_value":cash,
                        "capex_value":total_capex
                    },
                    "date":cash_doc.get('date',''),
                    "form":cash_doc.get('form',''),
                    "fp":cash_doc.get('fp','')
                }
                    
                collection.insert_one(new_doc)
                


def total_debt_calc(tickers):
    db = client['test']
    collection = db['StockScore']
    short_term_debt_metric=['ShortTermDebt','ShortTermBorrowings','DebtCurrent','LongTermDebtAndCapitalLeaseObligationsCurrent','CurrentDebtAndCapitalLeaseObligation','CommercialPaper','OtherShortTermBorrowings']
    long_term_debt_metric=['LongTermDebt','BondsPayableNoncurrent','LongTermBorrowings','MortgageLoansOnRealEstate','Noncurrent','DebtNoncurrent','AndCapitalLeaseObligation','LongTermDebtNoncurrent']
    actual_year = datetime.now().year
    for ticker in tickers:
        for i in range(actual_year-4,actual_year):
            frame =f"CY{i}"
            new_doc={'calculated_from':{}}

            short_term_debt = fetch_metric(collection,ticker.upper(),metric=short_term_debt_metric,mode='year',frame=frame,unique_metric=False)
            short_acc_debt=0
            long_acc_debt=0
            for e in short_term_debt:
                
                if  e['metric']=='ShortTermDebt':
                    short_term_debt_value=e.get('value',0)
                    new_doc['calculated_from']['short_term_debt']=short_term_debt_value
                    new_doc['date']=e.get('date','')
                    new_doc['form']=e.get('form','')
                    new_doc['fp']=e.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=e.get('frame','')
                    new_doc['entity']=e.get('entity','')
                    break
                else :
                    short_acc_debt=short_acc_debt+e.get('value')
                    new_doc['calculated_from']['short_term_debt']=short_acc_debt
                    new_doc['value']=short_acc_debt
                    new_doc['date']=e.get('date','')
                    new_doc['form']=e.get('form','')
                    new_doc['fp']=e.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=e.get('frame','')
                    new_doc['entity']=e.get('entity','')
                    
                    
                    
            long_term_debt =fetch_metric(collection,ticker.upper(),metric=long_term_debt_metric,mode='year',frame=frame,unique_metric=False)
            for e in long_term_debt:
                if e['metric']=='LongTermDebt':
                    long_term_debt_value=e.get('value',0)
                    new_doc['calculated_from']['long_term_debt']=long_term_debt_value
                    new_doc['date']=e.get('date','')
                    new_doc['form']=e.get('form','')
                    new_doc['fp']=e.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=e.get('frame','')
                    new_doc['entity']=e.get('entity','')
                    break
                else:
                    long_acc_debt=long_acc_debt+e.get('value')
                    new_doc['calculated_from']['long_term_debt']=long_acc_debt
                    new_doc['date']=e.get('date','')
                    new_doc['form']=e.get('form','')
                    new_doc['fp']=e.get('fp','')
                    new_doc['ticker']=ticker.upper()
                    new_doc['frame']=e.get('frame','')
                    new_doc['entity']=e.get('entity','')
            
            new_doc['metric']='total_debt'
            if 'short_term_debt' in new_doc['calculated_from']:
                if 'long_term_debt' in new_doc['calculated_from']:
                    new_doc['value']=new_doc['calculated_from'].get('short_term_debt',0)+new_doc['calculated_from'].get('long_term_debt',0)
                else:
                    new_doc['value']=new_doc['calculated_from'].get('short_term_debt',0)
            if 'long_term_debt' in new_doc['calculated_from']:
                new_doc['value']=new_doc['calculated_from'].get('long_term_debt',0)
            
            if 'value' in new_doc:
                collection.insert_one(new_doc)
                
                
            

if __name__=='__main__':
    db = client['test']
    collection = db['StockScore']
    tickers=['abt','air']
    outstanding_shares_metric=['WeightedAverageNumberOfSharesOutstandingBasic']
    fcf_metric=['fcf']
    fcf_cagr_metric=['fcf_cagr']
    dividends_metric=['PaymentsOfDividends','PaymentsOfDividendsCommonStock']
    stock_holders_equity_metric=['StockholdersEquity','StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest']
    basic_eps_metric=['EarningsPerShareBasic']
    diluted_eps_metric=['EarningsPerShareDiluted']
    short_term_debt_metric=['ShortTermBorrowings','ShortTermDebt','CurrentPortionOfLongTermDebt','CurrentDebtAndCapitalLeaseObligation','DebtCurrent']
    long_term_debt_metric=['LongTermDebtNoncurrent','LongTermBorrowings','LongTermDebt','DebtNoncurrent','LongTermDebtAndCapitalLeaseObligation']
    object= fetch_yearly_data()
    push_StockData(db,object,collection='StockScore')
    fcf_generate_doc(tickers)
    total_debt_calc(tickers)

    for ticker in tickers:
        first_fcf=fetch_metric(collection,ticker,metric=fcf_metric,mode='first')
        last_fcf=fetch_metric(collection,ticker,metric=fcf_metric,mode='last')
        calculate_historical_growth_rate(first_fcf,last_fcf)
        all_avg_shares=fetch_metric(collection,ticker.upper(),metric=outstanding_shares_metric,mode='all')
        dividends= fetch_metric(collection,ticker.upper(),metric=dividends_metric,mode='all')
        stock_holders_equity=fetch_metric(collection,ticker.upper(),metric=stock_holders_equity_metric,mode='all')
        basic_eps=fetch_metric(collection,ticker.upper(),metric=basic_eps_metric,mode='all')
        diluted_eps=fetch_metric(collection,ticker.upper(),metric=diluted_eps_metric,mode='all')
        short_term_debt = fetch_metric(collection,ticker.upper(),metric=short_term_debt_metric,mode='all')
        long_term_debt =fetch_metric(collection,ticker.upper(),metric=long_term_debt_metric,mode='all')
        
    