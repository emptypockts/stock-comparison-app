
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import json
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["test"]


def upatedB(db,file,collection='tickerCIK'):
    load_dotenv()
    with open(file) as f:
        document = f.read()
    jsonObj = json.loads(document)
    documents=[jsonObj[str(index)] for index,item in enumerate(jsonObj)]     
    stock_collection = db[collection]
    #inject the object in the database
    stock_collection.insert_many(documents)
    print("jsonData inserted successfully")

def fetch_cik(db,ticker,collection='tickerCIK'):
    filter={
        'ticker':ticker.upper()
    }
    project={
    'cik_str': 1, 
    '_id': 0
    }
    
    tickerCIK_Collection = db[collection]
    cik=tickerCIK_Collection.find_one(
        filter=filter,
        projection=project
    )
    return cik['cik_str'] 

    
if __name__ == "__main__":
    collection='tickerCIK'
    # file= "C:\\Users\\ejujo\\Downloads\\tickers.json"
    # updateCIKTicker(file,collection)
    print(fetch_cik('rost'))