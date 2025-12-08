from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import EmployeeSettings
from .serializers import EmployeeSettingsSerializer
from employee.models import Employee

class UserSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = EmployeeSettingsSerializer
    # permission_classes = [permissions.IsAuthenticated] # Uncomment if using Auth

    def get_object(self):
        # HARDCODED for development (Replace with self.request.user.employee in production)
        # Assuming we are editing settings for the first employee found or a specific ID
        # For real auth: employee = self.request.user.employee
        
        # Fallback logic for demo purposes:
        employee = Employee.objects.first() 
        
        if not employee:
            return None

        # Get existing settings or create default ones
        obj, created = EmployeeSettings.objects.get_or_create(employee=employee)
        return obj