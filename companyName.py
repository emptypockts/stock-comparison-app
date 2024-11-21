import yfinance as yf
import pandas as pd
import logging
import dotenv
import os
import requests
dotenv.load_dotenv()

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_company_name(ticker):
    stock = yf.Ticker(ticker)
    try:
        earnings_data = stock.earnings_dates
        current_date = pd.Timestamp.now().tz_localize('UTC')
        future_earnings = earnings_data[earnings_data.index > current_date]
        future_earnings=future_earnings.iloc[-1].name.strftime('%Y-%m-%d %H:%M:%S %Z')
    except:
        logging.info(f"earnings date not available for :{ticker}")
        future_earnings=0
    
    try:
        current_price = round(stock.fast_info.last_price,2)
        return (stock.info.get('longName', 'Unknown'),current_price,future_earnings)
    except:
        logging.info(f"stock price not available:{ticker}")
        return ("NA",0)
# def alpha_get_company_name(ticker):
#     matchScore = '0'
#     ALPHA_VANTAGE_API_KEY=os.getenv('ALPHA_VANTAGE_API_KEY')
#     url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
#     response = requests.get(url)
#     data= response.json()
#     StockObj = data['bestMatches']
#     for item in StockObj:
#        if item['8. currency']=='USD':
#         if matchScore<item['9. matchScore']:
#             name = item['2. name']
#             matchScore= item['9. matchScore']

#     return {name}

# Example function call
if __name__ == "__main__":

    # names = []
    # tickers = ['amzn','intc']  # Example ticker
    # for ticker in tickers:
    #     try:
    #         data= get_company_name(ticker)
    #         names.append(data)
    #     except:
    #         print(f"Cannot fetch stock {ticker}.")
    #         names.append(None)

    # company_names_df = pd.DataFrame({
    #     'symbol' : tickers,
    #     'name' : names

    # })
    # print(company_names_df)

    names=[]
    tickers = ['rost','intc']
    for ticker in tickers:
        print(get_company_name(ticker))

    