
from dotenv import load_dotenv
import os
from google.generativeai import configure,GenerativeModel
load_dotenv()
API_KEY = os.getenv('GEMINI_API')
configure(api_key=API_KEY)
model = GenerativeModel('gemini-1.5-flash')

def chatQuery(query):
    response = model.generate_content(query)
    return response


if __name__ == "__main__":
    ticker='pltr'
    user_query=f"You are a financial expert that will conduct the 7power analysis framewrok from Hamilton Helmer about the company with ticker {ticker}. Layout each of the 7 powers and your conclusion of each. Include any URL for reference."
    response = model.generate_content(user_query)
    print(response.text)