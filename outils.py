from bs4 import BeautifulSoup
from lxml import etree
from datetime import datetime,timedelta
import os
import json
import re 
from typing import Literal
from secDBFetch import get_sec_filings
from dotenv import load_dotenv
import requests
from langchain_text_splitters import RecursiveCharacterTextSplitter
load_dotenv()
API_KEY = os.getenv("GEMINI_API")
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
querystring = {"key": API_KEY}

form_types = ['10-K', '10-Q', '8-K', 'DEF 14A','20-F','6-K'] 
def clean_edgar_text(content: str) -> str:
    """
    Extracts and cleans the text from only the first document (<DOCUMENT>...</DOCUMENT>)
    in an SEC submission file, excluding embedded image/base64 content.
    """
    
    match = re.search(r"<DOCUMENT>(.*?)</DOCUMENT>", content, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("No <DOCUMENT> section found.")
    first_doc = match.group(1)

    
    first_doc = re.sub(r"begin [\s\S]+?end", "", first_doc, flags=re.IGNORECASE)

    
    soup = BeautifulSoup(first_doc, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def is_new_analysis_needed(ticker_dir,extension:Literal[".json",".quant",".rtn"]):
    three_months_ago = datetime.now() - timedelta(days=90)
    most_recent_report = None
    for file_name in os.listdir(ticker_dir):
        if file_name.endswith(extension):
            file_date_str = re.findall(r'\d{4}-\d{2}-\d{2}', file_name)
            if file_date_str:
                file_date = datetime.strptime(file_date_str[0], '%Y-%m-%d')
                if file_date > three_months_ago:
                    # Load the most recent analysis report
                    with open(os.path.join(ticker_dir, file_name), 'r', encoding='utf-8') as f:
                        most_recent_report = json.load(f)

                    return False, most_recent_report
    return True, None

def analyze_ticker(directory, ticker,extension:Literal[".json",".quant",".rtn"]):
    reports = []
    ticker_dir = os.path.join(directory, ticker.capitalize())
    
    if not os.path.exists(ticker_dir):
        print(f"Directory for ticker '{ticker}' not found. Creating folder...")
        os.makedirs(ticker_dir)
        get_sec_filings(directory=directory,ticker=ticker, form_types=form_types)
    
    # Check if any .txt files are older than 3 months and delete them
    three_months_ago = datetime.now() - timedelta(days=90)
    txt_files_exist = False
    
    for file_name in os.listdir(ticker_dir):
        if file_name.endswith('.txt'):
            file_path = os.path.join(ticker_dir, file_name)
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mod_time < three_months_ago:
                print(f"Deleting outdated file: {file_name}")
                os.remove(file_path)
            else:
                txt_files_exist = True
    
    # Fetch new data if no recent .txt files are left
    if not txt_files_exist or not os.listdir(ticker_dir):
        print(f"No recent files for '{ticker}' found. Fetching data...")
        get_sec_filings(directory=directory,ticker=ticker, form_types=form_types)
    
    needs_analysis, existing_report = is_new_analysis_needed(ticker_dir,extension)

    return needs_analysis,existing_report

def save_analysis_report(ticker_dir:str, ticker:str, report:str,extension: Literal[".quant",".json",".rtn"]):
    """
    this function save the report in the server
    args:
        ticker_dir: ticker directory
        ticker: the ticker name
        report: the report to be saved
        extension: the extension to use, .quant for red flag ai report, .json for other ai reports and .rittenhouse for rittenhouse sentiment report
    """
    today = datetime.today().strftime('%Y-%m-%d')
    report_file = os.path.join(ticker_dir, f"{ticker.capitalize()}_analysis_{today}{extension}")
    with open(report_file, 'w', encoding='utf-8') as f:
        if extension==".json":
            json.dump(report, f, ensure_ascii=False, indent=4)
        else:
            report = json.dumps(report,indent=4,ensure_ascii=False)
            f.write(report)
def json_validator(agent,r6)->str:
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

def parse_tickers(tickers):
    TICKER_RE = re.compile(r"^[a-z0-9\.\-]{1,10}$")
    clean_tickers=[]
    for ticker in tickers:
        if not ticker:
            continue
        if not TICKER_RE.match(ticker.lower().strip()):
            continue
        clean_tickers.append(ticker)

    return clean_tickers

def chunk_report(report:str)->list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=150,
        separators=["\n\n","\n","."," "]
    )
    return splitter.split_text(report)