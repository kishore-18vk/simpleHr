from rest_framework import serializers
from .models import LeaveRequest
from employee.models import Employee


class LeaveRequestSerializer(serializers.ModelSerializer):
    # Read-only fields for display
    employee_name = serializers.SerializerMethodField()
    department = serializers.CharField(source='employee.department', read_only=True)
    days = serializers.ReadOnlyField()

    # Lookup employee using the 'employee_id' string (e.g., "EMP006")
    employee = serializers.SlugRelatedField(
        slug_field='employee_id',
        queryset=Employee.objects.all()
    )

    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'employee_name', 'department', 'leave_type',
                  'start_date', 'end_date', 'days', 'reason', 'status', 'created_at']

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"