from celery import Celery
import socketio
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime,timezone
from celery.exceptions import Ignore
from PDFReport import PDFReport
from s3_bucket_ops import s3_upload


load_dotenv()
uri = os.getenv('MONGODB_URI')
WS_SOCKET_URI=os.getenv('VITE_WS_SERVER')
sio = socketio.Client()
celery = Celery(
    'ai_reports',
    broker=os.getenv('REDIS_SERVER'),
    backend=os.getenv('REDIS_SERVER')
)

def notify_task_result(event_name,payload,name_space):
    if not sio.connected:
        sio.connect(WS_SOCKET_URI,namespaces=[name_space])
    try:
        sio.emit(event_name,payload,namespace=name_space)
        sio.sleep(0)
    except Exception as e:
        print(f"error trying to connect to the ws socket {sio} error {str(e)}")

def connect_to_ws_server():
    sio.connect(WS_SOCKET_URI)

# ==============overall financials==============
@celery.task(bind=True)
def generate_ai_report(self,tickers,user_id,report_type):
    task_id=self.request.id
    from aiReport import compile
    notify_task_result('task_start',{
        'user_id':user_id,
        'task_id':task_id,
        'tickers':tickers,
        'report_type':report_type,
        "tickers":tickers,
        "timestamp":datetime.now().isoformat()+"Z"
    },'/ai')    
    
    try:
        if not user_id:
            raise Ignore()
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

            pdf_report = PDFReport(task_id)
            pdf_report.generate()
            s3_upload(bucket_name=report_type,file_name=f"{task_id}")

            
            print('notifying server of completion')
            notify_task_result('task_done',{
                'user_id':user_id,
                'task_id':task_id,
                'tickers':tickers,
                'report_type':report_type,
                "tickers":tickers,
                "timestamp":datetime.now().isoformat()+"Z"

            },'/ai')
            return result

    except Exception as e:
        print(f"error with task execution for tickers {tickers}, task id {task_id}")
        notify_task_result("task_failed", {
            "user_id": user_id,
            "task_id": task_id,
            "tickers": tickers,
            "report_type": report_type,
            "timestamp": datetime.now().isoformat() + "Z",
            "error": str(e)
        },'/ai')
        
        raise self.retry(exc=e,countdown=5,max_retries=1)
    
    # ============7powers===============

@celery.task(bind=True)
def generate_ai_7powers(self,tickers,user_id,report_type):
    from sevenPowers import seven_powers
    task_id=self.request.id
    notify_task_result('task_start',{
        'user_id':user_id,
        'task_id':task_id,
        'tickers':tickers,
        'report_type':report_type,
        "tickers":tickers,
        "timestamp":datetime.now().isoformat()+"Z"
    },'/ai')
    try:
        if not user_id:
            raise Ignore()

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
            pdf_report = PDFReport(task_id)
            pdf_report.generate()
            s3_upload(bucket_name=report_type,file_name=f"{task_id}")
            
            print("notifying server of completion")
            notify_task_result('task_done',{
            'user_id':user_id,
            'task_id':task_id,
            'tickers':tickers,
            'report_type':report_type,
            "tickers":tickers,
            "timestamp":datetime.now().isoformat()+"Z"
            },'/ai')
            
            return result

            
    except Exception as e:
        print(f"error with task execution for tickers {tickers}, task id {task_id}")
        notify_task_result("task_failed", {
            "user_id": user_id,
            "task_id": task_id,
            "tickers": tickers,
            "report_type": report_type,
            "timestamp": datetime.now().isoformat() + "Z",
            "error": str(e)
        },'/ai')
        
        raise self.retry(exc=e,countdown=5,max_retries=1)
    
    # ========quant============
       
@celery.task(bind=True)
def generate_ai_quant(self,tickers,user_id,report_type):
    current_year=(datetime.now().year)
    task_id=self.request.id
    from quant import quant
    notify_task_result('task_start',{
        'user_id':user_id,
        'task_id':task_id,
        'tickers':tickers,
        'report_type':report_type,
        "tickers":tickers,
        "timestamp":datetime.now().isoformat()+"Z"
    },'/ai')
    try:
        if not user_id:
            raise Ignore()
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
            pdf_report = PDFReport(task_id)
            pdf_report.generate()
            s3_upload(bucket_name=report_type,file_name=f"{task_id}")
        
            print("notifying server of completion")
            notify_task_result('task_done',{
            'user_id':user_id,
            'task_id':task_id,
            'tickers':tickers,
            'report_type':report_type,
            "tickers":tickers,
            "timestamp":datetime.now().isoformat()+"Z"
            },'/ai')
            
            return result

    except Exception as e:
         
        print(f"error with task execution for tickers {tickers}, task id {task_id}")
        notify_task_result("task_failed", {
            "user_id": user_id,
            "task_id": task_id,
            "tickers": tickers,
            "report_type": report_type,
            "timestamp": datetime.now().isoformat() + "Z",
            "error": str(e)
        },'/ai')
        
        raise self.retry(exc=e,countdown=5,max_retries=1)
    

# ======= rittenhouse ============

@celery.task(bind=True)
def generate_ai_quant_rittenhouse(self,tickers,user_id,report_type):
    current_year=(datetime.now().year)
    task_id=self.request.id
    from rittenhouse import quant_rittenhouse
    notify_task_result('task_start',{
        'user_id':user_id,
        'task_id':task_id,
        'tickers':tickers,
        'report_type':report_type,
        "tickers":tickers,
        "timestamp":datetime.now().isoformat()+"Z"
    },'/ai') 
    try:
        if not user_id:
            raise Ignore()

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
            pdf_report = PDFReport(task_id)
            pdf_report.generate()
            s3_upload(bucket_name=report_type,file_name=f"{task_id}")
        
            print("notifying server of completion")
            notify_task_result('task_done',{
            'user_id':user_id,
            'task_id':task_id,
            'tickers':tickers,
            'report_type':report_type,
            "tickers":tickers,
            "timestamp":datetime.now().isoformat()+"Z"
            },'/ai')
            
            return result

    except Exception as e:
         
        print(f"error with task execution for tickers {tickers}, task id {task_id}")
        notify_task_result("task_failed", {
            "user_id": user_id,
            "task_id": task_id,
            "tickers": tickers,
            "report_type": report_type,
            "timestamp": datetime.now().isoformat() + "Z",
            "error": str(e)
        },'/ai')
        
        raise self.retry(exc=e,countdown=5,max_retries=1)

@celery.task(bind=True)
def test_task(self):
    task_id= "test"
    user_id="noreply.info@eacsa.us"
    tickers=['sofi']
    report_type='overall-reports'
    print("notifying server of completion")
    notify_task_result('task_done',{
    'user_id':user_id,
    'task_id':task_id,
    'tickers':tickers,
    'report_type':report_type,
    "tickers":tickers,
    "timestamp":datetime.now().isoformat()+"Z"
    },'/ai')
