import yfinance as yf
import pandas as pd
def fetch_stock_price_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="5y")
    return ({str(date): round(price,2)for date, price in data['Close'].items()})

if __name__ == "__main__":

    price = []
    
    tickers = ['rost','intc']  # Example ticker
    for ticker in tickers:
        try:
            data,current_price= fetch_stock_price_data(ticker)
            price.append(data)
            
        except:
            print(f"Cannot fetch stock {ticker}.")
            price.append(None)

    stock_prices = pd.DataFrame({
    'symbol' : tickers,
    'price' : price,
    })

    print(stock_prices)