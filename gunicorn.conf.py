import eventlet
import eventlet.wsgi

# Patch as early as possible in the worker process
def post_fork(server, worker):
    eventlet.monkey_patch()

worker_class = "eventlet"
workers = 1
bind = "0.0.0.0:5009"
