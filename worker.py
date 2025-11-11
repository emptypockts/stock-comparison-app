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

def notify_task_done(event_name,payload):
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


        try:
            print('notifying server of completion')
            notify_task_done('task_done',{
                'user_id':user_id,
                'task_id':task_id,
                'tickers':tickers,
                'report_type':report_type,
                "tickers":tickers,
                "timestamp":datetime.now().isoformat()+"Z"

            })
            print(f"task {task_id} completed emitting task_done")
        except Exception as e:
            print('ws issue',str(e))
        return result
    except Exception as e:
        print('error with task execution',str(e))
        return str(e)
    
    # ============7powers===============

@celery.task(bind=True)
def generate_ai_7powers(self,tickers,user_id,report_type):
    from geminiChat import seven_powers
    try:
        if not user_id:
            raise Ignore()
        result= seven_powers(tickers)
        task_id=self.request.id
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
            try:
                print("notifying server of completion")
                notify_task_done('task_done',{
                'user_id':user_id,
                'task_id':task_id,
                'tickers':tickers,
                'report_type':report_type,
                "tickers":tickers,
                "timestamp":datetime.now().isoformat()+"Z"
                })
                print(f"task {task_id} completed emitting task_done")
            except Exception as e:
                print("error trying to notify task completion: ", str(e))
            return result
    except Exception as e:
        print("error executing task: ",str(e))
        return str(e)
    
    # ========quant============
       
@celery.task(bind=True)
def generate_ai_quant(self,tickers,user_id,report_type):
    from quant import quant
    try:
        if not user_id:
            raise Ignore()
        result=quant(tickers)
        print("quant report type: ",type(result))
        task_id=self.request.id
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
            try:
                print("notifying server of completion")
                notify_task_done('task_done',{
                'user_id':user_id,
                'task_id':task_id,
                'tickers':tickers,
                'report_type':report_type,
                "tickers":tickers,
                "timestamp":datetime.now().isoformat()+"Z"
                })
                print(f"task {task_id} completed emitting task_done")
            except Exception as e:
                print("error trying to notify task completion: ", str(e))
            return result
    except Exception as e:
        print("error executing task: ",str(e))
        return str(e)
         

