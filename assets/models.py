from django.db import models
from employee.models import Employee

class Asset(models.Model):
    TYPE_CHOICES = [
        ('Laptop', 'Laptop'),
        ('Monitor', 'Monitor'),
        ('Phone', 'Phone'),
        ('Accessory', 'Accessory'),
    ]
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Assigned', 'Assigned'),
        ('Broken', 'Broken'),
    ]
    CONDITION_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ]

    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    serial_number = models.CharField(max_length=100, unique=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    assigned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Excellent')
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})"

class AssetRequest(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=50, choices=Asset.TYPE_CHOICES)
    reason = models.TextField()
    # Auto-add date (Fixes the crash)
    request_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.employee.first_name} requested {self.asset_type}"