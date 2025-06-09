
from dotenv import load_dotenv
import os
import requests
load_dotenv()
API_KEY = os.getenv('GEMINI_API')

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
querystring = {"key":API_KEY}

def chatQuery(query):

    payload = {"contents": [{"parts": [{"text": query}]}]}
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    response =response.json()
    print ("API Response ",response["candidates"][0]["content"]["parts"][0]["text"])
    return response["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == "__main__":
    ticker='pltr'
    user_query=f"You are a financial expert that will conduct the 7power analysis framewrok from Hamilton Helmer about the company with ticker {ticker}. Layout each of the 7 powers and your conclusion of each. Include any URL for reference."
    response = chatQuery(user_query)
    print(response)