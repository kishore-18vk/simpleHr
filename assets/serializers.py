from rest_framework import serializers
from .models import Asset, AssetRequest

class AssetSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.first_name', read_only=True)

    class Meta:
        model = Asset
        fields = '__all__'

class AssetRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.first_name', read_only=True)

    class Meta:
        model = AssetRequest
        fields = '__all__'