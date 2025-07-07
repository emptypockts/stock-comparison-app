from celery import Celery
import socketio
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["test"]
socket_io=socketio.Client()

celery = Celery(
    'ai_reports',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@socket_io.event
def connect():
     print('connected to ws server')
@socket_io.event
def disconnect():
     print('disconnected from ws server')

@celery.task(bind=True)
def generate_ai_report(self,tickers,user_id):
    from aiReport import compile
    try:
        result= compile(tickers)
        task_id = self.request.id
        if result:
            
            stock_collection = db["aiTasks"]
            stock_collection.insert_one({
            "user_id":user_id,
            "task_id":task_id,
            "assistant":result
            })
        
                
        try:
            socket_io.connect("http://localhost:5009")
            socket_io.emit('task_done',{
            'user_id':user_id,
            'assistant':result
            })
            socket_io.disconnect()
        except Exception as e:
            print('ws issue',str(e))
        return result
    except Exception as e:
        print('error with task execution',str(e))
        return str(e)


    
         

