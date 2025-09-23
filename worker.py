from celery import Celery
import socketio
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
uri = os.getenv('MONGODB_URI')
WS_SOCKET_URI=os.getenv('VITE_WS_SERVER')

celery = Celery(
    'ai_reports',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

sio = socketio.Client()


@celery.task(bind=True)
def generate_ai_report(self,tickers,user_id):
    
    from aiReport import compile
    try:
        if not user_id:
            raise ValueError("missing user_id")
        result= compile(tickers)
        task_id = self.request.id

        if result:
            client = MongoClient(uri, server_api=ServerApi('1'))
            db = client["test"]
            ai_report_collections = db["aiTasks"]
            ai_report_collections.insert_one({
            "user_id":user_id,
            "task_id":task_id,
            "assistant":result
            })


        try:
            print('notifying server of completion')
            if not sio.connected:      
                sio.connect(
                    WS_SOCKET_URI,
                    )
            sio.emit('task_done',{
                'user_id':user_id,
                'task_id':task_id,
                'tickers':tickers
            },namespace='/')
            print('emit done')
        except Exception as e:
            print('ws issue',str(e))
        return result
    except Exception as e:
        print('error with task execution',str(e))
        return str(e)

@celery.task(bind=True)
def generate_ai_7powers(self,tickers,user_id):
    from geminiChat import seven_powers
    try:
        if not user_id:
            raise ValueError("missing user_id")
        result= seven_powers(tickers)
        task_id=self.request.id
        if result:
            client = MongoClient(uri, server_api=ServerApi('1'))
            db = client["test"]
            ai_report_collections = db["aiTasks"]
            ai_report_collections.insert_one({
                "user_id":user_id,
                "task_id":task_id,
                "assistant":result
            })
            try:
                print("notifying server of completion")
                if not sio.connected:
                    sio.connect(
                        WS_SOCKET_URI
                    )
                sio.emit('task done',{
                    "user_id":user_id,
                    "task_id":task_id,
                    "tickers":tickers
                },namespace='/')
                print("emit done")
            except Exception as e:
                print("error trying to notify task completion: ", str(e))
            return result
    except Exception as e:
        print("error executing task: ",str(e))
        return str(e)
       
         

