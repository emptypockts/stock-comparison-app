import json
import os
from datetime import datetime, timedelta
from outils import clean_edgar_text,analyze_ticker,save_analysis_report,process_sec_chunks,synthetize_summaries,llm
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_ollama import ChatOllama
from prompts import rittenhouse_synthesis_instructions,summarize_chunk_instructions
load_dotenv()
DIRECTORY=os.getenv('DIRECTORY')




#define the form types to fetch the files if needed
form_types = ['10-K', '10-Q', '8-K', 'DEF 14A','20-F','6-K'] 

# Function to load and preprocess text files
def load_and_preprocess(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        text=clean_edgar_text(text)
    return text



def rittenhouse_analysis(report)->str:
    try:
        summaries = process_sec_chunks(report=report,instructions=summarize_chunk_instructions)
        final_report = synthetize_summaries(summaries=summaries,instructions=rittenhouse_synthesis_instructions)
        if final_report:
            return final_report
        else:
            raise Exception(f"response has no content. see details: {response}")
            return {}
    except Exception as e:
        print("error executing final summary", str(e))
        return None

    
def synthetize_rittenhouse_reports(reports)->str:
    response=llm.invoke(
        [
            SystemMessage(content=rittenhouse_synthesis_instructions),
            HumanMessage(content=f"reports: {reports}")
        ]
    )
    if response.content:
        validated_json=json.loads(response.content.replace("```json","").replace("```","").strip().lower())
        return validated_json
    else:
        raise Exception(f"response has no content. see details: {response}")
        return {}
    
def quant_rittenhouse(year,tickers:list)->str:
    responses={}
    directory= os.path.join(DIRECTORY,year)
    tickers=[t.capitalize()for t in tickers]
    for ticker in tickers:
        ticker_dir=os.path.join(directory,ticker)
        extension=".rtn"

        needs_analysis, existing_report = analyze_ticker(directory,ticker,extension=extension)
        
        if not needs_analysis:
            print(f"Analysis for ticker '{ticker}' is up to date.")
            return existing_report  # Return the most recent analysis if no new analysis is needed
        
        for file_name in os.listdir(ticker_dir):
            if file_name.endswith('.txt'):
                with open(os.path.join(ticker_dir,file_name)) as f:
                    report=f.read()
                    clean_report=clean_edgar_text(report)
                    response = rittenhouse_analysis(clean_report)
                    if response:
                        responses[file_name.split('.')[0]]=response

        final_report=synthetize_rittenhouse_reports(responses)
        
        if final_report:
            save_analysis_report(ticker_dir, ticker, final_report,extension=extension)
            print(f"Saved analysis report for ticker {ticker}\n")
        
        return final_report



# Example function call
if __name__ == "__main__":
      # Root directory where ticker folders are stored
    ticker = ['sofi']  # Example ticker
    current_year=datetime.now().year
    directory = f"{DIRECTORY}/{current_year}"
    last_year=current_year-1
    current_qtr=datetime.now().month
    last_qtr=(datetime.now()-timedelta(days=90)).month
    extension=".rtn"
    response = quant_rittenhouse(str(current_year),ticker)
    print(response)
    
        