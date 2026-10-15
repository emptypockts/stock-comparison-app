from dotenv import load_dotenv

load_dotenv()

import yfinance as yf
from eacsa_logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def alpha_get_market_cap(symbol: str) -> int:
    """
    Fetches the current market capitalization for a given ticker symbol.

    Args:
        symbol (str): The stock ticker symbol (e.g. "AAPL").

    Returns:
        int: Market cap in USD, or 0 if unavailable or on error.
    """
    try:
        ticker = yf.Ticker(symbol)
        market_cap = ticker.info.get("marketCap")
        if market_cap:
            return int(market_cap)
        logger.warning(f"marketCap not available for {symbol} via yfinance.")
        return 0
    except Exception as e:
        logger.error(f"Error fetching market cap for {symbol}: {e}")
        return 0


def get_StockInfo(ticker: str) -> dict | None:
    """
    Fetches general stock information for a given ticker.

    Retrieves symbol, company name, shares outstanding, market cap,
    current price and industry description via yfinance.

    Args:
        ticker (str): The stock ticker symbol (e.g. "AAPL").

    Returns:
        dict | None: A dict with the following keys on success:
            - symbol (str): Ticker symbol.
            - name (str): Company long name.
            - share_class_shares_outstanding (int): Shares outstanding.
            - market_cap (int): Market capitalization in USD.
            - current_price (float): Latest market price.
            - sic_description (str): Industry description.
        Returns None on failure.
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info or "symbol" not in info:
            raise ValueError(f"No data returned for ticker: {ticker}")

        market_cap = int(info.get("marketCap") or 0)
        shares_outstanding = int(info.get("sharesOutstanding") or 1)
        current_price = round(
            info.get("currentPrice") or info.get("regularMarketPrice") or 0, 2
        )

        return {
            "symbol": info.get("symbol", ticker.upper()),
            "name": info.get("longName", "name not available"),
            "share_class_shares_outstanding": shares_outstanding,
            "market_cap": market_cap,
            "current_price": current_price,
            "sic_description": info.get("industry", ""),
        }
    except (KeyError, ValueError) as e:
        logger.error(f"Data parsing error for {ticker}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_StockInfo for {ticker}: {e}")
        return None


def get_qtr_earnings(ticker: str) -> list | None:
    """
    Fetches the last 10 quarterly revenue figures for a given ticker.

    Pulls quarterly income statement data via yfinance and normalises
    each entry into a consistent dict structure.

    Args:
        ticker (str): The stock ticker symbol (e.g. "AAPL").

    Returns:
        list | None: A list of up to 10 dicts, each containing:
            - ticker (str): Ticker symbol in uppercase.
            - filing_date (str): Quarter end date in YYYY-MM-DD format.
            - revenues_value_M (str): Revenue formatted as "$X.XX M".
        Returns None if no data is found or on error.
    """
    try:
        t = yf.Ticker(ticker)
        financials = t.quarterly_income_stmt

        if financials is None or financials.empty:
            raise ValueError(
                f"No quarterly financials found for ticker: {ticker}"
            )

        stock_obj = []
        revenue_row = None
        for label in ["Total Revenue", "Revenue"]:
            if label in financials.index:
                revenue_row = financials.loc[label]
                break

        if revenue_row is None:
            raise ValueError(
                f"No revenue row found in financials for: {ticker}"
            )

        for date, value in revenue_row.items():
            if value is None:
                continue
            stock_obj.append(
                {
                    "ticker": ticker.upper(),
                    "filing_date": str(date.date()),
                    "revenues_value_M": f"${round(float(value) / 1_000_000, 2)} M",
                }
            )
            if len(stock_obj) == 10:
                break

        return stock_obj if stock_obj else None

    except (KeyError, ValueError) as e:
        logger.error(f"Data parsing error for {ticker}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_qtr_earnings for {ticker}: {e}")
        return None


def compile_stockData(tickers: list[str]) -> dict:
    """
    Compiles general stock info and quarterly earnings for a list of tickers.

    Iterates over each ticker, fetching both general stock data and quarterly
    earnings. Tickers with incomplete data are skipped with a warning.

    Args:
        tickers (list[str]): List of stock ticker symbols to process.

    Returns:
        dict: A dict keyed by ticker symbol, each value containing:
            - gStockData (dict): Output of get_StockInfo().
            - qtrStockData (list): Output of get_qtr_earnings().
            - last_filing_date (str | None): Most recent quarterly filing date.
        Returns an empty dict if input is invalid or all tickers fail.
    """
    if not isinstance(tickers, list):
        logger.error("Input `tickers` must be a list.")
        return {}

    stockInfo = {}

    for ticker in tickers:
        try:
            gStockData = None
            qtrStockData = None

            try:
                gStockData = get_StockInfo(ticker)
            except Exception as e:
                logger.error(
                    f"Error fetching general stock data for {ticker}: {e}"
                )

            try:
                qtrStockData = get_qtr_earnings(ticker)
            except Exception as e:
                logger.error(
                    f"Error fetching quarterly earnings for {ticker}: {e}"
                )

            if not gStockData or not qtrStockData:
                logger.warning(f"Skipping {ticker} due to incomplete data.")
                continue

            stockInfo[ticker] = {
                "gStockData": gStockData,
                "qtrStockData": qtrStockData,
            }

            try:
                stockInfo[ticker]["last_filing_date"] = (
                    qtrStockData[0]["filing_date"]
                    if qtrStockData and "filing_date" in qtrStockData[0]
                    else None
                )
            except Exception as e:
                logger.error(
                    f"Error processing last filing date for {ticker}: {e}"
                )
                stockInfo[ticker]["last_filing_date"] = None

        except Exception as e:
            logger.error(f"Unexpected error processing {ticker}: {e}")

    return stockInfo


if __name__ == "__main__":
    tickers = ["ko"]
    stockInfo = compile_stockData(tickers)
    print(stockInfo)
