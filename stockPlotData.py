import pandas as pd
import yfinance as yf

def fetch_financials(ticker):
    stock = yf.Ticker(ticker)
    financial_data = []

    def get_financial_value(financial_df, labels, default=0):
        for label in labels:
            if label in financial_df.index:
                return financial_df.loc[label]
        return pd.Series([default] * len(financial_df.columns), index=financial_df.columns)

    revenue_labels = ['Total Revenue', 'Revenue']
    assets_labels = ['Total Assets', 'Total Current Assets']
    cash_labels = ['Cash', 'Cash And Cash Equivalents', 'Cash & Cash Equivalents']
    liabilities_labels = ['Total Liab', 'Total Liabilities Net Minority Interest', 'Total Liabilities & Shareholders Equity']
    net_income_labels = ['Net Income', 'Net Income Applicable To Common Shares']
    rd_labels = ['Research And Development', 'R&D']
    other_expenses_labels = ['Other Operating Expenses', 'Other Expenses']
    fcf_labels = ['Free Cash Flow', 'Operating Cash Flow']
    dividends_paid_labels = ['Cash Dividends Paid', 'Dividends']
    eps_labels = ['Basic EPS', 'Basic Earnings Per Share']

    # Fetch financial data for each metric
    revenue = get_financial_value(stock.financials, revenue_labels)
    assets = get_financial_value(stock.balance_sheet, assets_labels)
    cash = get_financial_value(stock.balance_sheet, cash_labels)
    liabilities = get_financial_value(stock.balance_sheet, liabilities_labels)
    net_income = get_financial_value(stock.financials, net_income_labels)
    rd = get_financial_value(stock.financials, rd_labels)
    other_expenses = get_financial_value(stock.financials, other_expenses_labels)
    fcf = get_financial_value(stock.cashflow, fcf_labels)
    Basic_EPS = get_financial_value(stock.financials, eps_labels)
    dividends_paid = get_financial_value(stock.cashflow, dividends_paid_labels)
    return_on_assets = (net_income / assets) if not assets.empty else pd.Series([0] * len(net_income), index=net_income.index)

    # Combine data into the expected structure, filtering out entries with all None values
    for date in revenue.index:
        financial_entry = {
            "date": str(date),
            "revenue": round(float(revenue.get(date, None)), 2) if not pd.isnull(revenue.get(date, None)) else None,
            "assets": round(float(assets.get(date, None)), 2) if not pd.isnull(assets.get(date, None)) else None,
            "cash": round(float(cash.get(date, None)), 2) if not pd.isnull(cash.get(date, None)) else None,
            "liabilities": round(float(liabilities.get(date, None)), 2) if not pd.isnull(liabilities.get(date, None)) else None,
            "net_income": round(float(net_income.get(date, None)), 2) if not pd.isnull(net_income.get(date, None)) else None,
            "rd": round(float(rd.get(date, None)), 2) if not pd.isnull(rd.get(date, None)) else None,
            "other_expenses": round(float(other_expenses.get(date, None)), 2) if not pd.isnull(other_expenses.get(date, None)) else None,
            "fcf": round(float(fcf.get(date, None)), 2) if not pd.isnull(fcf.get(date, None)) else None,
            "Basic EPS": round(float(Basic_EPS.get(date, None)), 2) if not pd.isnull(Basic_EPS.get(date, None)) else None,
            "dividends_paid": round(float(dividends_paid.get(date, None)), 2) if not pd.isnull(dividends_paid.get(date, None)) else None,
            "return_on_assets": round(float(return_on_assets.get(date, None)), 2) if not pd.isnull(return_on_assets.get(date, None)) else None
        }

        # Filter out entries where all values are None
        if any(value is not None for value in financial_entry.values() if value != "date"):
            financial_data.append(financial_entry)

    return financial_data

# Example function call
if __name__ == "__main__":
    all_data = []
    tickers = ['smci']  # Example ticker
    for ticker in tickers:
        try:
            data= fetch_financials(ticker)
            all_data.append(data)
        except:
            print(f"Cannot fetch stock {ticker}.")
            all_data.append(None)


    print(all_data)
