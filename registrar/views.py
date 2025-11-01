from django.shortcuts import render

# Registrar homepage
def registrar_home(request):
    return render(request, 'folder/list.html')

# Dashboard page
def registrar_dashboard(request):
    return render(request, 'registrar/dashboard.html')

# Example: list of students
def registrar_students(request):
    return render(request, 'registrar/students.html')


# Example: list of students
def registrar_couurses(request):
    return render(request, 'courses/list.html')
