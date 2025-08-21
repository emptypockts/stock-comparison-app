from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
# Formatting functions
def format_currency(value):
    return "${:,.2f}".format(value) if value is not None else "N/A"

def format_number(value):
    return "{:,.0f}".format(value) if value is not None else "N/A"

def format_ratio(value):
    return "{:.2f}".format(value) if value is not None else "N/A"

def format_percentage(value):
    return "{:.2f}%".format(value * 100) if value is not None else "N/A"

def format_percentage_growth(value):
    return "{:.2f}%".format(value) if value is not None else "N/A"

def stockFetch(db,page=1, items_per_page=100):
    print("Page query ",page)
    print("Page size ",items_per_page)

    stock_collection = db["StockScore"]
  
    # Fetch records with pagination
    stocks = stock_collection.aggregate([
        {
        '$sort':{'fcf_cagr':-1}
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
        stock['Basic Average Shares'] = stock.get('EarningsPerShareBasic')
        stock['Tangible Book Value'] = stock.get('book_value')
        stock['Free Cash Flow'] = stock.get('fcf')
        stock['Basic EPS'] = stock.get('EarningsPerShareBasic')
        stock['Diluted EPS'] = stock.get('EarningsPerShareDiluted')
        stock['Total Debt'] = stock.get('total_debt')
        stock['Dividends'] = stock.get('PaymentsOfDividendsCommonStock')
        stock['Price Per Share'] = stock.get('price_close')
        stock['p/b ratio'] = stock.get('pb_ratio')
        stock['p/e ratio'] = stock.get('pe_ratio')
        stock['Debt FCF ratio'] = stock.get('debt_fcf_ratio')
        stock['Dividends Yield'] = stock.get('dividend_yield')
        stock['Earnings Yield'] = stock.get('earnings_yield')
        stock['Market Cap'] = stock.get('market_cap')
        stock['Growth']=stock.get('fcf_cagr')
        symbol = stock['ticker']
        if symbol not in grouped_stocks:
            grouped_stocks[symbol] = []
        grouped_stocks[symbol].append(stock)
    
    total_symbols = stock_collection.distinct("ticker")
    total_symbols_count = len(total_symbols)
    return grouped_stocks,total_symbols_count

def stockInsert(db,jsonData):
    stock_collection = db["StockScore"]
    #inkect the object in the database
    stock_collection.insert_many(jsonData)
    print("jsonData inserted successfully")

if __name__ == "__main__":
    load_dotenv()
    uri = os.getenv('MONGODB_URI')
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["test"]

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")

    except Exception as e:
        print("Error trying to connect to the DB")

    grouped_stocks, total_symbols_count = stockFetch(db,page=9, items_per_page=100)
    print("Grouped Stocks:", grouped_stocks)
    print("Total Symbols Count:", total_symbols_count)