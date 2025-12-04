from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    employee_id = models.IntegerField(unique=True)
    designation = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

