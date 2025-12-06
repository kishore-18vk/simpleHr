from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id', 
            'first_name', 'last_name', 'employee_id', 
            'gender', 'date_of_birth', 
            'email', 'phone', 'address', 
            'department', 'designation', 'date_of_joining', 'is_active'
        ]
        read_only_fields = ['id']

    def validate_employee_id(self, value):
        if "EMP" not in value.upper():
            raise serializers.ValidationError("Employee ID must contain 'EMP'")
        return value
