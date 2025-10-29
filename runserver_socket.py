import os
import django
import socketio
import eventlet
import eventlet.wsgi
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

# 🔌 Create Socket.IO server
sio = socketio.Server(async_mode='eventlet', cors_allowed_origins='*')

# Django WSGI app
django_app = get_wsgi_application()

# Wrap Django inside Socket.IO middleware
app = socketio.WSGIApp(sio, django_app)

# Example event handlers
@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
def trigger_event(sid, data):
    print(f"Received trigger event: {data}")
    sio.emit("update", {"message": "Triggered event received!"})



# 🏃 Run the combined server
if __name__ == "__main__":
    print("🚀 Running Django + Socket.IO server on http://127.0.0.1:8000")
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
