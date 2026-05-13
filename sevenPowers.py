from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,SystemMessage
import json
from datetime import datetime,timedelta
from prompts import seven_powers_instructions,json_validator_instructions
from outils import (
    analyze_ticker,
    save_analysis_report,
    generic_trim_document,
    llm,
    extract_def_14a_sections,
    extract_items
)
from financialUtils import fetch_name
import os
load_dotenv()
REPORTS_WITH_ITEMS = ['10-K','8-K','10-Q']
REPORTS_WITH_SECTIONS = ['DEF 14A']
DIRECTORY=os.getenv('DIRECTORY')
def seven_powers(tickers)->str:
    extension='.seven'
    current_year=datetime.now().year
    current_year=str(current_year)
    directory = f"{DIRECTORY}/{current_year}"

    directory= os.path.join(DIRECTORY,current_year)
    tickers=[t.capitalize()for t in tickers]
    companies = fetch_name(tickers)
    for ticker,company in zip(tickers,companies):
        ticker_dir=os.path.join(directory,ticker)
        extension=".seven"
        needs_analysis, existing_report = analyze_ticker(directory,ticker,extension=extension)
        if not needs_analysis:
            print(f"Analysis for ticker '{ticker}' is up to date.")
            return existing_report  # Return the most recent analysis if no new analysis is needed
        report_blocks=[]
        files = os.listdir(ticker_dir)
        # ====================================================== setting 1 file====================================
        for file in files:
            if file.endswith((".json",".quant",".rtn",".DS_Store",".seven")):
                pass
            else:
                file_name=os.path.join(ticker_dir,file)
                with open(file_name,encoding='latin') as f:
                    report=f.read()
                    print ("\n\n---------generic prune-------------\n\n",datetime.now())
                    file_name_split = file_name.split('_')
                    report_type = file_name_split[2].strip()
                    report_date = file_name_split[3].strip()
                    pruned_doc = generic_trim_document(report,ticker,report_type,report_date,company)
                    if report_type in REPORTS_WITH_ITEMS:
                        report_blocks.append(
                            {
                                "report_type":report_type,
                                "date_of_filing":report_date,
                                "ticker":ticker,
                                "data":extract_items(pruned_doc)
                            }
                        )
                    elif report_type in REPORTS_WITH_SECTIONS:
                        report_blocks.append(
                            {
                                "report_type":report_type,
                                "date_of_filing":report_date,
                                "ticker":ticker,
                                "data":extract_def_14a_sections(pruned_doc)
                            }
                        )
                    else:
                        raise(f"report type not recognized : {report_type}")
        response = llm.invoke(
            [
                SystemMessage(content=seven_powers_instructions),
                HumanMessage(content=f"ticker symbol: {tickers} latest SEC filed reports: {report_blocks}")
            ]
        )
        if response.content:
            validated_json=json.loads(response.content.replace("```json","").replace("```","").strip())
            save_analysis_report(ticker_dir, ticker, validated_json,extension=extension)
            print(f"Saved analysis report for ticker {ticker}\n")
            return validated_json
        else:
            raise Exception(f"response has no content. see details: {response}")
        
    


if __name__ == "__main__":
    user_query=['mov']
    response = seven_powers(user_query)
    print(response)