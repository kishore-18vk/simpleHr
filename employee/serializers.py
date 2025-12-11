from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id', 
            'first_name', 'last_name', 'employee_id', 
            'gender', 'date_of_birth', 
            'email', 'phone', 'address', 
            'department', 'designation', 'date_of_joining', 
            'basic_salary', 'is_active', 'role'
        ]
        read_only_fields = ['id']

    def validate_employee_id(self, value):
        if "EMP" not in value.upper():
            raise serializers.ValidationError("Employee ID must contain 'EMP'")
        return value


class EmployeeRegisterSerializer(serializers.ModelSerializer):
    """Serializer for admin to register a new employee."""
    username = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=False)
    
    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'employee_id', 
            'username', 'email', 'phone',
            'gender', 'date_of_birth', 'address',
            'department', 'designation', 'date_of_joining',
            'basic_salary', 'role'
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_employee_id(self, value):
        if "EMP" not in value.upper():
            raise serializers.ValidationError("Employee ID must contain 'EMP'")
        if Employee.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID already exists.")
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        
        # Create User with unusable password (will be set later)
        user = User.objects.create_user(
            username=username,
            email=validated_data.get('email', ''),
            password=None  # No password yet
        )
        user.set_unusable_password()
        user.save()
        
        # Create Employee linked to User
        employee = Employee.objects.create(
            user=user,
            **validated_data
        )
        
        # Generate invitation token
        employee.generate_invitation_token()
        
        return employee


class SetPasswordSerializer(serializers.Serializer):
    """Serializer for employee to set password via token."""
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs


class EmployeeLoginSerializer(serializers.Serializer):
    """Serializer for employee login."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class EmployeeProfileSerializer(serializers.ModelSerializer):
    """Serializer for employee viewing their own profile."""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'username',
            'first_name', 'last_name', 'employee_id', 
            'gender', 'date_of_birth', 
            'email', 'phone', 'address', 
            'department', 'designation', 'date_of_joining',
            'basic_salary', 'role', 'is_active'
        ]
        read_only_fields = ['id', 'employee_id', 'role', 'basic_salary', 'username']
