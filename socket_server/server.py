import eventlet
eventlet.monkey_patch()
from flask import Flask,request 
from flask_socketio import SocketIO,send,emit,join_room
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
import os
app = Flask(__name__)
ws_server = SocketIO(app,cors_allowed_origins="*",message_queue=os.getenv('REDIS_SERVER'),async_mode='eventlet')


@ws_server.on("connect")
def handle_connect():
    print(f"new client joined in at {datetime.now()} id: {request.sid}")

@ws_server.on("disconnect")
def handle_disconnect():
    print(f"client got disconnected at {datetime.now()} id: {request.sid}")

@ws_server.on("task_done")
def handle_task_completed(data):
    print("task is completed dropping result,",data)
    join_room(room=data.get('task_id',''))
    print(f"client: {data.get('user_id','')} joined the room {data.get('task_id','')} with sid {request.sid}")
    ws_server.emit('task_done',data)


@ws_server.on("message")
def handle_message(data):
    print("i received a", data)
    send(f"whatever you said {data}")
    
@ws_server.on("join_room")
def handle_join(data):
    if data:
        user_id=data.get('user_id','')
        sid=request.sid
        join_room(user_id)
        print(f"client {request.sid} joined room {user_id} with id:{sid}")

@ws_server.on('register_user')
def register_user(data):
    if data:
        user_id=data.get('user_id')
        sid=request.sid
        print(f"🔗 User {user_id} joined room {user_id} with SID {sid}")



if __name__=="__main__":
    port = '5009'
    print(f"running app in ws_server",ws_server)
    ws_server.run(app,port=port,debug=True)