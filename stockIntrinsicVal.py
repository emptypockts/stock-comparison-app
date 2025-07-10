import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
import os
import requests
from io import StringIO
import logging
import locale
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
KEY = os.getenv('CURRENCY_API')
url='https://api.exchangeratesapi.io/v1/latest'
query_string = {
    "access_key":KEY
}
def calculate_historical_growth_rate(ticker):
    """Calculate the Compound Annual Growth Rate (CAGR) of Free Cash Flow."""
    stock=yf.Ticker(ticker)
    fcf = stock.cashflow.loc['Free Cash Flow']
    if fcf.empty:
        raise ValueError("FCF empty")
    if len(fcf) < 2:
        raise ValueError("Not enough data to calculate growth rate.")
    
    fcf = fcf.dropna()  # Remove any NaN values
    start_value = fcf.iloc[-1]
    end_value = fcf.iloc[0]
    num_years = len(fcf) - 1

    if start_value <= 0 or end_value <= 0:
        logging.info("Invalid FCF values for growth rate calculation. returning default 5%")
        return 5.0
    if 'growth' in stock.earnings_estimate:
        cagr=stock.earnings_estimate['growth'].iloc[-1]
    else:
        cagr = (end_value / start_value) ** (1 / num_years) - 1
    

    return cagr * 100  # Convert to percentage

def convert_to_usd(amount, currency):
    if currency == "USD":
        return amount
    response = requests.request("GET",url, params=query_string)
    df = pd.read_json(StringIO(response.text))
    df.reset_index(inplace=True)
    currency_to='USD'
    stock_price_USD = (amount/df[df['index'].str.contains(currency)]['rates'].values[0])*df[df['index'].str.contains(currency_to)]['rates'].values[0]
    if df.empty:
        raise ValueError(f"Error fetching currency conversion: {response.status_code()}")

    return stock_price_USD

