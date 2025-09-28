import eventlet
eventlet.monkey_patch()
from flask import Flask,request
from flask_socketio import SocketIO,send,emit,join_room
from dotenv import load_dotenv
load_dotenv()
import os
app = Flask(__name__)
ws_server = SocketIO(app,cors_allowed_origins="*",message_queue=os.getenv('REDIS_SERVER'),async_mode='eventlet')


@ws_server.on("connect")
def handle_connect():
    print('server connected')

@ws_server.on("disconnect")
def handle_disconnect():
    print('bye felicia')

@ws_server.on("task_done")
def handle_task_completed(data):
    print("task is completed dropping result,",data)
    ws_server.emit('task_done',data)

@ws_server.on("message")
def handle_message(data):
    print("i received a", data)
    send(f"whatever you said {data}")
    
@ws_server.on("join_room")
def handle_join(data):
    if data:
        user_id=data.get('user_id','')
        join_room(user_id)
        print(f"client {request.sid} joined room {user_id}")

if __name__=="__main__":
    port = '5009'
    print(f"running app in ws_server",ws_server)
    ws_server.run(app,port=port,debug=True)