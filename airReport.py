
from dotenv import load_dotenv
import os
import requests
from companyData import compile_stockData
load_dotenv()
import json
API_KEY = os.getenv('GEMINI_API')

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
querystring = {"key":API_KEY}

def chatQuery(agent,data):

    payload = {
        "system_instruction":{
            "parts":[
                {
                "text":agent
                }
            ]
        },
        "contents": [
        {
            "parts": [
            {
                "text": "here is the stock data \n"+json.dumps(data,indent=2)
            }
            ]
        }
        ]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post( url, json=payload, headers=headers, params=querystring)
    response =response.json()
    return response["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == "__main__":
    tickers=['pltr','axp']
    
    companyDataAgent= f"""
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
    data = compile_stockData(tickers)
    
    
    

    response = chatQuery(companyDataAgent,data)
    print(response)