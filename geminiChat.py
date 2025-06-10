
from dotenv import load_dotenv
import os
import requests
load_dotenv()
API_KEY = os.getenv('GEMINI_API')

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
querystring = {"key":API_KEY}

def chatQuery(query)->str:
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
                {"text": ' '.join(query)}
            ]
        }
    ],
    }
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    response =response.json()
    print ("API Response ",response["candidates"][0]["content"]["parts"][0]["text"])
    return response["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == "__main__":
    ticker='pltr'
    user_query=['pltr','axp']
    response = chatQuery(user_query)
    print(response)