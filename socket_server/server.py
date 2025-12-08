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
name_space='/ai'

@ws_server.on("connect",namespace=name_space)
def handle_connect():
    print(f"new client joined in at {datetime.now()} id: {request.sid}")

@ws_server.on("disconnect",namespace=name_space)
def handle_disconnect():
    print(f"client got disconnected at {datetime.now()} id: {request.sid}")

@ws_server.on("task_done",namespace=name_space)
def handle_task_completed(data):
    print("task is completed dropping result,",data)
    room_name = f"user:{data.get('user_id','')}"
    join_room(room=room_name,namespace=name_space)
    print(f"client: {data.get('user_id','')} joined the room {data.get('task_id','')} with sid {request.sid}")
    ws_server.emit('task_done',data,namespace=name_space)


@ws_server.on("task_failed",namespace=name_space)
def handle_message(data):
    room_name = f"user:{data.get('user_id','')}"
    join_room(room=room_name,namespace=name_space)
    print(f"socket server: task_failed: {data['task_id']} namespace: {name_space}")
    ws_server.emit('task_failed',data,namespace=name_space)
    
@ws_server.on("join_room",namespace=name_space)
def handle_join(data):
    if data:
        user_id=data.get('user_id','')
        sid=request.sid
        room_name = f"user:{user_id}"
        join_room(room_name,namespace=name_space)
        print(f"client {request.sid} joined room {room_name} with id:{sid}")
def notify_user(user_id,event_name,payload=None):
    room_name = f"user:{user_id}"
    SocketIO.emit(event_name,payload or {},room=room_name,namespace=name_space)


if __name__=="__main__":
    port = '5009'
    print(f"running app in ws_server",ws_server)
    ws_server.run(app,port=port,debug=True)