from django.urls import path
from .views import LeaveRequestView

urlpatterns = [
    # Empty string because the prefix is handled in the main urls.py
    path('', LeaveRequestView.as_view(), name='leave-request'),
]