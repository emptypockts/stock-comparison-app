
from pymongo import MongoClient
from pymongo.collection import Collection
from financialUtils import fetch_ticker,fetch_cik
from app_constants import MONGODB_URI
import json

def createCikTickerCollection(file: str, collection: Collection) -> None:
    """
    Extracts the CIK Ticker data and stores it in a MongoDB Collection.
    Args:
        file: str
        collection : Collection
    Returns:
        None 
    """

    # {'cik_str': 1045810, 'ticker': 'NVDA', 'title': 'NVIDIA CORP'}
    with open(file) as f:
        json_obj = json.load(f)
    ciks =[]
    for _, v in json_obj.items():
        ciks.append(
            {
                'cik_str': v['cik_str'],
                'title': v['title'],
                'ticker': v['ticker'],
            }
        )

    with open('/Users/jjmr86/coding/cik_adjusted.json','w') as w:
        json.dump(ciks, w, ensure_ascii=False, indent=4)   
    #inject the object in the database
    collection.insert_many(ciks)
    print("jsonData inserted successfully")





    
if __name__ == "__main__":
    # client = MongoClient(uri, server_api=ServerApi('1'),tls=True,tlsCaFile=certifi.where())
    client = MongoClient(MONGODB_URI)

    db = client["test"]
    collection=db['tickerCIK']
    file= "/Users/jjmr86/coding/cik.json"
    createCikTickerCollection(file,collection)

    print(fetch_cik('rost',collection))
    file=['CIK000019617.json','CIK0000002098.json']
    ciks=[int(e[:-5].lstrip("CIK").lstrip("0"))for e in file]
    print(fetch_ticker(ciks,collection))