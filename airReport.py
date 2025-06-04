from dotenv import load_dotenv
import os
import requests
from companyData import compile_stockData
from fetch5yData import fetch_5y_data
import pandas as pd

load_dotenv()
import json


def get_company_data_agent(tickers):
    return f"""
    You are a financial analysis AI assistant designed to generate concise, insightful feedback for investors.

    You will receive a Python dictionary with financial data per stock tickers {tickers}. Each entry contains:
    - General stock info: symbol, name, share count, market cap, and derived current price
    - A list of recent quarterly earnings (filing date, revenue in millions)
    - The last known filing date

    Your role:
    1. Analyze trends in quarterly revenue over time — identify if revenue is growing, stable, or declining.
    2. Evaluate whether the market cap appears undervalued or overvalued based on recent revenue figures (simple revenue multiples).
    3. Flag any unusual patterns like sharp revenue drops, delayed filings, or zero earnings.
    4. Use layman's terms in your feedback so it’s digestible for non-technical investors.
    5. For each ticker, provide a brief insight summary (2–4 bullet points) that could help an investor decide whether to look deeper, hold, or avoid.

    Avoid financial advice (e.g., "Buy now"), but you can suggest whether a stock appears "worth further analysis" or "shows signs of risk."""

def get_company_score_agent(tickers):
    return f"""
    You are an AI assistant specialized in value investing, inspired by the principles of Benjamin Graham. Your job is to review a company's historical financials and determine how well it aligns with value investing standards.

Company ticker : {tickers}

You will be given one row per fiscal year. Each row includes:
- Raw metrics (EPS, Debt, FCF, Market Cap, Dividend Yield, etc.)
- Calculated valuation ratios (P/E, P/B, Debt/FCF, Earnings Yield)
- A score from 0 to 7 that evaluates value-aligned traits.

Each score represents:
1. Market Cap Score → if the company is large enough
2. P/E Ratio Score → favorable if mean P/E < 15
3. P/B Ratio Score → favorable if mean P/B < 2
4. Debt-to-FCF Score → favorable if total debt relative to cash flow is low
5. Earnings Yield Score → favorable if positive across all years
6. 1.3x Earnings Yield Growth Score → favorable if yield has grown at least 130%
7. Dividend Yield Score → favorable if dividends exist each year

**High score (6–7):** aligns with classic value investing  
**Low score (0–2):** may indicate risk, debt load, or unproven growth  
**Mid scores (3–5):** mixed signals — investigate further

Your response should:
- Summarize valuation trends across time
- Explain if the company's investment profile is improving or deteriorating
- Clarify the meaning of the score in this case (not all low scores are bad)
- Output 3–5 bullet points
- Avoid financial advice (e.g., "buy", "sell") but suggest whether it's "value-aligned", "growth-tilted", or "risky fundamentals"

Here is the historical data:
"""


API_KEY = os.getenv("GEMINI_API")

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
querystring = {"key": API_KEY}


def chat_query(agent, data):

    payload = {
        "system_instruction": {"parts": [{"text": agent}]},
        "contents": [
            {
                "parts": [
                    {"text": "here is the stock data \n" + json.dumps(data, indent=2)}
                ]
            }
        ],
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers, params=querystring)
    response = response.json()
    return response["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == "__main__":
    tickers = ["pltr", "axp"]
    response =[]
    
    company_data_agent = get_company_data_agent(tickers)
    d1 = compile_stockData(tickers)
    
    d2={
        "ticker":[ticker for ticker in tickers],
        "data":[fetch_5y_data(e).to_json() for e in tickers]
    }
    print(d2)
   
   
   
    company_score_agent = get_company_score_agent(tickers)
    
    # r1=chat_query(company_data_agent, d1)
    # r2= chat_query(company_score_agent,d2)

    
    

    
