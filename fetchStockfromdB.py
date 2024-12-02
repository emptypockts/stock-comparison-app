from pymongo import MongoClient,DESCENDING
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
        '$sort':{'Growth':-1}
        },{
        '$limit': 5000
        },{
        '$skip': (page-1)*items_per_page
    }
    ])

  
        
    # Group the fetched records by symbol
    grouped_stocks = {}
    for stock in stocks:
        stock['_id'] = str(stock['_id'])  # Convert ObjectId to string
                # Apply formatting to each relevant field
        stock['Basic Average Shares'] = format_number(stock.get('Basic Average Shares'))
        stock['Tangible Book Value'] = format_currency(stock.get('Tangible Book Value'))
        stock['Free Cash Flow'] = format_currency(stock.get('Free Cash Flow'))
        stock['Basic EPS'] = format_currency(stock.get('Basic EPS'))
        stock['Diluted EPS'] = format_currency(stock.get('Diluted EPS'))
        stock['Total Debt'] = format_currency(stock.get('Total Debt'))
        stock['Dividends'] = format_currency(stock.get('Dividends'))
        stock['Price Per Share'] = format_currency(stock.get('Price Per Share'))
        stock['Tangible Book Value Per Share'] = format_currency(stock.get('Tangible Book Value Per Share'))
        stock['p/b ratio'] = format_ratio(stock.get('p/b ratio'))
        stock['p/e ratio'] = format_ratio(stock.get('p/e ratio'))
        stock['Debt FCF ratio'] = format_ratio(stock.get('Debt FCF ratio'))
        stock['Dividends Yield'] = format_percentage(stock.get('Dividends Yield'))
        stock['Earnings Yield'] = format_percentage(stock.get('Earnings Yield'))
        stock['Market Cap'] = format_currency(stock.get('Market Cap'))
        stock['Growth']=format_percentage_growth(stock.get('Growth'))
        symbol = stock['Symbol']
        if symbol not in grouped_stocks:
            grouped_stocks[symbol] = []
        grouped_stocks[symbol].append(stock)
    
    total_symbols = stock_collection.distinct("Symbol")
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

    grouped_stocks, total_symbols_count = stockFetch(page=9, items_per_page=100)
    print("Grouped Stocks:", grouped_stocks)
    print("Total Symbols Count:", total_symbols_count)