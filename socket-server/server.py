from flask import Flask
from flask_socketio import SocketIO
app = Flask(__name__)
ws_server = SocketIO(app,cors_allowed_origins="*",)

@ws_server.on("connect")
def handle_connect():
    print('dropping ai result')
@ws_server.on("disconnect")
def handle_disconnect():
    print('result dropped bye felicia')
@ws_server.on("task_done")
def handle_task_completed(data):
    print("task is completed dropping result,",type(data))
if __name__=="__main__":
    ws_server.run(app,port=5009,host="0.0.0.0")
