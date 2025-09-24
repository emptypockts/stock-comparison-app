import requests
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()


def getEconomicIndex(indexID):
    today = datetime.today().strftime('%Y-%m-%d')
    fifty_years_back = (datetime.today() - timedelta(days=50 * 365)).strftime('%Y-%m-%d')
    API_KEY = os.getenv('FRED_API')
    url = "https://api.stlouisfed.org/fred/series/observations"
    querystring = {"series_id":indexID,
                "api_key":API_KEY,
                "file_type":"json",
                "observation_start":fifty_years_back,
                "observation_end":today,
                "sort_order":"asc",
                }
    try:
        response = requests.request("GET", url, params=querystring)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json().get('observations', [])

        # Process the JSON data directly
        processed_data = [
            {
                'date': item['date'],
                'value': float(item['value']) if item['value'] not in ['.', None] else None
            }
            for item in data
        ]

        # Filter out entries with None values if needed
        processed_data = [item for item in processed_data if item['value'] is not None]

        return processed_data
    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    indexList= ["STLFSI4","SP500","HOUST1F","UNRATE","SOFR","DCOILWTICO","U6RATE"]
    for myIndex in indexList:
        print(f"index data for index:{myIndex} \n{getEconomicIndex(myIndex)}")

