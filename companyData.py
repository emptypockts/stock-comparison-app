import logging
import dotenv
import os
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

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
        
        jsonObj = response.json()
        if 'results' not in jsonObj or not jsonObj['results']:
            raise ValueError(f"No results found for ticker: {ticker}")
        
        stockData = {
            'symbol': jsonObj['results']['ticker'],
            'name': jsonObj['results']['name'],
            'share_class_shares_outstanding': jsonObj['results']['share_class_shares_outstanding'],
            'market_cap': jsonObj['results']['market_cap'],
            'current_price': round(jsonObj['results']['market_cap'] / jsonObj['results']['share_class_shares_outstanding'],2)
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
    try:
        stockInfo = {}
        for ticker in tickers:
            gStockData = get_StockInfo(ticker)
            qtrStockData = get_qtr_earnings(ticker)
            
            if not gStockData or not qtrStockData:
                logger.warning(f"Skipping incomplete data for {ticker}")
                continue
            
            stockInfo[ticker] = {
                "gStockData": gStockData,
                "qtrStockData": qtrStockData
            }

            # Safely access the first quarterly data
            if qtrStockData and 'filing_date' in qtrStockData[0]:
                stockInfo[ticker]['last_filing_date'] = qtrStockData[0]['filing_date']
            else:
                stockInfo[ticker]['last_filing_date'] = None
        
        return stockInfo

    except Exception as e:
        logger.error(f"Unexpected error in compile_stockData: {e}")
        return None



# Example function call
if __name__ == "__main__":
    tickers= ['msft','cnc']
    stockInfo = compile_stockData(tickers)
    
    print(stockInfo)