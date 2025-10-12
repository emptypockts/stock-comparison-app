from dotenv import load_dotenv
import os
import requests
from companyData import compile_stockData
from fetch5yData import fetch_5y_data
from stockPlotData import fetch_financials
from stockPlotDataQtr import fetch_4qtr_data
from stockIntrinsicVal import getAllIntrinsicValues
import pandas as pd
import json
load_dotenv()
API_KEY = os.getenv("GEMINI_API")
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
querystring = {"key": API_KEY}
def get_company_data_agent(tickers)->str:
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
def get_company_score_agent(tickers)->str:
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
    Do not speculate on stock prices. Focus only on the financial data provided.

    Here is the historical data:
    """
def get_company_financials_agent(tickers)->str:
    return f"""
    You are a financial analysis assistant helping investors make informed decisions. You receive financial data for up to 3 stock tickers given here {tickers}, 
    each consisting of multiple years of key financial metrics (such as revenue, net income, free cash flow, assets, liabilities, EPS, and dividends).
    Your task is to analyze the trends over time for each ticker and highlight insights such as:
    Revenue and income growth or decline
    Changes in profitability (e.g. return on assets, EPS trends)
    Free cash flow sustainability and capital allocation
    Dividend consistency or risk of cuts
    Liquidity and financial health (cash vs. liabilities)
    Then compare the tickers against each other using key financial metrics and suggest which one(s) may be more attractive to a long-term investor.
    Be concise but insightful, use plain language, and avoid overly technical jargon. Include bullet points for clarity where appropriate.
    Do not speculate on stock prices. Focus only on the financial data provided.
    """
def get_company_financials_qtr_agent(tickers)->str:
    return f"""
    You are a financial analysis AI assistant that evaluates and compares companies based on their quarterly financial statements.
    You receive structured financial data for up to 3 stock tickers given here {tickers}, each with quarterly values for key metrics such as:

    Revenue and Net Income
    Earnings Per Share (Basic and Diluted)
    Operating & Investing Cash Flows
    Free Cash Flow (FCF)
    Assets, Liabilities, Return on Assets (ROA)
    Capital Expenditures and Dividends
    Your tasks:
    Analyze the most recent 3-4 quarters per ticker and summarize trends:
    Is revenue growing or declining?
    Is profitability (EPS, Net Income, ROA) improving or weakening?
    Is free cash flow strong and consistent?
    Are cash flows supporting dividend payments and capex?
    Evaluate financial health:
    Are assets growing faster than liabilities?
    Is ROA stable or improving?
    Compare tickers side by side:
    Highlight which company shows better growth, consistency, or financial strength.
    Deliver insights clearly:
    Use bullet points
    Avoid complex financial jargon
    Be concise but insightful
    Do not speculate on stock prices. Focus only on the financial data provided.
    """
def get_company_intrinsic_value_agent(tickers)->str:
    return f"""
    You are a financial valuation assistant specializing in intrinsic value analysis using Discounted Cash Flow (DCF) and Graham valuation models.
    You are given structured data for up to 3 tickers given here {tickers}. For each, you receive:
    Estimated Earnings Growth for the next year
    Intrinsic Value (DCF and Graham)
    Current Market Price
    30% Margin of Safety levels for both models
    Flags indicating whether the current price is below the safety margin

    Your job is to:

    Assess each stock individually:

    Is the stock undervalued or overvalued based on intrinsic value vs. current price?
    Is the current price within a 30% safety margin?

    Highlight if the stock has strong projected growth (e.g., above 20%)
    Compare across all tickers:
    Which stock appears most undervalued?
    Which has the highest upside potential based on estimated earnings?
    Which stock offers a better margin of safety?
    Present insights clearly:
    Use bullet points and short paragraphs
    Avoid technical valuation math
    Speak in plain language suitable for a retail investor audience
    Do not recommend buying or selling. Simply highlight valuation insights and risk indicators based on the data provided.
    """
def get_full_report_agent(tickers)->str:
    return f"""
    you are an expert financial agent and you will analyse the reports provided here and provide a final report ready to be processed.
    analysis expected: 

    ## 1. Executive Summary
    This report reviews the financial health, performance trends, and valuation insights for the following companies: {tickers}.

    ## 2. Financial Trends Analysis (Annual)
    [Insert AI-generated insights about annual trends, revenue, ROA, FCF, etc.]

    ## 3. Quarterly Performance Review
    [Insert quarterly data analysis for {tickers}.]

    ## 4. Intrinsic Value Analysis
    [Insert DCF & Graham valuation summaries for {tickers}.]

    ## Conclusion
    [Comparison and wrap-up.]

    ✅ The output MUST be a **pure JSON array** (no wrapper object, no "report" field, etc.), where each element matches **exactly one** of the following formats:

    1. {{ "type": "title", "content": "string" }}
    2. {{ "type": "paragraph", "content": "string" }}
    3. {{ "type": "bullets", "content": ["bullet1", "bullet2", ..., "bulletn"] }}

    Do NOT include any outer object like {{ "report": [...] }}. Only return the array.

    Ensure the JSON is valid and ready for parsing.
    """
def get_json_validator():
    return """
