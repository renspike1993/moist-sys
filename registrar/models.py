from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    abbrv = models.CharField(max_length=50)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
