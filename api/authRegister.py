from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os
from pymongo.server_api import ServerApi
from datetime import datetime, timezone
import bcrypt
import re  # For email validation

def registerStep(username, password, name, email):
    current_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
    load_dotenv()
    uri = os.getenv('MONGODB_URI')
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client["test"]
    users_collection = db["User"]

    try:
        # Validate email format using regex
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            return {"success": False, "message": "Invalid email format."}

        # Check if the username or email already exists in the database
        if users_collection.find_one({"username": username}):
            return {"success": False, "message": "Username already exists."}

        if users_collection.find_one({"email": email}):
            return {"success": False, "message": "Email already exists."}

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new user
        users_collection.insert_one({
            "email": email,
            "password": hashed_password.decode('utf-8'),  # Store as a string
            "name": name,
            "username": username,
            "createdAt": current_time,
            "updatedAt": current_time
        })

        return {"success": True, "message": "User created successfully."}

    except errors.DuplicateKeyError:
        return {"success": False, "message": "User already exists."}
    
    except Exception as e:
        return {"success": False, "message": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    load_dotenv()
    uri = os.getenv('MONGODB_URI')
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        # Testing user registration
        result = registerStep(username='ChandraP', password='ChandraP', name='Chandra', email='ChandraP@eric.com')
        print(result)

    except Exception as e:
        print(e)
