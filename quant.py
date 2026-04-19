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
    replace_smart_punctuation,
    sections_summarizer,
    types_synthetiser,
    save_file_test
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
        summaries={}
        summary_reports=[]
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
                    report_blocks.append(generic_trim_document(report,ticker,report_type,report_date,company))
        print ("\n\n---------summarize all sections l2-------------\n\n",datetime.now())
        for types in report_blocks:
            for t in types:
                texts = t.get('texts_synthesis',[])
                if not texts:
                    t['summary']=""
                    continue
                elif len (texts)==1:
                    # if summarized texts are only 1 then it is the summary
                    t['summary']=texts[0]
                else:
                    # level 2 summarize the chunks into one per section
                    t['summary']= replace_smart_punctuation(sections_summarizer(texts))
            
            
            summaries[types[0]['file_name']]=[
                {"section_type": sec['section_type'],"summary":sec['summary']}
                for sec in types if sec.get('section_type') and sec.get('summary')
                ]

        
        for k,v in summaries.items():
            print("\n\n---------synthetise final report l3-------------\n\n",datetime.now())
            summary_reports.append(
                {
                    "file":k,
                    # level 3 summarizes the sections into one per report
                    "file_summary":replace_smart_punctuation(types_synthetiser(v))
                }
            )
        
            # level 4 summarizes the sections into one and exports it to a pdf file.
            print("\n\n---------prettyfying report almost done... l4-------------\n\n",datetime.now())
        final_report = ' '.join(quant_report(summary_reports).split())
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

