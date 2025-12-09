from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Asset, AssetRequest
from .serializers import AssetSerializer, AssetRequestSerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    @action(detail=False, methods=['get'])
    def category_stats(self, request):
        stats = [
            {'id': 1, 'name': 'Laptops', 'count': Asset.objects.filter(asset_type='Laptop').count(), 'color': '#6366f1'},
            {'id': 2, 'name': 'Monitors', 'count': Asset.objects.filter(asset_type='Monitor').count(), 'color': '#22c55e'},
            {'id': 3, 'name': 'Phones', 'count': Asset.objects.filter(asset_type='Phone').count(), 'color': '#f59e0b'},
            {'id': 4, 'name': 'Accessories', 'count': Asset.objects.filter(asset_type='Accessory').count(), 'color': '#ec4899'},
        ]
        return Response(stats)

class AssetRequestViewSet(viewsets.ModelViewSet):
    queryset = AssetRequest.objects.all().order_by('-request_date')
    serializer_class = AssetRequestSerializer

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        asset_request = self.get_object()
        new_status = request.data.get('status')
        
        if new_status == 'Approved' and asset_request.status != 'Approved':
            # === LOGIC TO CREATE ASSET ON APPROVAL ===
            Asset.objects.create(
                name=f"{asset_request.asset_type} for {asset_request.employee.first_name}",
                asset_type=asset_request.asset_type,
                serial_number=f"AUTO-{asset_request.id}", # Placeholder serial
                assigned_to=asset_request.employee,
                assigned_date=asset_request.request_date,
                status='Assigned',
                condition='Good'
            )
            
        if new_status in ['Approved', 'Rejected']:
            asset_request.status = new_status
            asset_request.save()
            return Response({'message': f'Request {new_status}'})
        
        return Response({'error': 'Invalid status'}, status=400)