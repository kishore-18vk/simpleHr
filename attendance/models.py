from django.db import models
from datetime import date, datetime, timedelta

# Import Employee model if available, else use CharField
try:
    from employee.models import Employee
except ImportError:
    Employee = None

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('On Leave', 'On Leave'),
        ('Late', 'Late'),
        ('Half Day', 'Half Day'),
        ('Working', 'Working'), # For currently active sessions
    ]

    # If you have an Employee model, use ForeignKey
    # employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    # For now, using name/id directly to match your request
    employee_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20) # e.g. EMP001
    
    date = models.DateField(default=date.today)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Absent')
    
    # We store this, but also calculate it
    working_hours = models.CharField(max_length=20, blank=True, null=True, default='-')

    def save(self, *args, **kwargs):
        # 1. Auto-Calculate Status based on Time
        if self.check_in and not self.check_out and self.status != 'On Leave':
             self.status = 'Working'
        
        elif self.check_in and self.check_out:
            # Example Logic: Late if after 9:30 AM
            check_in_time = self.check_in.strftime('%H:%M')
            if check_in_time > '09:30':
                self.status = 'Late'
            else:
                self.status = 'Present'

            # 2. Calculate Working Hours
            t1 = datetime.combine(date.today(), self.check_in)
            t2 = datetime.combine(date.today(), self.check_out)
            diff = t2 - t1
            
            total_seconds = diff.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            self.working_hours = f"{hours}h {minutes}m"
        
        elif not self.check_in and self.status != 'On Leave':
            self.status = 'Absent'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_name} - {self.date}"