from celery import Celery
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
import os
from datetime import datetime,timezone
from celery.exceptions import Ignore
from PDFReport import PDFReport
from s3_bucket_ops import s3_upload
from flask_socketio import SocketIO

load_dotenv()
uri = os.getenv('MONGODB_URI')
WS_SOCKET_URI=os.getenv('VITE_WS_SERVER')
sio = SocketIO(message_queue=os.getenv('REDIS_SERVER'))
celery = Celery(
    'ai_reports',
    broker=os.getenv('REDIS_SERVER'),
    backend=os.getenv('REDIS_SERVER')
)
SUBJECT = "EACSA Financial Report for ticker {tickers} ready"
E_BODY = """
Hello:
Your ai analysis {report_type} for ticker {tickers} is ready for review. 
Click on the link below to access it or login to the EACSA app https://eacsa.us and download it from your report list at the very bottom of the layout.
link to pdf:
{signed_url}
Thank you for using EACSA US! 
"""
def notify_task_result(event_name,payload,name_space):
    if not payload:
        raise(f"message from task queue handler: report metadata is missing.")
    room_name = f"user:{payload['user_id']}"
    try:
        print(f"trying to emit {sio} with event_name: {event_name} and name_space: {name_space}")
        sio.emit(event_name,payload,namespace=name_space,room=room_name)
        sio.sleep(0)
    except Exception as e:
        print(f"error trying to connect to the ws socket {sio} error {str(e)}")

def connect_to_ws_server():
    print(f"trying to connect to socket uri: {WS_SOCKET_URI}")
    sio.connect(WS_SOCKET_URI,namespaces=["\ai"])

def fetch_s3_url(bucket_name:str,file_name:str,client_method='get_object'):
    if not bucket_name or not file_name:
        raise (f"error, missing bucket_name or file_name")
    from s3_bucket_ops import s3_presigned_url
    params={"Bucket":bucket_name,"Key":f"{file_name}.pdf"}
    signed_url=s3_presigned_url(client_method=client_method,method_params=params,expiration_time=30)
    return signed_url

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
            client = MongoClient(uri, server_api=ServerApi('1'),tls=True,tlsCaFile=certifi.where())
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
            try:
                signed_url = fetch_s3_url(bucket_name=report_type,file_name=task_id)
                from emailFunctions import email_send
                email_send(
                    e_to=user_id,
                    e_subject=SUBJECT.format(tickers=tickers),
                    e_body=E_BODY.format(report_type=report_type,tickers=tickers,signed_url=signed_url),
                    e_content_type="text"
                )
            except Exception as e:
                print(f"error trying to fetch a signed url: str(e)")
            


            
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
            client = MongoClient(uri, server_api=ServerApi('1'),tls=True,tlsCaFile=certifi.where())
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
    import sys
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
        print(f"variable type of report quant sent to mongodb: {type(result)}")
        now=datetime.now()
        if result:
            client = MongoClient(uri, server_api=ServerApi('1'),tls=True,tlsCaFile=certifi.where())
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
            client = MongoClient(uri, server_api=ServerApi('1'),tls=True,tlsCaFile=certifi.where())
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
