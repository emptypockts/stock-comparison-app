from bs4 import BeautifulSoup,NavigableString
from datetime import datetime,timedelta
import os
import json
import re 
from langchain_core.messages import HumanMessage,SystemMessage
from typing import Literal
from secDBFetch import get_sec_filings
from dotenv import load_dotenv
import requests
import uuid
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from classes_langchain import Chunk
from prompts import (
    types_synthetiser_instructions,
    sections_summarizer_instructions,
    quant_instructions,
    recursive_summarize_instructions,
    mdna_analysis_instructions
    )
load_dotenv()


url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_API=os.getenv('GEMINI_API')
DIRECTORY=os.getenv('DIRECTORY')
DEEP_SEEK_API_KEY = os.getenv('DEEP_SEEK_API_KEY')
querystring = {"key": GEMINI_API}

#===========================================#
#           llm model seclection            #
#===========================================#

# llm = ChatOpenAI(model="groq/compound",base_url="https://api.groq.com/openai/v1")
# llm =ChatOpenAI(model="deepseek-reasoner",base_url="https://api.deepseek.com",api_key=DEEP_SEEK_API_KEY)
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=GEMINI_API,max_retries=1)
# llm=ChatOllama(model="phi4-mini-reasoning:3.8b",base_url="http://localhost:11434")
# llm=ChatOllama(model="gpt-oss:20b-cloud",base_url="https://ollama.com")
llm=ChatOllama(model="gpt-oss:120b-cloud",base_url="https://ollama.com")
# llm=ChatOllama(model="llama2-uncensored:latest")



#===========================================#
#     red flag sec report helpers           #
#===========================================#

def normalize_text(text: str,remove_tables=False) -> str:
    """
    Replace common smart punctuation characters with their standard equivalents.
    params:
        text: string to be normalized
    returns:     normalized string
    """
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\u2011": "-",
        "\u200b": " ",
        "\u2610": " ",
        "\u2611": " ",
        "\u2612": " ",
        "\u00a8":" ",
        "\u2022":" ",
        "\u25e6":" ",
        "\u00e9":" ",
        "\xa0": " ",
        "\u00a7":" ",
        "`" : "'",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[ \t\r\f\v]+',' ',text)
    text = re.sub(r"\b_{2,}\b","_",text)
    text = re.sub(r'[^a-zA-Z0-9 \n_\.,-]+',"",text)
    text = re.sub(' *\n *','\n',text)
    PAGE_IDX_PATTERN = re.compile(r'(?m)^\s*\d+\s*$\n?')
    text = re.sub(PAGE_IDX_PATTERN,'',text)
    TABLE_CONTENTS_PATTERN = re.compile(r'(?m)^\s*TABLE OF CONTENT(S.?)\s*$',re.I)
    text = re.sub(TABLE_CONTENTS_PATTERN,'',text)
    ONE_CHAR_PATTERN = re.compile(r'(?m)^\s*[a-z]{1,3}\s*$',re.I)
    text = re.sub(ONE_CHAR_PATTERN,'',text)
    if remove_tables:
        TABLE_PATTERN= re.compile(r'(?m)^\s*TABLE_\d+\s*$')
        text = re.sub(TABLE_PATTERN,'',text)
    text = re.sub(r'\n{3,}','\n\n',text)
    return text.strip()

# recursive langchain chunker
def recursively_chunk(text: str) -> list:
    """
    function to recursively chunk and add back the tables after the chunk is completed
    params:
        text: string of the sec report
        tables: list of tables
    returns: list of chunks
    """
    if len(text)<10000:
        return [text]
    else:
        overlap=200
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name='cl100k_base',
        chunk_size=10000,
        chunk_overlap=overlap,
    )
    text = normalize_text(text)
    texts= text_splitter.split_text(text)
    return texts




# find the first meaningful section for def14a reports
def find_init_def14a(main_soup):
    
    soup = BeautifulSoup(main_soup,'lxml')
    docs = soup.find_all(['span'])
    for doc in docs:
        if 'table of contents' in doc.get_text(" ",strip=True).strip().lower():
            return doc
