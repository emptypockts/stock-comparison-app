import eventlet
eventlet.monkey_patch()
from flask import Flask,request 
from flask_socketio import SocketIO,join_room
from datetime import datetime
from app_constants import REDIS_SERVER_URI
app = Flask(__name__)
ws_server = SocketIO(app,cors_allowed_origins="*",message_queue=REDIS_SERVER_URI,
                     async_mode='eventlet'
                     )
name_space="/ai"

@ws_server.on("connect",namespace=name_space)
def handle_connect(auth):
    print(f"client connected to /ai {request.sid}")
    user_id = None
    if auth:
        
        user_id = auth.get("user_id")
    if not user_id:
        print (f"no user_id provided to join a room")
        return
    
    room_name = f"user:{user_id}"
    join_room(room_name)
    print(f"joined {request.sid} to room {room_name}")

@ws_server.on("disconnect",namespace=name_space)
def handle_disconnect():
    print(f"client got disconnected at {datetime.now()} id: {request.sid}")

    
@ws_server.on("join_room",namespace=name_space)
def handle_join(data):
    if not data:
        print("missing data to join the room")
        return
    if data:
        user_id=data.get('user_id','')
        room_name = f"user:{user_id}"
        join_room(room_name)
        print(f"Socket {request.sid} joined room {room_name}")



def notify_user(user_id,event_name,name_space,payload=None):
    print(f"notifying user: {user_id} of task completion: {event_name}")
    room_name = f"user:{user_id}"
    ws_server.emit(event_name,payload or {},room=room_name,namespace=name_space)


if __name__=="__main__":
    port = '5009'
    print(f"running app in ws_server",ws_server)
    ws_server.run(app,port=port,debug=True)