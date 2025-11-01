from django.urls import path
from . import views

urlpatterns = [
    path('', views.registrar_home, name='registrar_home'),
    path('dashboard/', views.registrar_dashboard, name='registrar_dashboard'),
    path('students/', views.registrar_students, name='registrar_students'),
]
