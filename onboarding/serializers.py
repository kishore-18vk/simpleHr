from rest_framework import serializers
from .models import OnboardingTask
from employee.models import Employee

class OnboardingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingTask
        fields = '__all__'

class NewHireSerializer(serializers.ModelSerializer):
    # Custom field to calculate progress dynamically
    progress = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'first_name', 'last_name', 'full_name', 'designation', 'department', 'date_of_joining', 'progress']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_progress(self, obj):
        total_tasks = obj.onboarding_tasks.count()
        if total_tasks == 0:
            return 0
        completed = obj.onboarding_tasks.filter(status='completed').count()
        return int((completed / total_tasks) * 100)