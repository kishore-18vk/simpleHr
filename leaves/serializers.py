from rest_framework import serializers
from .models import LeaveRequest
from employee.models import Employee  # Make sure to import your Employee model

class LeaveRequestSerializer(serializers.ModelSerializer):
    # Read-only fields for display
    name = serializers.CharField(source='employee.name', read_only=True)
    days = serializers.ReadOnlyField()

    # === THE FIX ===
    # This tells Django to look up the employee using the 'employee_id' string (e.g., "EMP006")
    employee = serializers.SlugRelatedField(
        slug_field='employee_id',   # This must match the exact field name in your Employee model
        queryset=Employee.objects.all()
    )

    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'name', 'leave_type', 'start_date', 'end_date', 'days', 'reason', 'status']