You are a JSON Output Validator.

Your job is to receive a JSON object generated by another AI agent and ensure that:
1. The JSON is syntactically valid.
2. The structure matches the expected schema.
3. Any errors or mismatches are clearly reported.
4. You return structured output as shown below.

Expected schema:
[
    {
        "type": "title",
    "content": "string"
    },
    {
    "type": "paragraph",
    "content": "string"
    },
    {
    "type": "bullets",
    "content": ["bullet1", "bullet2", "... bulletn"]
    }
]

if the validated json object is correct, return the same, otherwise return the new object.

Additional rules:
- Never guess field values.
- Optionally, you may correct common formatting issues only if it's clear and safe.
- Be concise, structured, and strictly follow the output format.
"""
def ai_query(agent, data)->str:

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
    if response.status_code==429:
        raise Exception("quota exceeded",response)
    response = response.json()
    
    return response["candidates"][0]["content"]["parts"][0]["text"]
def get_full_report(agent,r1,r2,r3,r4,r5)->str:
    payload = {
            "system_instruction": {"parts": [{"text": agent}]},
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""current status report\n {r1}\n value score report\n{r2}
                            yearly report\n{r3}\n quarterly report{r4}\n intrinsic value report{r5}
                            """ }
                    ]
                }
            ],
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers, params=querystring)
    if response.status_code==429:
        raise Exception("quota exceeded",response)
    response = response.json()
    return response["candidates"][0]["content"]["parts"][0]["text"]
def validate_json(agent,r6)->str:
    payload={
        "system_instruction":{"parts":[{"text":agent}]},
        "contents":[
            {
                "parts":[
                    {
                        "text":r6
                    }
                ]
            }
        ],
    }
    headers= {"Content-Type":"application/json"}
    response=requests.post(url,json=payload,headers=headers,params=querystring)
    if response.status_code==429:
        raise Exception("quota exceeded",response)
    response=response.json()
    return response["candidates"][0]["content"]["parts"][0]["text"]
def compile(tickers)->str:
    try:
        #ai agent that analyses company basic data such as revenue and stock price
        company_data_agent = get_company_data_agent(tickers)
        ai1 = compile_stockData(tickers)
        
        #ai agent that score companies based on the Benjamin G. valued investor analysis
        ai2={
            "ticker":[ticker for ticker in tickers],
            "data":[fetch_5y_data(e).to_json() for e in tickers]
        }
        
        company_score_agent = get_company_score_agent(tickers)
        
        #ai agent that analyses financials
        company_financials_agent=get_company_financials_agent(tickers)
        ai3 ={
            "ticker":[ticker for ticker in tickers],
            "data":[json.dumps(fetch_financials(e)) for e in tickers]
        }

        #ai agent that analyses financials per quarter
        company_financials_qtr_agent = get_company_financials_qtr_agent(tickers)
        ai4 = {
            "ticker":[ticker for ticker in tickers],
            "data":[json.dumps(fetch_4qtr_data(e)) for e in tickers]
        }

        #ai agent that analyses intrinsic value
        company_intrinsic_value_agent = get_company_intrinsic_value_agent(tickers)
        ai5 = {
            "ticker":[ticker for ticker in tickers],
            "data":[json.dumps(getAllIntrinsicValues(e))for e in tickers]
        }


        # trigger ai agents
        r1 = ai_query(company_data_agent, ai1)
        r2 = ai_query(company_score_agent,ai2)
        r3 = ai_query(company_financials_agent,ai3)
        r4 = ai_query(company_financials_qtr_agent,ai4)
        r5 = ai_query(company_intrinsic_value_agent,ai5)

        #final report
        try:
            full_report_agent =get_full_report_agent(tickers) 
            r6 =get_full_report(full_report_agent,r1,r2,r3,r4,r5)
        except Exception as e:
            print(str(e))
            raise(f"error getting full report is {str(e)}")
        #validate json object
        json_validator_agent=get_json_validator()
        response = validate_json(json_validator_agent,r6.replace("```","").replace("json","").strip().lower())
        r7=json.loads(response.replace("```json","").replace("```","").strip().lower())
        return r7
        
        
    except Exception as e:
        return e
if __name__ == "__main__":
    tickers = ["ko",'celh','pep']

    print(compile(tickers))
