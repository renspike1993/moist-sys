from django.shortcuts import render

# Create your views here.
def registrar_home(request):
    return render(request, 'base2.html')

def registrar_dashboard(request):
    return render(request, 'dashboard.html')