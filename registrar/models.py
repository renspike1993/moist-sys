from django.db import models

class Program(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name



# Create your models here.
class Students(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    fullname = models.CharField(max_length=100)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.student_id})"