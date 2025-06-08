import logging
import dotenv
import os
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def alpha_get_market_cap(symbol):
    api_key  = os.getenv('ALPHA_VANTAGE_API_KEY')
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    if 'MarketCapitalization' in data:
        return int(data['MarketCapitalization'])
    else:
        return int(0)


def get_StockInfo(ticker):
    try:
        dotenv.load_dotenv()
        API = os.getenv('POLYGON_API')
        if not API:
            raise EnvironmentError("POLYGON_API key not found in environment variables.")
        
        stockData = {}
        url = f"https://api.polygon.io/v3/reference/tickers/{ticker.upper()}?apiKey={API}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        market_cap= alpha_get_market_cap(ticker)
        jsonObj = response.json()
        if market_cap==0:
            market_cap=jsonObj['results']['market_cap'],
            if isinstance(market_cap,tuple):
                market_cap=market_cap[0]
        if 'results' not in jsonObj or not jsonObj['results']:
            raise ValueError(f"No results found for ticker: {ticker}")
        stockData = {
            'symbol': jsonObj['results']['ticker'],
            'name': jsonObj['results']['name'],
            'share_class_shares_outstanding': jsonObj['results']['weighted_shares_outstanding'],
            'market_cap': market_cap,
            'current_price': round(market_cap / jsonObj['results']['weighted_shares_outstanding'],2)
        }
        return stockData

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while fetching stock info for {ticker}: {e}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Data parsing error for {ticker}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_StockInfo for {ticker}: {e}")
        return None


def get_qtr_earnings(ticker):
    try:
        dotenv.load_dotenv()
        API = os.getenv('POLYGON_API')
        if not API:
            raise EnvironmentError("POLYGON_API key not found in environment variables.")
        
        stock_obj = []
        url = f"https://api.polygon.io/vX/reference/financials?ticker={ticker.upper()}&&timeframe=quarterly&limit=10&sort=filing_date&apiKey={API}"
        response = requests.get(url)
        response.raise_for_status()
        
        jsonObj = response.json()

        if 'results' not in jsonObj or not jsonObj['results']:
            raise ValueError(f"No quarterly earnings found for ticker: {ticker}")
        
        for result in jsonObj['results']:
            stock_obj.append({
                'ticker': result['tickers'][0],
                'filing_date': result['filing_date'],
                'revenues_value_M': f"${round(result['financials']['income_statement']['revenues']['value'], 0) / 1_000_000} M"
            })
        return stock_obj

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while fetching quarterly earnings for {ticker}: {e}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Data parsing error for {ticker}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_qtr_earnings for {ticker}: {e}")
        return None


def compile_stockData(tickers):
    if not isinstance(tickers, list):
        logger.error("Input `tickers` must be a list.")
        return {}

    stockInfo = {}
    
    for ticker in tickers:
        try:
            gStockData = None
            qtrStockData = None

            # Safely attempt to fetch stock data
            try:
                gStockData = get_StockInfo(ticker)
            except Exception as e:
                logger.error(f"Error fetching general stock data for {ticker}: {e}")
            
            # Safely attempt to fetch quarterly earnings
            try:
                qtrStockData = get_qtr_earnings(ticker)
            except Exception as e:
                logger.error(f"Error fetching quarterly earnings for {ticker}: {e}")
            
            # Skip ticker if data is incomplete
            if not gStockData or not qtrStockData:
                logger.warning(f"Skipping {ticker} due to incomplete data.")
                continue

            stockInfo[ticker] = {
                "gStockData": gStockData,
                "qtrStockData": qtrStockData,
            }

            # Safely extract the last filing date
            try:
                stockInfo[ticker]['last_filing_date'] = (
                    qtrStockData[0]['filing_date'] if qtrStockData and 'filing_date' in qtrStockData[0] else None
                )
            except Exception as e:
                logger.error(f"Error processing last filing date for {ticker}: {e}")
                stockInfo[ticker]['last_filing_date'] = None
        
        except Exception as e:
            logger.error(f"Unexpected error processing {ticker}: {e}")
    
    return stockInfo




# Example function call
if __name__ == "__main__":
    tickers= ['intc']
    stockInfo = compile_stockData(tickers)
    
    print(stockInfo)