from pymongo import MongoClient
import certifi
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import requests
import jwt
from app_constants import MONGODB_URI, CF_CERT_URL
import certifi

def loginStep(username):
    load_dotenv()
    
    client = MongoClient(MONGODB_URI)


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
    
    CERT_KYS = requests.get(CF_CERT_URL).json()

    client = MongoClient(MONGODB_URI)

    
    # try:
    #     client.admin.command('ping')
    #     print("Pinged your deployment. You successfully connected to MongoDB!")

    # except Exception as e:
    #     print(e)
    token = request.headers.get("Cf-Access-Jwt-Assertion") or request.cookies.get("CF_Authorization")    
    print(token)
