
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from financialUtils import fetch_ticker,fetch_cik
import os
import json
load_dotenv()
uri = os.getenv('MONGODB_URI')



def createCikTickerCollection(file,collection):
    with open(file) as f:
        document = f.read()
    jsonObj = json.loads(document)
    documents=[jsonObj[str(index)] for index,item in enumerate(jsonObj)]     
    #inject the object in the database
    collection.insert_many(documents)
    print("jsonData inserted successfully")





    
if __name__ == "__main__":
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["test"]
    collection=db['tickerCIK']
    # file= "C:\\Users\\ejujo\\Downloads\\tickers.json"
    # updateCIKTicker(file,collection)
    print(fetch_cik('rost',collection))
    file='CIK000019617.json'
    cik_integer= int(file[:-5].lstrip("CIK").lstrip("0"))
    print(fetch_ticker(cik_integer,collection))