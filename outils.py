from bs4 import BeautifulSoup
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
    recursive_summarize_instructions
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

# level 1, structure report and chunk text


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
# etl with soup on sec report
def extract_sections (text:str,file:str)->list:
    """
    this function will process a sec report text file and extracts the important sections and provide structure.
    params:
        text: str that contains the sec report
        file: str that states the type of report
        returns: a list of summarized chunks
    """
    sections = []
    SEC_DOC_TYPE_DESCRIPTIONS = {

    # Core filing
    "8-K": "Form 8-K Current Report. Discloses material corporate events such as earnings releases, mergers, acquisitions, executive changes, or other significant developments.",

    # Common earnings / investor exhibits
    "EX-99.1": "Exhibit 99.1. Typically an earnings press release or investor-facing announcement included with the filing.",
    "EX-99.2": "Exhibit 99.2. Supplemental investor materials such as presentations, schedules, or supporting financial information.",
    "EX-99.3": "Exhibit 99.3. Additional supplemental materials such as financial tables, investor presentations, or explanatory schedules.",

    # Certification exhibits (common in 10-K / 10-Q)
    "EX-31.1": "Section 302 certification by the Chief Executive Officer confirming the accuracy of the report and effectiveness of disclosure controls.",
    "EX-31.2": "Section 302 certification by the Chief Financial Officer confirming the accuracy of the report and effectiveness of disclosure controls.",

    "EX-32.1": "Section 906 certification by the Chief Executive Officer stating the report fully complies with the Securities Exchange Act.",
    "EX-32.2": "Section 906 certification by the Chief Financial Officer stating the report fully complies with the Securities Exchange Act.",

    # Legal / governance exhibits
    "EX-10": "Material contract exhibit such as employment agreements, credit agreements, partnership agreements, or other legally significant contracts.",
    "EX-3.1": "Articles of incorporation or charter documents describing the company's legal formation.",
    "EX-3.2": "Bylaws of the company defining governance rules and procedures.",
    "EX-21": "List of subsidiaries of the registrant.",
    "EX-23": "Consent of independent registered public accounting firm.",
    "EX-24": "Power of attorney authorizing individuals to sign filings on behalf of officers or directors.",

    # XBRL exhibits (machine-readable financial metadata)
    "EX-101.INS": "XBRL instance document containing the machine-readable financial statement data.",
    "EX-101.SCH": "XBRL schema file defining financial reporting elements, data types, and relationships. Not narrative text.",
    "EX-101.CAL": "XBRL calculation linkbase defining mathematical relationships between financial statement elements.",
    "EX-101.DEF": "XBRL definition linkbase defining dimensional relationships such as axes, domains, and members. Not narrative text.",
    "EX-101.LAB": "XBRL label linkbase providing human-readable labels for financial elements.",
    "EX-101.PRE": "XBRL presentation linkbase defining the ordering and hierarchy of financial statements.",

    # Inline XBRL (modern filings)
    "EX-104": "Inline XBRL exhibit containing embedded machine-readable financial data within the HTML filing."
    }
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
    for doc in documents:    
        # start by skipping non narrative document types
        
        try:
            section_type = (doc.type.next).strip()
            if section_type.startswith(NON_NARRATIVE_TYPES):
                print(f"----removing non narrative documents----\n{section_type}")
                continue
        except:
            print("no section type. assigning empty")
            continue

            #   skipping pdf
            #   removing none style divs
            #   namespaces ix, xbrli, dei and us-gaap
            #   deletable tags
            #   anchor/links noise
        

        if doc.pdf:
            continue
        # normalize style: none and style:none and other variants
        for div in doc.find_all("div"):
            style = div.get("style","")
            normalized = style.lower().replace(" ","")
            if "display:none" in normalized:
                div.decompose()
        for tag in doc.find_all(lambda t: t.name and t.name.startswith(NAMESPACE_PREFIX)):
            tag.unwrap()
        for tag in doc.find_all(DELETABLE_TAGS):
            tag.unwrap()
        for tag in doc.find_all("a"):
            txt = tag.get_text(" ",strip=True)
            href = tag.get("href","")
            if not txt or txt in {"back to top","top"}:
                tag.decompose()
        for i,table in enumerate(doc.find_all("table")):
            table_text=table.get_text(separator=" | ",strip=True)
            # check for foot notes
            separator_count = len(table_text.split('|'))-1
            if separator_count==1:
                table.replace_with(f"\n[FOOT NOTE START]\n{table_text}\n[FOOT NOTE END]\n")
            elif separator_count==0:
                continue
            else:
                TABLE_BLOCK_DICT[f"TABLE_{table_idx}"]=table_text
                table.replace_with(f" TABLE_{table_idx} ")
                table_idx+=1
        print(f"----------------calling for recusrive chunk--------")
        texts = [replace_smart_punctuation(t) for t in recursively_chunk(doc.text,TABLE_BLOCK_DICT)]
        if not texts:
            continue
            
        type_description=""
        for k,v in SEC_DOC_TYPE_DESCRIPTIONS.items():
            if section_type.startswith(k):
                type_description=v
                break
        sections.append(
            {
                "file_name":file,
                "id":str(uuid.uuid4()),
                "section_type":section_type,
                "type_description":type_description,
                "text":texts,
                "texts_synthesis":process_sec_chunks(texts)
            }
        )
    return sections
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
                    HumanMessage(content=replace_smart_punctuation(combined_content))
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
# process unicode character
def replace_smart_punctuation(text: str) -> str:
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
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'\s+', ' ', text).strip()
    text = ' '.join(text.split())
    return text
# recursive langchain chunker
def recursively_chunk(text: str,tables:dict) -> list:
    """
    function to recursively chunk and add back the tables after the chunk is completed
    params:
        text: string of the sec report
        tables: list of tables
    returns: list of chunks
    """
    if len(text)<3000:
        return [restore_tables(text,tables)]
    else:
        overlap=200
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name='cl100k_base',
        chunk_size=10000,
        chunk_overlap=overlap,
    )
    text = replace_smart_punctuation(text)
    texts= text_splitter.split_text(text)
    texts_w_tables = [restore_tables(t,tables) for t in texts]
    return texts_w_tables
    
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