# find the first meaningful section for 8k 10q 10k reports
def find_init_8k_10q_10k(main_soup):
    ITEM_PATTERN = re.compile(r"\bitem\s+\d(\.\d+)?\b", re.IGNORECASE)
    soup = BeautifulSoup(main_soup,"lxml")
    docs = soup.find_all(["span"])
    for doc in docs:
        text = doc.get_text(" ",strip=True).lower()
        if ITEM_PATTERN.search(text):
            return doc
# add tables back
def restore_tables(chunk,tables):
    
    for k,v in tables.items():
        pattern = rf'(?<!\w){re.escape(k)}(?!\w)'
        chunk=re.sub(
            pattern,
            f"\n\n----[TABLE START]----\n{v}\n\n----[TABLE END]----",chunk
        )
    return chunk

#===========================================#
#           etl                             #
#===========================================#

# level 2, summarize chunks. recursive
def process_sec_chunks(chunks:list,level:int=1)->list:
    """
    function to chunk a long text and summarize it. it will return a list of summarized chunks.
    
    params 
        report: Description
        type report: str
    returns: list of summarized chunks
    """
    if not chunks:
        return []
    
    chunks = [c for c in chunks if isinstance(c, str) and c.strip()]
    if not chunks:
        return []

    SYSTEM_MESSAGE = SystemMessage(content=recursive_summarize_instructions + f"\n Currently at synthesis Level {level}" )
    responses=[]
    if len(chunks)<=3 and level >1:
        return chunks
    responses =[]
    llm_current = llm
    # pairing chunks
    for i in range (0,len(chunks),2):
        batch = chunks[i:i+2]
        texts_to_combine=[]
        for b in batch:
            texts_to_combine.append(str(b))
        combined_content="\n\n----SECTION BREAK----\n\n".join(texts_to_combine)
        if len(combined_content.strip())<500:
            continue

        for attempt in range(2):
            try:
                print(f"calling llm with text (first 200 characters): {combined_content[0:200]}")
                response = llm_current.invoke([
                    SYSTEM_MESSAGE,
                    HumanMessage(content=normalize_text(combined_content))
                ])
                if response.content is None:
                    raise ValueError("llm didnt return any content")
                responses.append(response.content.replace("```json","").replace("```","").strip())

                
                break
            except:
                if attempt==1:
                    raise
    if not responses:
        return []
    return process_sec_chunks(responses,level+1)


# --------analyse mdna---------

def process_mdna(text:str,company:str):
    """
    function to analyze the mdna section with ai
    """
    if not text:
        raise ValueError(f"missing text")
    
    for attempt in range(2):
        try:
            response = llm.invoke([
                SystemMessage(content=mdna_analysis_instructions),
                HumanMessage(content=f"text for company:{company}:\n:{text}")
            ])
            if response.content is None:
                raise ValueError("llm did not return any content")
            break
            
        except:
            if attempt ==1:
                raise
        
    return response.content


def normalize_heading(text)->str:
    text = normalize_text(text).lower()
    text=re.sub(r"[^a-z0-9\s\-\.\(\)]","",text)
    return text

def get_lines(tag):
    text = tag.get_text("\n",strip=True)
    texts = text.split("\n")
    return texts
# etl with soup on sec report

def detect_child_bold(tag)->bool:
    for child in tag.find_all(['b','strong','span']):
        if child.name in ["b","strong"]:
            return True
        style = child.get("style","").replace(" ","")
        if "font-weight:bold" in style or any(f"font-weight:{w}" in style for w in ["600","700","800","900"]):
            return True
    return False

def looks_like_sentence(line:str)->bool:
    if not line:
        return False
    words= line.split(' ')
    if not words:
        return False
    lower_words = sum(
        1
        for w in words 
        if w and (
            w.islower() or 
            (len(w)>1 and w[0].isupper() and w[1].islower())
        )
    )
    lower_ratio = lower_words/len(words)
    if lower_ratio> 0.7 and len(words)>6:
        return True
    if line.endswith((".",";",":")) and len(words)>5:
        return True
    return False

def get_paragraphs(text:str)->list:
    cleaned_up_paragraphs = []
    if not text:
        return []
    
    paragraphs= text.split('\n\n')
    for p in paragraphs:
        if not p:
            continue
        if len(p)>100 and looks_like_sentence(p):
            cleaned_up_paragraphs.append(p)
    return '\n'.join(cleaned_up_paragraphs)
