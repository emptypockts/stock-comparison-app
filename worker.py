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
from financialUtils import Status

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
‼️This link is valid only for the next 5 minutes. To access the report after 5 minutes, please login to the EACSA app and download it from your report list section.
{signed_url}
Thank you for using EACSA US! 
"""
name_space = "/ai"
def notify_task_result(event_name,payload,name_space):
    if not payload:
        raise ValueError(f"message from task queue handler: report metadata is missing.")
    room_name = f"user:{payload['user_id']}"
    try:
        print(f"trying to emit an event with event_name: {event_name} and name_space: {name_space} for room_name: {room_name}")
        sio.emit(event_name,payload,namespace=name_space,room=room_name)
        sio.sleep(0)
    except Exception as e:
        print(f"error trying to connect to the ws socket {sio} error {str(e)}")


def fetch_s3_url(bucket_name:str,file_name:str,client_method='get_object'):
    if not bucket_name or not file_name:
        raise ValueError(f"error, missing bucket_name or file_name")
    from s3_bucket_ops import s3_presigned_url
    params={"Bucket":bucket_name,"Key":f"{file_name}.pdf"}
    signed_url=s3_presigned_url(client_method=client_method,method_params=params,expiration_time=300)
    return signed_url

def ai_task_queries_collections_update(
    user_id:str,
    task_id:str,
    tickers:list,
    report_type:str,
    collection:str,
    db_name:str,
    status:Status,
    error=None
    ):
    client = MongoClient(uri, server_api=ServerApi('1'),tls=True,tlsCaFile=certifi.where())
    db = client[db_name]
    ai_task_queries_collections=db[collection]
    ai_task_queries_collections.update_one(
        {"task_id":task_id},
        {
            "$setOnInsert":{
                "user_id":user_id,
                "task_id":task_id,
                "report_type":report_type,
                "tickers":tickers,
                "timestamp":datetime.now(timezone.utc),
            },
            "$set":{
                "status":status.value
            }
            

        },
        upsert=True            
    )
    if error:
        print(f"task_id: {task_id} stored in the db as: {status.value} with error as: {error}")
    else:
        print(f"task_id: {task_id} stored in the db as: {status.value}")
    return None
def ai_report_collections_update(
    user_id:str,
    task_id:str,
    tickers:list,
    report_type:str,
    collection:str,
    db_name:str,
    result:list,
):
    client = MongoClient(uri, server_api=ServerApi('1'),tls=True,tlsCaFile=certifi.where())
    db = client[db_name]
    ai_report_collections = db[collection]
    ai_report_collections.update_one(
            {"task_id":task_id},
        {
            "$set":{
                "assistant":result,
                "report_type":report_type,
                "tickers":tickers,
                "timestamp": datetime.now(timezone.utc)
            },
            "$setOnInsert":{
                "user_id":user_id,
                "task_id":task_id
            }
        },
        upsert=True

    )
    return None

# ==============overall financials==============
@celery.task(bind=True)
def generate_ai_report(self,tickers,user_id,report_type):
    if not user_id:
        raise Ignore()
    task_id=self.request.id
    from aiReport import compile
    # this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.        
    # notify_task_result('task_start',{'user_id':user_id,'task_id':task_id,'tickers':tickers,'report_type':report_type,"timestamp":datetime.now().isoformat()+"Z"},name_space)  
    ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.ongoing)
    try:
        result= compile(tickers)
        if result:
            ai_report_collections_update(user_id,task_id,tickers,report_type,'aiTasks','test',result)
            pdf_report = PDFReport(task_id)
            pdf_report.generate()
            s3_upload(bucket_name=report_type,file_name=f"{task_id}")
            signed_url = fetch_s3_url(bucket_name=report_type,file_name=task_id)
            from emailFunctions import email_send
            response =email_send(
                e_to=user_id,
                e_subject=SUBJECT.format(tickers=tickers),
                e_body=E_BODY.format(report_type=report_type,tickers=tickers,signed_url=signed_url),
                e_content_type="text"
            )
            print(f"email send status: {response}")
        
            print('notifying server of completion')
            ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.completed)
            # this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
            # notify_task_result('task_done',{'user_id':user_id,'task_id':task_id,'tickers':tickers,'report_type':report_type,"tickers":tickers,"timestamp":datetime.now().isoformat()+"Z"},name_space)
            return result

    except Exception as e:
        # this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
        # notify_task_result("task_failed", {"user_id": user_id,"task_id": task_id,"tickers": tickers,"report_type": report_type,"timestamp": datetime.now().isoformat() + "Z","error": str(e)},name_space)
        ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.failed,str(e))
        raise self.retry(exc=e,countdown=5,max_retries=1)
    
    # ============7powers===============

@celery.task(bind=True)
def generate_ai_7powers(self,tickers,user_id,report_type):
    if not user_id:
        raise Ignore()
    from sevenPowers import seven_powers
    task_id=self.request.id
    ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.ongoing)
    try:
        result= seven_powers(tickers)
        if result:
            ai_report_collections_update(user_id,task_id,tickers,report_type,'aiTasks','test',result)
            pdf_report = PDFReport(task_id)
            pdf_report.generate()
            s3_upload(bucket_name=report_type,file_name=f"{task_id}")
            signed_url = fetch_s3_url(bucket_name=report_type,file_name=task_id)
            from emailFunctions import email_send
            response =email_send(
                e_to=user_id,
                e_subject=SUBJECT.format(tickers=tickers),
                e_body=E_BODY.format(report_type=report_type,tickers=tickers,signed_url=signed_url),
                e_content_type="text"
            )
            print(f"email send status: {response}")
            print("notifying server of completion")
            ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.completed)
            # this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
            # notify_task_result('task_done',{'user_id':user_id,'task_id':task_id,'tickers':tickers,'report_type':report_type,"tickers":tickers,"timestamp":datetime.now().isoformat()+"Z"},name_space)
            return result
    except Exception as e:
        ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.failed,str(e))
        # this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
        # notify_task_result("task_failed", {"user_id": user_id,"task_id": task_id,"tickers": tickers,"report_type": report_type,"timestamp": datetime.now().isoformat() + "Z","error": str(e)},name_space)
        raise self.retry(exc=e,countdown=5,max_retries=1)
    
    # ========red-flags quant============
       
@celery.task(bind=True)
def generate_ai_quant(self,tickers,user_id,report_type):
    if not user_id:
        raise Ignore()
    task_id=self.request.id
    import sys
    from quant import quant
    ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.ongoing)
    try:
        current_year=(datetime.now().year)
        
        result=quant(str(current_year),tickers)
        if result:
            ai_report_collections_update(user_id,task_id,tickers,report_type,'aiTasks','test',result)
            pdf_report = PDFReport(task_id)
            pdf_report.generate()
            s3_upload(bucket_name=report_type,file_name=f"{task_id}")
            signed_url = fetch_s3_url(bucket_name=report_type,file_name=task_id)
            from emailFunctions import email_send
            response =email_send(
                e_to=user_id,
                e_subject=SUBJECT.format(tickers=tickers),
                e_body=E_BODY.format(report_type=report_type,tickers=tickers,signed_url=signed_url),
                e_content_type="text"
            )
            print(f"email send status: {response}")
            print("notifying server of completion")
            ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.completed)
            # this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
            # notify_task_result('task_done',{'user_id':user_id,'task_id':task_id,'tickers':tickers,'report_type':report_type,"tickers":tickers,"timestamp":datetime.now().isoformat()+"Z"},name_space)
            return result

    except Exception as e:         
        # this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
        # notify_task_result("task_failed", {"user_id": user_id,"task_id": task_id,"tickers": tickers,"report_type": report_type,"timestamp": datetime.now().isoformat() + "Z","error": str(e)},name_space)
        ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.failed,str(e))
        raise self.retry(exc=e,countdown=5,max_retries=1)
    

# ======= rittenhouse ============

@celery.task(bind=True)
def generate_ai_quant_rittenhouse(self,tickers,user_id,report_type):
    if not user_id:
        raise Ignore()
    task_id=self.request.id
    from rittenhouse import quant_rittenhouse
    # this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
    # notify_task_result('task_start',{'user_id':user_id,'task_id':task_id,'tickers':tickers,'report_type':report_type,"tickers":tickers,"timestamp":datetime.now().isoformat()+"Z"},name_space)
    ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.ongoing)
    try:
        current_year=(datetime.now().year)
        
        result=quant_rittenhouse(str(current_year),tickers)
        if result:
            ai_report_collections_update(user_id,task_id,tickers,report_type,'aiTasks','test',result)
            pdf_report = PDFReport(task_id)
            pdf_report.generate()
            s3_upload(bucket_name=report_type,file_name=f"{task_id}")
            
            signed_url = fetch_s3_url(bucket_name=report_type,file_name=task_id)
            from emailFunctions import email_send
            response =email_send(
                e_to=user_id,
                e_subject=SUBJECT.format(tickers=tickers),
                e_body=E_BODY.format(report_type=report_type,tickers=tickers,signed_url=signed_url),
                e_content_type="text"
            )
            print(f"email send status: {response}")
            print("notifying server of completion")
            ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.completed)
            # this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
            # notify_task_result('task_done',{'user_id':user_id,'task_id':task_id,'tickers':tickers,'report_type':report_type,"tickers":tickers,"timestamp":datetime.now().isoformat()+"Z"},name_space)
            return result

    except Exception as e:
        # this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
        # notify_task_result("task_failed", {"user_id": user_id,"task_id": task_id,"tickers": tickers,"report_type": report_type,"timestamp": datetime.now().isoformat() + "Z","error": str(e)},name_space)
        ai_task_queries_collections_update(user_id,task_id,tickers,report_type,'aiTaskQueries','test',Status.failed,str(e))
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
    },name_space)
