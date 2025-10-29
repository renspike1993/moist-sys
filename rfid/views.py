from django.shortcuts import render
from django.http import JsonResponse
import socketio

# Create Socket.IO server
sio = socketio.Server(async_mode='eventlet', cors_allowed_origins='*')
django_app = socketio.WSGIApp(sio)

def index(request):
    return render(request, 'dashboard/index.html')

# This view triggers the frontend update
def trigger_event(request):
    sio.emit('rfid_trigger', {'message': 'RFID event triggered from Django!'})
    return JsonResponse({'status': 'ok', 'msg': 'Event triggered'})
def dashboard(request):
    sio.emit('rfid_trigger', {'message': 'RFID event triggered from Django!'})

    return render(request, 'dashboard.html')