from rest_framework import serializers
from .models import EmployeeSettings

class EmployeeSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSettings
        fields = ['theme', 'email_notifications', 'push_notifications', 'language', 'timezone', 'two_factor_enabled']