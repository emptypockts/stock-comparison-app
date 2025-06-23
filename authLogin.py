from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import requests
import jwt

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
    # load_dotenv()
    from flask import Flask,request
    app = Flask(__name__)
    CF_CERT_URL = f"https://{os.getenv('CF_URL_CDN_CGI_CERTS')}/cdn-cgi/access/certs"
    CERT_KYS = requests.get(CF_CERT_URL).json()
    CF_AUDIENCE_ID = os.getenv('CF_AUD_ID')

    # uri = os.getenv('MONGODB_URI')
    # client = MongoClient(uri, server_api=ServerApi('1'))
    
    # try:
    #     client.admin.command('ping')
    #     print("Pinged your deployment. You successfully connected to MongoDB!")

    # except Exception as e:
    #     print(e)
    token = request.headers.get("Cf-Access-Jwt-Assertion") or request.cookies.get("CF_Authorization")    
    print(token)
