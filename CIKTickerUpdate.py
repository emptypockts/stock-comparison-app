
from pymongo import MongoClient
import certifi
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from financialUtils import fetch_ticker,fetch_cik
import os
import json
load_dotenv()
uri = os.getenv('MONGODB_URI')



def createCikTickerCollection(file,collection):
    import json

    json_obj = json.loads(file)
    data = json_obj['data']
    ciks =[]
    for d in data:
        ciks.append(
            {
                'cik_str':d[0],
                'title':d[1],
                'ticker':d[2],
                'exchange':d[3]

            }
        )

    with open('/Users/jjmr86/coding/cik_adjusted.json','w') as w:
        json.dump(ciks, w, ensure_ascii=False, indent=4)   
    #inject the object in the database
    collection.insert_many(ciks)
    print("jsonData inserted successfully")





    
if __name__ == "__main__":
    client = MongoClient(uri, server_api=ServerApi('1'),tls=True,tlsCaFile=certifi.where())
    db = client["test"]
    collection=db['tickerCIK']
    file= "/Users/jjmr86/coding/cik.json"
    createCikTickerCollection(file,collection)

    print(fetch_cik('rost',collection))
    file=['CIK000019617.json','CIK0000002098.json']
    ciks=[int(e[:-5].lstrip("CIK").lstrip("0"))for e in file]
    print(fetch_ticker(ciks,collection))