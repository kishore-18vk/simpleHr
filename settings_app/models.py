from django.db import models
from employee.models import Employee

class EmployeeSettings(models.Model):
    THEME_CHOICES = [('light', 'Light'), ('dark', 'Dark'), ('system', 'System')]
    LANG_CHOICES = [('en', 'English'), ('es', 'Spanish'), ('fr', 'French')]

    # Link to Employee
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='settings')
    
    # 1. Appearance
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    
    # 2. Notifications
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=False)
    
    # 3. Language & Region
    language = models.CharField(max_length=10, choices=LANG_CHOICES, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # 4. Security (2FA)
    two_factor_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"Settings for {self.employee.first_name}"