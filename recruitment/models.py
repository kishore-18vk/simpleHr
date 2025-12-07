from django.db import models

class JobPosting(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Closed', 'Closed'),
        ('Draft', 'Draft'),
    ]

    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50) # e.g. Full-time, Contract
    applicants_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    posted_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title