from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from employee.models import Employee


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
    
    # Month/Year for payroll period
    payroll_month = models.IntegerField(default=1)
    payroll_year = models.IntegerField(default=2024)

    class Meta:
        unique_together = ['employee', 'payroll_month', 'payroll_year']

    def save(self, *args, **kwargs):
        # 1. If basic_salary is missing, grab it from the Employee profile
        if not self.basic_salary and self.employee.basic_salary:
            self.basic_salary = self.employee.basic_salary
            
        # 2. Auto-calculate Net Salary
        self.net_salary = float(self.basic_salary) + float(self.allowances) - float(self.deductions)
        
        # 3. Set payroll month/year from pay_date if not set
        if not self.payroll_month or not self.payroll_year:
            self.payroll_month = self.pay_date.month
            self.payroll_year = self.pay_date.year
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.pay_date.strftime('%B %Y')}"


class PayrollStatusLog(models.Model):
    """Log all payroll status changes for audit purposes."""
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payroll #{self.payroll.id}: {self.old_status} -> {self.new_status}"

    class Meta:
        ordering = ['-changed_at']