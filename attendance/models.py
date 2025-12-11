from django.db import models
from datetime import date, datetime, timedelta
from employee.models import Employee


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('On Leave', 'On Leave'),
        ('Late', 'Late'),
        ('Half Day', 'Half Day'),
        ('Working', 'Working'),
    ]

    # ForeignKey to Employee model
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    
    date = models.DateField(default=date.today)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Absent')
    
    # We store this, but also calculate it
    working_hours = models.CharField(max_length=20, blank=True, null=True, default='-')
    working_hours_decimal = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ['employee', 'date']  # One attendance per employee per day

    def calculate_working_hours(self):
        """Calculate working hours from check-in and check-out times."""
        if not self.check_in or not self.check_out:
            return 0.0
        
        t1 = datetime.combine(date.today(), self.check_in)
        t2 = datetime.combine(date.today(), self.check_out)
        diff = t2 - t1
        
        total_seconds = diff.total_seconds()
        hours = total_seconds / 3600
        return round(hours, 2)

    def save(self, *args, **kwargs):
        # 1. Auto-Calculate Status based on Time
        if self.check_in and not self.check_out and self.status not in ['On Leave']:
            self.status = 'Working'
        
        elif self.check_in and self.check_out:
            # Calculate Working Hours
            hours = self.calculate_working_hours()
            self.working_hours_decimal = hours
            
            hrs = int(hours)
            mins = int((hours - hrs) * 60)
            self.working_hours = f"{hrs}h {mins}m"
            
            # Determine status based on working hours
            if hours < 4:
                self.status = 'Absent'  # Less than 4 hours = Absent
            elif hours < 8:
                self.status = 'Half Day'  # 4-8 hours = Half Day
            else:
                # Check if late (after 9:30 AM)
                check_in_time = self.check_in.strftime('%H:%M')
                if check_in_time > '09:30':
                    self.status = 'Late'
                else:
                    self.status = 'Present'
        
        elif not self.check_in and self.status not in ['On Leave']:
            self.status = 'Absent'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.date}"