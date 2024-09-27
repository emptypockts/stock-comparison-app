from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

def loginStep(username):
    load_dotenv()
    uri = os.getenv('MONGODB_URI')
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Access the 'users' collection in the database
    db = client["test"]
    users_collection = db["User"]
    # Check if user exists in the database
    user = users_collection.find_one({"username": username})
    return user


if __name__ == "__main__":
    load_dotenv()
    uri = os.getenv('MONGODB_URI')
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")

    except Exception as e:
        print(e)