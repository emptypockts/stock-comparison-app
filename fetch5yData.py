import yfinance as yf
import pandas as pd

def fetch_5y_data(ticker):
    stock = yf.Ticker(ticker)
    dividends = stock.dividends

    def Transform_Obj_and_Date(Object):
        index = pd.to_datetime(Object.index)
        Object_df = pd.DataFrame(Object, index=index)
        Object_df.index = Object_df.index.year
        Object_df.index.name = 'Date'
        Object_df[Object.name] = Object_df[Object.name].astype(float)
        try:
            Object_df = Object_df.drop(2019)
        except:
            return Object_df
        return Object_df

    def check_market_cap(row):
        return int(row['Market Cap'] > 2e+09)

    def format_currency(value):
        return "${:,.2f}".format(value)

    def format_number(value):
        return "{:,.0f}".format(value)

    def format_ratio(value):
        return "{:.2f}".format(value)

    def format_percentage(value):
        return "{:.2f}%".format(value * 100)

    Avg_Shares = stock.financials.loc['Basic Average Shares']
    Avg_Shares_df = Transform_Obj_and_Date(Avg_Shares)
    tangible_book_value = stock.balance_sheet.loc['Stockholders Equity', :]
    tangible_book_value_df = Transform_Obj_and_Date(tangible_book_value)

    fcf = stock.cashflow.loc['Free Cash Flow']
    fcf_df = Transform_Obj_and_Date(fcf)

    EPS = stock.financials.loc['Basic EPS']
    EPS_df = Transform_Obj_and_Date(EPS)

    EPS_diluted = stock.financials.loc['Diluted EPS']
    EPS_diluted_df = Transform_Obj_and_Date(EPS_diluted)

    total_debt = stock.balance_sheet.loc['Total Debt']
    total_debt_df = Transform_Obj_and_Date(total_debt)

    dividends = dividends.resample('YE').sum()
    dividends_df = Transform_Obj_and_Date(dividends)

    price_per_share = stock.history(period='5y')['Close']
    price_per_share = price_per_share.resample('YE').last()
    price_per_share_df = Transform_Obj_and_Date(price_per_share)

    combined_df = pd.concat([
        Avg_Shares_df.rename(columns={Avg_Shares_df.columns[0]: 'Basic Average Shares'}),
        tangible_book_value_df.rename(columns={tangible_book_value_df.columns[0]: 'Tangible Book Value'}),
        fcf_df.rename(columns={fcf_df.columns[0]: 'Free Cash Flow'}),
        EPS_df.rename(columns={EPS_df.columns[0]: 'Basic EPS'}),
        EPS_diluted_df.rename(columns={EPS_diluted_df.columns[0]: 'Diluted EPS'}),
        total_debt_df.rename(columns={total_debt_df.columns[0]: 'Total Debt'}),
        dividends_df.rename(columns={dividends_df.columns[0]: 'Dividends'}),
        price_per_share_df.rename(columns={price_per_share_df.columns[0]: 'Price Per Share'})
    ], axis=1, join='outer')
    
    combined_df = combined_df.head(4)


    
    combined_df['Tangible Book Value Per Share'] = combined_df['Tangible Book Value'] / combined_df['Basic Average Shares']
    combined_df['p/b ratio'] = combined_df['Price Per Share'] / combined_df['Tangible Book Value Per Share']
    combined_df['p/e ratio'] = combined_df['Price Per Share'] / combined_df['Diluted EPS']
    combined_df['Debt FCF ratio'] = combined_df['Total Debt'] / combined_df['Free Cash Flow']
    combined_df['Dividends Yield'] = combined_df['Dividends'] / combined_df['Price Per Share']
    combined_df['Earnings Yield'] = combined_df['Diluted EPS'] / combined_df['Price Per Share']
    combined_df['Market Cap'] = combined_df['Basic Average Shares'] * combined_df['Price Per Share']

    # Calculate metrics
    combined_df['Market Cap Score'] = combined_df.apply(check_market_cap, axis=1)
    combined_df['p/e ratio Score'] = int(combined_df['p/e ratio'].mean() < 15)
    combined_df['p/b ratio Score'] = int(combined_df['p/b ratio'].mean() < 2)
    combined_df['Sum of Debt/FCF ratio Score'] = int(combined_df['Debt FCF ratio'].sum() > 0)
    combined_df['Earnings Yield Score'] = int(combined_df['Earnings Yield'].gt(0).all())
    initial_value = combined_df['Earnings Yield'].iloc[-1]  # 2020
    last_value = combined_df['Earnings Yield'].iloc[0]  # 2023
    # Calculate the percentage change from 2020 to 2023
    growth = (last_value - initial_value) / abs(initial_value)
    # Check if the growth is greater than or equal to 1.3x (130%)
    combined_df['1.3 Earnings Yield Score'] = (growth >= 1.3).astype(int)
    combined_df['Dividends Yield Score'] = int(combined_df['Dividends Yield'].gt(0).all())
    combined_df['Total Score'] = combined_df['Dividends Yield Score'] + combined_df['Earnings Yield Score'] + combined_df['1.3 Earnings Yield Score'] + combined_df['Sum of Debt/FCF ratio Score'] + combined_df['p/b ratio Score'] + combined_df['p/e ratio Score'] + combined_df['Market Cap Score']

    # remove $nan for 0
    combined_df=combined_df.fillna(0.01)
    # Formats
    combined_df['Basic Average Shares'] = combined_df['Basic Average Shares'].apply(format_number)
    combined_df['Tangible Book Value'] = combined_df['Tangible Book Value'].apply(format_currency)
    combined_df['Free Cash Flow'] = combined_df['Free Cash Flow'].apply(format_currency)
    combined_df['Basic EPS'] = combined_df['Basic EPS'].apply(format_currency)
    combined_df['Diluted EPS'] = combined_df['Diluted EPS'].apply(format_currency)
    combined_df['Total Debt'] = combined_df['Total Debt'].apply(format_currency)
    combined_df['Dividends'] = combined_df['Dividends'].apply(format_currency)
    combined_df['Price Per Share'] = combined_df['Price Per Share'].apply(format_currency)
    combined_df['Tangible Book Value Per Share'] = combined_df['Tangible Book Value Per Share'].apply(format_currency)
    combined_df['p/b ratio'] = combined_df['p/b ratio'].apply(format_ratio)
    combined_df['p/e ratio'] = combined_df['p/e ratio'].apply(format_ratio)
    combined_df['Debt FCF ratio'] = combined_df['Debt FCF ratio'].apply(format_ratio)
    combined_df['Dividends Yield'] = combined_df['Dividends Yield'].apply(format_percentage)
    combined_df['Earnings Yield'] = combined_df['Earnings Yield'].apply(format_percentage)
    combined_df['Market Cap'] = combined_df['Market Cap'].apply(format_currency)
    combined_df['Symbol'] = ticker
    combined_df['Name'] = stock.info['shortName']
    
    return combined_df
# Example function call
if __name__ == "__main__":
    
    tickers = ['nvda']  # Replace with your desired ticker
    all_data = []

    # all_data = [fetch_5y_data(ticker)for ticker in tickers]
    for ticker in tickers:
        try:
            data= fetch_5y_data(ticker)
            print('returned object: \n',data)
            all_data.append(data)
        except:
            print(f"Cannot fetch stock {ticker}.")
            all_data.append(None)

    combined_data = pd.concat(all_data,ignore_index=False)
    print(combined_data.to_string(index=False))