SECTION_PATTERNS = {
    "meeting": [
        r"^notice of annual meeting",
        r"^notice of special meeting",
        r"^annual meeting of shareholders",
        r"^annual meeting of stockholders",
        r"^general information about the meeting",
        r"^questions and answers about the meeting",
        r"^proxy summary",
    ],
    "proposals": [
        r"^proposal\s+\d+",
        r"^matters to be voted on",
        r"^items of business",
        r"^election of directors",
        r"^ratification of.*auditor",
        r"^advisory vote.*executive compensation",
        r"^say-on-pay",
        r"^say-on-frequency"
    ],
    "directors": [
        r"^board of directors",
        r"^director nominees?",
        r"^nominees for director",
        r"^election of directors",
        r"^corporate governance"
    ],
    "executive_compensation": [
        r"^executive compensation",
        r"^compensation discussion and analysis",
        r"^cd&a",
        r"^compensation committee report",
        r"^pay versus performance"
    ],
    "ownership": [
        r"^security ownership",
        r"^beneficial ownership",
        r"^principal shareholders",
        r"^ownership of common stock"
    ],
    "auditor": [
        r"^ratification of.*auditor",
        r"^independent registered public accounting firm",
        r"^audit committee report",
        r"^auditor fees",
        r"^principal accountant fees"
    ],
    "related_party_transactions": [
        r"^related party transactions",
        r"^certain relationships and related transactions",
        r"^transactions with related persons",
        r"^review, approval, or ratification of related party transactions"
    ],
    "risk_oversight": [
        r"^risk oversight",
        r"^board leadership structure",
        r"^board'?s role in risk oversight"
    ]
    }



def generic_trim_document(
        text:str,
        ticker:str,
        report_type:str,
        report_date:str,
        company:str
)->json:

    
    if not text or not ticker or not report_type or not report_date or not company:
        raise ValueError("empty value received. check text, ticker, report_type, report_date, company are passed.")

    NON_NARRATIVE_TYPES = (
    'GRAPHIC',
    'XML',
    'JSON',
    'ZIP',
    'EX-101',
    'EX-104',
    'EX-31',
    'EX-32',
    'PDF'
    )
    NAMESPACE_PREFIX = ("ix:","xbrli:","dei:","us-gaap:","xbrldi:")
    DELETABLE_TAGS = ["b","s","strike","del","noscript","svg","image","meta","link"]
    TABLE_BLOCK_DICT = {}
    table_idx=0
    soup = BeautifulSoup(text,"lxml")
    documents = soup.find_all("document")
    text_out=""
    for doc in documents:   
        
        # start by skipping non narrative document types  
        try:
            type_tag = doc.find("type")
            section_type = type_tag.get_text(" ",strip=True) if type_tag else ""
            if section_type.startswith(NON_NARRATIVE_TYPES):
                continue
        except:
            print("no section type. assigning empty")
            continue
        if doc.pdf:
            continue
        # normalize style: none and style:none and other variants
        for div in doc.find_all("div"):
            if div is not None and div.attrs is not None:
                style = div.get("style","")
                style_normalized = style.lower().replace(" ","")
                if "display:none" in style_normalized:
                    div.decompose()
                    continue
            else:
                continue
        for tag in doc.find_all(lambda t: t.name and t.name.startswith(NAMESPACE_PREFIX)):
            tag.unwrap()
        for tag in doc.find_all(DELETABLE_TAGS):
            tag.decompose()
        for tag in doc.find_all("a"):
            if tag is not None and tag.attrs is not None:
                txt = tag.get_text(" ",strip=True)
                if not txt or txt in {"back to top","top","#toc"}:
                    tag.decompose()
            else:
                continue
        for i,table in enumerate(doc.find_all("table")):
            table_text=table.get_text(separator=" | ",strip=True)
            # check for foot notes
            separator_count = len(table_text.split('|'))-1
            if separator_count==1:
                table.replace_with(f"\n\n[FOOT NOTE START] {table_text} [FOOT NOTE END]\n\n")
            elif separator_count>1:
                TABLE_BLOCK_DICT[f"TABLE_{table_idx}"]=table_text
                table.replace_with(f" TABLE_{table_idx} ")
                table_idx+=1
                continue
            else:
                continue
        text_out = text_out+ doc.get_text("\n",strip=True)

    text_normalized = normalize_text(text_out,remove_tables=True)
    cleaned_paragraphs = get_paragraphs(text_normalized)

    return cleaned_paragraphs.strip()

