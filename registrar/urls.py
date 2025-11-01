from django.urls import path
from . import views

urlpatterns = [
    path('', views.registrar_home, name='registrar_home'),
    path('courses/', views.registrar_couurses, name='courses'),
    path('students/', views.registrar_students, name='registrar_students'),



]
