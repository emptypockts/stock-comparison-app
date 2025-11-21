
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,SystemMessage
import json
from datetime import datetime
from prompts import quant_instructions,synthesis_prompt,json_validator_instructions
from outils import (
    clean_edgar_text, 
    analyze_ticker,
    save_analysis_report,
    json_validator
)
load_dotenv()

import os
GEMINI_API=os.getenv('GEMINI_API')
DIRECTORY=os.getenv('DIRECTORY')


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=GEMINI_API,max_retries=1)
# llm=ChatOllama(model="llama3.2:latest")

    
def quant(year,tickers:list)->str:
    """
    quant analyzes a ticker 10K, 10Q, 8K, DEF 14A reports and identify red flags and opportunities
    args:
        ticker of the company
    returns:
        str report
    """
    
    directory= os.path.join(DIRECTORY,year)
    tickers=[t.capitalize()for t in tickers]
    for ticker in tickers:
        ticker_dir=os.path.join(directory,ticker)
        extension=".quant"


        needs_analysis, existing_report = analyze_ticker(directory,ticker,extension=extension)
        if not needs_analysis:
            print(f"Analysis for ticker '{ticker}' is up to date.")
            try:
                return json.dumps(existing_report)
            except Exception as e:
                print("error returning a json object", e)
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
            try:
                validated_json=json.loads(json_validator(json_validator_instructions,final_response.content).replace("```json","").replace("```","").strip().lower())
                save_analysis_report(ticker_dir, ticker, validated_json,extension=extension)
                print(f"Saved analysis report for ticker {ticker}\n")
                return  validated_json
            except Exception as e:
                print("error returning a json structure: ",e)
                return final_response.content




if __name__=="__main__":
    year= str(datetime.now().year)
    print(quant(year,["aapl"]))