def section_processor(text:str)->json:
    """
    this function will receive a text and extract the sections to form a json object with specific data ready for analyisis
    """


    
# summarize the sections chunks into one per section
def sections_summarizer(chunks:list)->str:
    """
    this function will summarize the chunks of a report. this can be used for any tipe of report, 8k, 10k, 14def etc.
    params:
        sections: list of summarized chunks
    returns:
        string of the final report summarized
    """
    if not chunks:
        return chunks
    if len(chunks)==1:
        return chunks[0]
    combined_message = "\n\n--- PARTIAL SUMMARY ---\n\n".join(chunks)
    
    for attempt in range(2):
        try:
            response = llm.invoke([
                SystemMessage(content=sections_summarizer_instructions),
                HumanMessage(content=combined_message)
            ])
            if response.content is None:
                raise ValueError("llm did not return any content")
            break
            
        except:
            if attempt ==1:
                raise
        
    return response.content
#  summarize the sections into one per report
def types_synthetiser(summaries_all_types:list)->str:
    for attempt in range(2):
        try:
            response = llm.invoke(
                [
                    SystemMessage(content=types_synthetiser_instructions),
                    HumanMessage(
                        content=f"""
                            Below is a list of summarized sections that all belong to the same SEC filing.
                            Generate one final consolidated summary for the report.
                            Input:
                            {summaries_all_types}
                            Output:
                            Return a single paragraph or short multi-paragraph executive summary
                            that represents the entire report.
                            """
                                )
                ]
            )
            if response.content is None:
                raise ValueError("llm did not return any content")
            break
        except:
            if attempt==1:
                raise
    return response.content
# use for testing summarization levels
def save_file_test(file_name:str,dict_obj,file_mode:str):
    """
    use for saving json and testing summarization levels.
    """
    with open(file_name,file_mode) as f:
        f.write(json.dumps(dict_obj,indent=4))
        f.close()

#=================================#
#   quant logic helpers           #
#=================================#

form_types = ['10-K', '10-Q', '8-K', 'DEF 14A','20-F','6-K'] 

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

def quant_report(summaries:list)->object:

    for attempt in range(2):
        try:
            response =llm.invoke(
                [
                    SystemMessage(content=quant_instructions),
                    HumanMessage(content=f"""summaries: {summaries}""")
                ]
            )
            if response.content is None:
                raise ValueError("llm did not return any content")
            break
        except:
            if attempt==1:
                raise
    return response.content

#=================================#
#   rittenhouse logic helpers     #
#=================================#

# provide final summary
def synthetize_summaries(summaries:list,instructions)->list:
    """
    function to synthetize summaries and provide a final summary ready for pdf conversion.
    
    :param summaries: 
    :type summaries: list
    :param instructions: Description
    :return: llm response in structured output for pdf (title, content, bullets)
    :rtype: list
    """
    response = llm.invoke(
        [
            SystemMessage(content=instructions),
            HumanMessage(content=f"here is the report: {summaries}")
        ]
    )
    return response.content if response.content else None

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
def chunk_report(report:str)->list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=60000,
        chunk_overlap=300,
        separators=["\n\n","\n","."," "]
    )
    return splitter.split_text(report)

def process_sec_chunks_ritten(report:str,instructions:str)->list:
    """
    function to chunk a long text and summarize it. it will return a list of chunks.
    
    :param report: Description
    :type report: str
    :param instructions: Description
    :type instructions: str
    :return: list of summarized chunks
    :rtype: list
    """
    dict_chunks = chunk_report(report)
    structured_llm=llm.with_structured_output(Chunk)
    responses=[]
    idx = 0
    for i in dict_chunks:
        response = structured_llm.invoke(
            [
                SystemMessage(content=instructions),
                HumanMessage(content=i)
            ]
        )
        responses.append({"chunk_index":idx,
                        "chunk":response.chunk})
        idx+=1
        print("response chunk idx: ",idx)
    return responses

if __name__ =='__main__':
    print("hello from main")