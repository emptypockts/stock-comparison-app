
from dotenv import load_dotenv
import os
import requests
from aiReport import get_json_validator,validate_json
import json
load_dotenv()
API_KEY = os.getenv('GEMINI_API')

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
querystring = {"key":API_KEY}

def seven_powers(tickers)->str:
    agent = """
    You are a financial expert applying the 7 Powers framework by Hamilton Helmer to companies based on the provided ticker array.

    Generate a concise and insightful report for each power, backed by recent data and clearly cited URLs. Mention the date of the data wherever possible.

    ✅ The output MUST be a **pure JSON array** (no wrapper object, no "report" field, etc.), where each element matches **exactly one** of the following formats:

    1. { "type": "title", "content": "string" }
    2. { "type": "paragraph", "content": "string" }
    3. { "type": "bullets", "content": ["bullet1", "bullet2", ..., "bulletn"] }

    Do NOT include any outer object like `{ "report": [...] }`. Only return the array.

    Ensure the JSON is valid and ready for parsing.
    """
    payload = {
    "system_instruction": {"parts": [{"text": agent}]},
    "contents": [
        {
            "parts": [
                {"text": ' '.join(tickers)}
            ]
        }
    ],
    }
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    response =response.json()
    r1 = response["candidates"][0]["content"]["parts"][0]["text"]
    #validate json object
    json_validator_agent=get_json_validator()
    r2 = validate_json(json_validator_agent,r1.replace("```","").replace("json","").strip().lower())
    r3=json.loads(r2.replace("```json","").replace("```","").strip().lower())
    return r3

if __name__ == "__main__":
    ticker='pltr'
    user_query=['pltr','axp']
    response = seven_powers(user_query)
    print(response)