from celery import Celery
import socketio
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime,timezone
from celery.exceptions import Ignore


load_dotenv()
uri = os.getenv('MONGODB_URI')
WS_SOCKET_URI=os.getenv('VITE_WS_SERVER')
sio = socketio.Client()
celery = Celery(
    'ai_reports',
    broker=os.getenv('REDIS_SERVER'),
    backend=os.getenv('REDIS_SERVER')
)

def notify_task_result(event_name,payload):
    if not sio.connected:
        sio.connect(WS_SOCKET_URI)
    try:
        sio.emit(event_name,payload,namespace='/')
        sio.sleep(0)
    except Exception as e:
        print(f"error trying to connect to the ws socket {sio} error {str(e)}")

def connect_to_ws_server():
    sio.connect(WS_SOCKET_URI)

# ==============overal financials==============
@celery.task(bind=True)
def generate_ai_report(self,tickers,user_id,report_type):
    
    from aiReport import compile
    
    try:
        if not user_id:
            raise Ignore()
        task_id = self.request.id
        result= compile(tickers)

        if result:
            client = MongoClient(uri, server_api=ServerApi('1'))
            db = client["test"]
            ai_report_collections = db["aiTasks"]
            ai_report_collections.insert_one({
            "user_id":user_id,
            "task_id":task_id,
            "assistant":result,
            "report_type":report_type,
            "tickers":tickers,
            "timestamp": datetime.now(timezone.utc)

            })


            
            print('notifying server of completion')
            notify_task_result('task_done',{
                'user_id':user_id,
                'task_id':task_id,
                'tickers':tickers,
                'report_type':report_type,
                "tickers":tickers,
                "timestamp":datetime.now().isoformat()+"Z"

            })
            return result

    except Exception as e:
        print(f"error with task execution {str(e)} for tickers {tickers}, task id {task_id}")
        notify_task_result("task_failed", {
            "user_id": user_id,
            "task_id": task_id,
            "tickers": tickers,
            "report_type": report_type,
            "timestamp": datetime.now().isoformat() + "Z",
            "error": str(e)
        })
        
        raise self.retry(exc=e,countdown=5,max_retries=1)
    
    # ============7powers===============

@celery.task(bind=True)
def generate_ai_7powers(self,tickers,user_id,report_type):
    from sevenPowers import seven_powers
    try:
        if not user_id:
            raise Ignore()
        task_id=self.request.id
        result= seven_powers(tickers)
        
        now=datetime.now()
        if result:
            client = MongoClient(uri, server_api=ServerApi('1'))
            db = client["test"]
            ai_report_collections = db["aiTasks"]
            ai_report_collections.insert_one({
                "user_id":user_id,
                "task_id":task_id,
                "assistant":result,
                "report_type":report_type,
                "tickers":tickers,
                "timestamp":datetime.now(timezone.utc)
            })
            
            print("notifying server of completion")
            notify_task_result('task_done',{
            'user_id':user_id,
            'task_id':task_id,
            'tickers':tickers,
            'report_type':report_type,
            "tickers":tickers,
            "timestamp":datetime.now().isoformat()+"Z"
            })
            
            return result

            
    except Exception as e:
        print(f"error with task execution {str(e)} for tickers {tickers}, task id {task_id}")
        notify_task_result("task_failed", {
            "user_id": user_id,
            "task_id": task_id,
            "tickers": tickers,
            "report_type": report_type,
            "timestamp": datetime.now().isoformat() + "Z",
            "error": str(e)
        })
        
        raise self.retry(exc=e,countdown=5,max_retries=1)
    
    # ========quant============
       
@celery.task(bind=True)
def generate_ai_quant(self,tickers,user_id,report_type):
    current_year=(datetime.now().year)
    from quant import quant
    try:
        if not user_id:
            raise Ignore()
        task_id=self.request.id
        result=quant(str(current_year),tickers)
        
        now=datetime.now()
        if result:
            client = MongoClient(uri, server_api=ServerApi('1'))
            db = client["test"]
            ai_report_collections = db["aiTasks"]
            ai_report_collections.insert_one({
                "user_id":user_id,
                "task_id":task_id,
                "assistant":result,
                "report_type":report_type,
                "tickers":tickers,
                "timestamp":datetime.now(timezone.utc)
            })
        
            print("notifying server of completion")
            notify_task_result('task_done',{
            'user_id':user_id,
            'task_id':task_id,
            'tickers':tickers,
            'report_type':report_type,
            "tickers":tickers,
            "timestamp":datetime.now().isoformat()+"Z"
            })
            
            return result

    except Exception as e:
         
        print(f"error with task execution {str(e)} for tickers {tickers}, task id {task_id}")
        notify_task_result("task_failed", {
            "user_id": user_id,
            "task_id": task_id,
            "tickers": tickers,
            "report_type": report_type,
            "timestamp": datetime.now().isoformat() + "Z",
            "error": str(e)
        })
        
        raise self.retry(exc=e,countdown=5,max_retries=1)
    
@celery.task(bind=True)
def generate_ai_quant_rittenhouse(self,tickers,user_id,report_type):
    current_year=(datetime.now().year)
    from rittenhouse import quant_rittenhouse
    try:
        if not user_id:
            raise Ignore()
        task_id=self.request.id
        result=quant_rittenhouse(str(current_year),tickers)
        
        now=datetime.now()
        if result:
            client = MongoClient(uri, server_api=ServerApi('1'))
            db = client["test"]
            ai_report_collections = db["aiTasks"]
            ai_report_collections.insert_one({
                "user_id":user_id,
                "task_id":task_id,
                "assistant":result,
                "report_type":report_type,
                "tickers":tickers,
                "timestamp":datetime.now(timezone.utc)
            })
        
            print("notifying server of completion")
            notify_task_result('task_done',{
            'user_id':user_id,
            'task_id':task_id,
            'tickers':tickers,
            'report_type':report_type,
            "tickers":tickers,
            "timestamp":datetime.now().isoformat()+"Z"
            })
            
            return result

    except Exception as e:
         
        print(f"error with task execution {str(e)} for tickers {tickers}, task id {task_id}")
        notify_task_result("task_failed", {
            "user_id": user_id,
            "task_id": task_id,
            "tickers": tickers,
            "report_type": report_type,
            "timestamp": datetime.now().isoformat() + "Z",
            "error": str(e)
        })
        
        raise self.retry(exc=e,countdown=5,max_retries=1)
