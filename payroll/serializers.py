from rest_framework import serializers
from .models import Payroll, PayrollStatusLog


class PayrollSerializer(serializers.ModelSerializer):
    # Get employee details from Employee model
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    department = serializers.CharField(source='employee.department', read_only=True)
    designation = serializers.CharField(source='employee.designation', read_only=True)

    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'employee_id',
            'department', 'designation', 'basic_salary', 'allowances', 'deductions',
            'net_salary', 'status', 'pay_date', 'payroll_month', 'payroll_year'
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"


class PayrollStatusLogSerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)
    employee_id = serializers.CharField(source='payroll.employee.employee_id', read_only=True)
    
    class Meta:
        model = PayrollStatusLog
        fields = [
            'id', 'payroll', 'employee_id', 'old_status', 'new_status',
            'changed_by', 'changed_by_username', 'changed_at', 'notes'
        ]
        read_only_fields = ['id', 'changed_at']


class SetPayrollStatusSerializer(serializers.Serializer):
    """Serializer for setting payroll status."""
    payroll_id = serializers.IntegerField(required=False)
    employee_id = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=['Paid', 'Pending'], required=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get('payroll_id') and not attrs.get('employee_id'):
            raise serializers.ValidationError("Either payroll_id or employee_id is required")
        return attrs
    
    def validate_status(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Status cannot be empty")
        return value