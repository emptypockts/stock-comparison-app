
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
load_dotenv()

import os
GEMINI_API=os.getenv('GEMINI_API')
directory=os.getenv('DIRECTORY')


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=GEMINI_API)
# llm=ChatOllama(model="llama3.2:latest")

    
def quant(tickers:list)->str:
    """
    quant analyzes a ticker 10K, 10Q, 8K, DEF 14A reports and identify red flags and opportunities
    args:
        ticker of the company
    returns:
        str report
    """
    tickers=[t.capitalize()for t in tickers]
    for ticker in tickers:
        ticker_dir=os.path.join(directory,ticker)
        extension=".quant"


        needs_analysis, existing_report = analyze_ticker(directory,ticker,extension=extension)
        if not needs_analysis:
            print(f"Analysis for ticker '{ticker}' is up to date.")
            try:
                return existing_report.replace("```json","").replace("```","").lower()
            except Exception as e:
                print("error returning a json object")
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
            
            save_analysis_report(ticker_dir, ticker, final_response.content,extension=extension)
            print(f"Saved analysis report for ticker {ticker}\n")
        try:
            return  final_response.content.replace("```json","").replace("```","").strip().lower()
        except Exception as e:
            print("error returning a json structure: ",e)
            return final_response.content.lower()




if __name__=="__main__":

    print(quant(["duo"]))

