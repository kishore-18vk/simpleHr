from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets


class Employee(models.Model):
    # Link to Django User for authentication
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')
    
    # Basic Info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=20, unique=True)
    
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    
    # Payroll field
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00) 
    
    is_active = models.BooleanField(default=True)
    
    # Role-based access
    ROLE_CHOICES = [('admin', 'Admin'), ('employee', 'Employee')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    
    # Invitation token for password setup
    invitation_token = models.CharField(max_length=64, null=True, blank=True)
    token_expires = models.DateTimeField(null=True, blank=True)

    def generate_invitation_token(self):
        """Generate a secure token for password setup."""
        self.invitation_token = secrets.token_urlsafe(32)
        self.token_expires = timezone.now() + timezone.timedelta(days=7)  # Token valid for 7 days
        self.save()
        return self.invitation_token

    def is_token_valid(self, token):
        """Check if invitation token is valid and not expired."""
        if not self.invitation_token or not self.token_expires:
            return False
        if self.invitation_token != token:
            return False
        if timezone.now() > self.token_expires:
            return False
        return True

    def clear_token(self):
        """Clear invitation token after password is set."""
        self.invitation_token = None
        self.token_expires = None
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"