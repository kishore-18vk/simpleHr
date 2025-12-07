from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from employee.models import Employee  # Link to Employee App

class Payroll(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]

    # FOREIGN KEY: Links specific payroll record to a specific employee
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    
    # Financials
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    pay_date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        # 1. If basic_salary is missing, grab it from the Employee profile
        if not self.basic_salary and self.employee.basic_salary:
            self.basic_salary = self.employee.basic_salary
            
        # 2. Auto-calculate Net Salary
        # Convert to float for calculation to avoid Decimal type errors
        self.net_salary = float(self.basic_salary) + float(self.allowances) - float(self.deductions)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.pay_date.strftime('%B %Y')}"