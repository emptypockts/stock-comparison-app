
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,SystemMessage
from prompts import quant_instructions,synthesis_prompt
from outils import (
    clean_edgar_text, 
    analyze_ticker,
    save_analysis_report
)
from pymongo.server_api import ServerApi
from pymongo import MongoClient, errors,UpdateOne
from pymongo.collection import Collection
from secDBFetch import get_sec_filings
from datetime import datetime,timedelta
from textwrap import dedent

load_dotenv()

import os
GEMINI_API=os.getenv('GEMINI_API')
directory=os.getenv('DIRECTORY')


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=GEMINI_API)
# llm=ChatOllama(model="llama3.2:latest")

    
def quant(ticker:str,collection:object=None)->str:
    """
    quant analyzes a ticker 10K, 10Q, 8K, DEF 14A reports and identify red flags and opportunities
    args:
        ticker of the company
        collection object for MongoDB
    returns:
        str report
    """
    ticker_dir=os.path.join(directory,ticker)
    extension=".quant"
    needs_analysis, existing_report = analyze_ticker(directory,ticker.capitalize(),extension=extension)
    if not needs_analysis:
        print(f"Analysis for ticker '{ticker}' is up to date.")
        return existing_report

    submitted_reports={}
    files = os.listdir(ticker_dir)
    for file in files:
        if file.endswith((".json",".quant")):
            pass
        else:
            file_name=os.path.join(ticker_dir,file)
            with open(file_name) as f:
                report=f.read()
                clean_report=clean_edgar_text(report)
                response = llm.invoke(
                    [
                        SystemMessage(content=quant_instructions),
                        HumanMessage(content=f"here is the report: {clean_report}")
                    ]
                )
                submitted_reports[file.split('.')[0]]=response.content
    final_response=llm.invoke(
        [
            HumanMessage(content=synthesis_prompt.format(filing_summaries=submitted_reports))
        ]
    )
    if final_response.content:
        ai_final_response_json={"final_report":final_response.content}
        save_analysis_report(ticker_dir, ticker, ai_final_response_json,extension=extension)
        print(f"Saved analysis report for ticker {ticker}\n")

    return  final_response.content



if __name__=="__main__":
    print(dedent(quant("tsla".capitalize())['final_report']))