def calculate_intrinsic_value(ticker, growth_rate, discount_rate, terminal_growth_rate, projection_years):
    # print(f"calculating value for  {ticker, growth_rate, discount_rate, terminal_growth_rate, projection_years}")
    growth_rate /= 100.0
    discount_rate /= 100.0
    terminal_growth_rate /= 100.0
    stock = yf.Ticker(ticker)
    fcf = stock.cashflow.loc['Free Cash Flow']
    if fcf.empty:
        raise ValueError("Free Cash Flow data is not available for this stock.")
    currency = stock.info['currency']
    
    avg_fcf = fcf.mean() # changing this average for the last FCF recorded
    avg_fcf=fcf.iloc[0]
    projected_fcf = [avg_fcf * (1 + growth_rate) ** year for year in range(1, projection_years + 1)]
    terminal_value = projected_fcf[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    discounted_fcf = [fcf / (1 + discount_rate) ** year for year, fcf in enumerate(projected_fcf, start=1)]
    discounted_terminal_value = terminal_value / (1 + discount_rate) ** projection_years
    intrinsic_value = sum(discounted_fcf) + discounted_terminal_value
    
    shares_outstanding = stock.info['sharesOutstanding']
    intrinsic_value_per_share = intrinsic_value / shares_outstanding
    return intrinsic_value_per_share


def calculate_grahams_formula_2(ticker, growth_rate=5.0):
    # print(f"calculating grahams value 2nd method for  {ticker, growth_rate}")
    growth_rate /= 100.0
    stock = yf.Ticker(ticker)
    eps = stock.info['trailingEps']
    if eps is None or eps<0:
        logging.info(f"EPS data is not available for {ticker} or eps negative")
        return 0
    currency = stock.info['currency']
    # eps = convert_to_usd(eps, currency)
    graham_value = eps * (8.5 + 2 * growth_rate) * 4.4 / 3
    return graham_value

def calculate_grahams_formula(ticker,growth_rate=5.0):
    # print(f"calculating grahams value for  {ticker, growth_rate}")
    stock = yf.Ticker(ticker)
    eps = stock.info['trailingEps']
    
    tangible_book_value_per_share = stock.balancesheet.loc['Tangible Book Value'] / stock.fast_info['shares']

    if eps is None or eps<0 or tangible_book_value_per_share.empty or tangible_book_value_per_share.iloc[0]<0:
        logging.info(f"EPS or Tangible Book Value data is not available for this stock or is negative.{ticker} using 2nd Graham method")
        return calculate_grahams_formula_2(ticker)  

    tangible_book_value_per_share = tangible_book_value_per_share.iloc[0]  # Use the most recent tangible book value per share
    graham_number = (22.5 * eps * tangible_book_value_per_share) ** 0.5
    return graham_number

def calculate_ddm(ticker, dividend_growth_rate, discount_rate):
    stock = yf.Ticker(ticker)
    dividend = stock.info.get('dividendRate')
    if dividend is None:
        logging.warning(f"Dividend data is not available for {ticker}.")
        return None
    currency = stock.info['currency']
    dividend = convert_to_usd(dividend, currency)
    intrinsic_value = dividend * (1 + dividend_growth_rate) / (discount_rate - dividend_growth_rate)
    return intrinsic_value


def calculate_residual_income(ticker, equity_cost_of_capital, growth_rate):
    stock = yf.Ticker(ticker)
    roe = stock.info['returnOnEquity']
    bvps = stock.info['bookValue']
    if roe is None or bvps is None:
        raise ValueError("ROE or BVPS data is not available for this stock.")
    currency = stock.info['currency']
    bvps = convert_to_usd(bvps, currency)
    residual_income = bvps * (roe - equity_cost_of_capital)
    intrinsic_value = residual_income / (1 + growth_rate)
    return intrinsic_value


def calculate_apv(ticker, wacc, growth_rate, debt_ratio):
    stock = yf.Ticker(ticker)
    ebit = stock.info['ebitda']  # Using EBITDA as a proxy for EBIT
    if ebit is None:
        raise ValueError("EBIT data is not available for this stock.")
    currency = stock.info['currency']
    ebit = convert_to_usd(ebit, currency)
    # could change to 28%
    tax_rate = stock.info.get('taxRate', 0.21)
    intrinsic_value = ebit * (1 - tax_rate) / (wacc - growth_rate)
    unlevered_value = intrinsic_value * (1 - debt_ratio)
    return unlevered_value


def calculate_epv(ticker,wacc):
    stock = yf.Ticker(ticker)
    ebit = stock.info['ebitda']  # Using EBITDA as a proxy for EBIT
    if ebit is None:
        raise ValueError("EBIT data is not available for this stock.")
    currency = stock.info['currency']
    ebit = convert_to_usd(ebit, currency)
    
    
    intrinsic_value = ebit / wacc
    return intrinsic_value


def calculate_asset_based_value(ticker):
    stock = yf.Ticker(ticker)
    total_assets = stock.balance_sheet.loc['Total Assets']
    total_liabilities = stock.balance_sheet.loc['Total Liabilities Net Minority Interest']
    currency = stock.info['currency']
    total_assets = convert_to_usd(total_assets, currency)
    total_liabilities = convert_to_usd(total_liabilities, currency)
    intrinsic_value = total_assets - total_liabilities
    return intrinsic_value / stock.info['sharesOutstanding']


def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    current_price = stock.fast_info.last_price
    currency = stock.info['currency']
    return convert_to_usd(current_price, currency)


def get_company_name(ticker):
    stock = yf.Ticker(ticker)
    if stock.cash_flow.empty:
        logging.warning(f"Stock is not available {ticker}")
        return None
    else:
        return stock.info['longName']


def getAllIntrinsicValues(ticker, growth_rate=5.0, discount_rate=10.0, terminal_growth_rate=2.0, projection_years=5)->list:
    intrinsic_values = []
    if not ticker:
        logging.warning(f"Ticker '{ticker}' is invalid or empty")
        return None

    try:
        suggestedGrowthRate=calculate_historical_growth_rate(ticker)
        intrinsic_value_dcf = calculate_intrinsic_value(ticker, growth_rate, discount_rate, terminal_growth_rate,projection_years)
        graham_value = calculate_grahams_formula(ticker, growth_rate)
        # ddm_value = calculate_ddm(ticker, dividend_growth_rate=0.04, discount_rate=0.08)
        # rim_value = calculate_residual_income(ticker, equity_cost_of_capital=0.08, growth_rate=0.05)
        # apv_value = calculate_apv(ticker, wacc=0.08, growth_rate=0.05, debt_ratio=0.2)
        # epv_value = calculate_epv(ticker, wacc=0.08)
        # asset_value = calculate_asset_based_value(ticker)
        current_price = get_current_price(ticker)
        company_name = get_company_name(ticker)
        
        safety_margin_price_dcf = intrinsic_value_dcf * 0.7
        safety_margin_price_graham = graham_value * 0.7
        # safety_margin_price_ddm = ddm_value * 0.7 if ddm_value is not None else None
        # safety_margin_price_rim = rim_value * 0.7
        # safety_margin_price_apv = apv_value * 0.7
        # safety_margin_price_epv = epv_value * 0.7
        # safety_margin_price_asset = asset_value.iloc[-1] * 0.7 if isinstance(asset_value, pd.Series) else asset_value * 0.7

        # Try setting locale to something that supports currency
        # locale.setlocale(locale.LC_ALL, '')


        intrinsic_values.append({
            'Ticker': ticker,
            'Company Name': company_name,
            'Estimaded earnings +1y %':round(suggestedGrowthRate,2),
            'Intrinsic Value (DCF)': "${:,.2f}".format(intrinsic_value_dcf),
            'Graham Value': "${:,.2f}".format(graham_value),
            # 'DDM Value': locale.currency(round(ddm_value, 2), grouping=True) if ddm_value is not None else None,
            # 'RIM Value': locale.currency(round(rim_value, 2), grouping=True),
            # 'APV Value': locale.currency(round(apv_value, 2), grouping=True),
            # 'EPV Value': locale.currency(round(epv_value, 2), grouping=True),
            # 'Asset-Based Value': locale.currency(round(asset_value.iloc[-1], 2), grouping=True) if isinstance(asset_value, pd.Series) else locale.currency(round(asset_value, 2), grouping=True),
            'Current Price': "${:,.2f}".format(current_price),
            'Price - 30% Safety Margin (DCF)': "${:,.2f}".format(safety_margin_price_dcf),
            'Below 30% Safety Margin (DCF)': bool(current_price < safety_margin_price_dcf),
            'Price - 30% Safety Margin (Graham)': "${:,.2f}".format(safety_margin_price_graham),
            'Below 30% Safety Margin (Graham)': bool(current_price < safety_margin_price_graham),
            # 'Price - 30% Safety Margin (DDM)': locale.currency(round(safety_margin_price_ddm, 2), grouping=True) if safety_margin_price_ddm is not None else None,
            # 'Below 30% Safety Margin (DDM)': bool(current_price < safety_margin_price_ddm) if safety_margin_price_ddm is not None else None,
            # 'Price - 30% Safety Margin (RIM)': locale.currency(round(safety_margin_price_rim, 2), grouping=True),
            # 'Below 30% Safety Margin (RIM)': bool(current_price < safety_margin_price_rim),
            # 'Price - 30% Safety Margin (APV)': locale.currency(round(safety_margin_price_apv, 2), grouping=True),
            # 'Below 30% Safety Margin (APV)': bool(current_price < safety_margin_price_apv),
            # 'Price - 30% Safety Margin (EPV)': locale.currency(round(safety_margin_price_epv, 2), grouping=True),
            # 'Below 30% Safety Margin (EPV)': bool(current_price < safety_margin_price_epv),
            # 'Price - 30% Safety Margin (Asset-Based)': locale.currency(round(safety_margin_price_asset, 2), grouping=True) if safety_margin_price_asset is not None else None,
            # 'Below 30% Safety Margin (Asset-Based)': bool(current_price < safety_margin_price_asset) if safety_margin_price_asset is not None else None
        })

    except Exception as e:
        logging.error(f"Error processing ticker {ticker}: {e}")
        return None

    return intrinsic_values

# Example usage
if __name__ == "__main__":

    tickers = ['intc']
    data={
        ticker:{
            "data": getAllIntrinsicValues(ticker,growth_rate=5.0, discount_rate=10.0, terminal_growth_rate=2.0, projection_years=5)
        
        }for ticker in tickers
    }
    print(data)