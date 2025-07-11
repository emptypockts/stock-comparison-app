import eventlet
eventlet.monkey_patch()
from flask import Flask
from flask_socketio import SocketIO,send,emit
app = Flask(__name__)
ws_server = SocketIO(app,cors_allowed_origins="*",message_queue='redis://localhost:6379/0',async_mode='eventlet')


@ws_server.on("connect")
def handle_connect():
    print('dropping ai result')

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
    
if __name__=="__main__":
    port = '5009'
    print(f"running app in ws_server",ws_server)
    ws_server.run(app,port=port,debug=True)