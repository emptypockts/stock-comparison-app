from dotenv import load_dotenv
import json
from datetime import datetime
from financialUtils import fetch_name
from outils import ( 
    analyze_ticker,
    save_analysis_report,
    generic_trim_document,
    llm,
    quant_report,
    normalize_text,
    sections_summarizer,
    types_synthetiser,
    save_file_test,
    chunk_report
)
load_dotenv()
import os
DIRECTORY=os.getenv('DIRECTORY')
# analyses the sec reports from edgar db and provides a summary with red flags and suspicious patterns
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
    companies = fetch_name(tickers)
    for ticker,company in zip(tickers,companies):
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

        report_blocks=[]
        files = os.listdir(ticker_dir)
        # ====================================================== setting 1 file====================================
        for file in files:
            if file.endswith((".json",".quant",".rtn")):
                pass
            else:
                file_name=os.path.join(ticker_dir,file)
                with open(file_name,encoding='latin') as f:
                    report=f.read()
                    print ("\n\n---------generic prune-------------\n\n",datetime.now())
                    file_name_split = file_name.split('_')
                    report_type = file_name_split[1].strip()
                    report_date = file_name_split[2].strip()
                    pruned_doc = generic_trim_document(report,ticker,report_type,report_date,company)
                    pruned_doc_chunks = chunk_report(pruned_doc)
                    summary = sections_summarizer(pruned_doc_chunks)
                    report_blocks.append(summary)
        final_report = ' '.join(quant_report(report_blocks).split())
        if final_report:
            try:
                
                save_analysis_report(ticker_dir, ticker, final_report,extension=extension)
                print(f"Saved analysis report for ticker {ticker}\n")
                return  final_report
            except Exception as e:
                print("error returning a json structure: ",e)
                return final_report

if __name__=="__main__":
    year= str(datetime.now().year)
    print(quant(year,["Rost"]))

