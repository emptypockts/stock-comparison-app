from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,SystemMessage
import json
from datetime import datetime
from prompts import seven_powers_instructions,json_validator_instructions
from outils import (
    clean_edgar_text, 
    analyze_ticker,
    save_analysis_report,
    json_validator,
    llm
)
load_dotenv()

import os
DIRECTORY=os.getenv('DIRECTORY')
def seven_powers(tickers)->str:
    response = llm.invoke(
        [
            SystemMessage(content=seven_powers_instructions),
            HumanMessage(content=f"ticker symbol: {tickers}")
        ]
    )
    if response.content:
        validated_json=json.loads(response.content.replace("```json","").replace("```","").strip().lower())
        return validated_json
    else:
        raise Exception(f"response has no content. see details: {response}")
        return {}


if __name__ == "__main__":
    ticker='pltr'
    user_query=['eric']
    response = seven_powers(user_query)
    print(response)