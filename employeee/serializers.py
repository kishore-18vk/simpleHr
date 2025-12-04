from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'employee_id', 'designation']

    def validate(self, data):
        if not data.get("name") or not data.get("employee_id"):
            raise serializers.ValidationError(
                {"error": "name and employee_id are mandatory"}
            )
        return data
