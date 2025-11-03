
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,SystemMessage
from prompts import quant_instructions,synthesis_prompt
from outils import clean_edgar_text
from pymongo.server_api import ServerApi
from pymongo import MongoClient, errors,UpdateOne
from pymongo.collection import Collection
load_dotenv()

import os
GEMINI_API=os.getenv('GEMINI_API')


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=GEMINI_API)
# llm=ChatOllama(model="llama3.2:latest")

def quant(ticker:str,collection:object)->str:
    """
    quant analyzes a ticker 10K, 10Q, 8K, DEF 14A reports and identify red flags and opportunities
    args:
        ticker of the company
        collection object for MongoDB
    returns:
        str report
    """
    submitted_reports={}
    files = os.listdir(f"sec_filings/{ticker}")
    for file in files:
        if "json" in file:
            pass
        else:
            with open(f"sec_filings/{ticker}/{file}") as f:
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

    return  final_response.content

if __name__=="__main__":
    print(quant("Mu"))
