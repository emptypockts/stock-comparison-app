from dotenv import load_dotenv
load_dotenv()
import json
from datetime import datetime
from financialUtils import fetch_name
from outils import ( 
    analyze_ticker,
    save_analysis_report,
    generic_trim_document,
    quant_report,
    extract_items,
    extract_def_14a_sections,
    )
from eacsa_logger import setup_logging,get_logger
setup_logging()
logger = get_logger(__name__)


import os
DIRECTORY_PATH = os.getenv('DIRECTORY')
# analyses the sec reports from edgar db and provides a summary with red flags and suspicious patterns
def quant(year,tickers:list[str])->list:
    """
    quant analyzes a ticker 10K, 10Q, 8K, DEF 14A reports and identify red flags and opportunities
    args:
        ticker of the company
    returns: a list object ready for parsing into a pdf report
    """
    logger.info("Start Quant log")
    REPORTS_WITH_ITEMS = ['10-K','8-K','10-Q']
    REPORTS_WITH_SECTIONS = ['DEF 14A']
    directory = os.path.join(DIRECTORY_PATH,year)
    tickers = [t.capitalize()for t in tickers]
    companies = fetch_name(tickers)
    final_reports = []
    for ticker,company in zip(tickers,companies):
        ticker_dir = os.path.join(directory,ticker)
        extension = ".quant"
        needs_analysis, existing_report = analyze_ticker(directory,ticker,extension=extension)
        if needs_analysis:    
            report_blocks=[]
            files = os.listdir(ticker_dir)
            # ====================================================== setting 1 file====================================
            for file in files:
                if file.endswith('.txt'):
                    file_name = os.path.join(ticker_dir,file)
                    with open(file_name,encoding = 'latin-1') as f:
                        report = f.read()
                        logger.info("Generic Prune Start")
                        try:
                            file_name_split = file_name.split('_')
                            report_type = file_name_split[2].strip()
                            report_date = file_name_split[3].strip()
                        except Exception as e:
                            logger.error(f"error trying to split the file: {file_name}.\n Error: {e}\nis it a sec report?")
                            continue
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
                            raise ValueError(f"report_type not recognized: {report_type}")
            
            final_report = ' '.join(quant_report(report_blocks).split())
            if final_report:
                try:
                    
                    save_analysis_report(ticker_dir, ticker, final_report,extension=extension)
                    logger.info(f"Saved analysis report for ticker {ticker}\n")

                    final_reports.append(json.loads(final_report))
                except Exception as e:
                    logger.error(f"loading obj into a json str: {e}")
                    continue
        else:
            logger.info(f"Analysis for ticker '{ticker}' is up to date.")
            final_reports.append(existing_report)
            
    # TODO: returning only last report as frontend works with 1 ticker at a time for the moment.
    return final_reports[-1] if final_reports else None
    

if __name__ == "__main__":
    year = str(datetime.now().year)
    print(quant(year,["celh"]))

