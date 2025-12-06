from django.urls import path
from .views import EmployeeProfileView

urlpatterns = [
    path('employee-profile/', EmployeeProfileView.as_view(), name='employee-profile'),
]
