from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from .models import Attendance
from .serializers import AttendanceSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by('-date', 'employee_name')
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        # Filter by date if provided in URL (e.g. ?date=2024-12-07)
        queryset = super().get_queryset()
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)
        return queryset

    # =========================================================
    # API for the 4 Summary Cards (Present, Absent, etc.)
    # =========================================================
    @action(detail=False, methods=['get'])
    def stats(self, request):
        # Get date or default to today
        date_str = request.query_params.get('date', str(timezone.now().date()))
        
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = timezone.now().date()

        # Filter records for that specific day
        daily_records = Attendance.objects.filter(date=target_date)

        stats = [
            {
                'label': 'Present',
                'value': daily_records.filter(status='Present').count(),
                'icon': 'check',
                'color': '#22c55e'
            },
            {
                'label': 'Absent',
                'value': daily_records.filter(status='Absent').count(),
                'icon': 'x',
                'color': '#ef4444'
            },
            {
                'label': 'On Leave',
                'value': daily_records.filter(status='On Leave').count(),
                'icon': 'coffee',
                'color': '#f59e0b'
            },
            {
                'label': 'Late',
                'value': daily_records.filter(status='Late').count(),
                'icon': 'clock',
                'color': '#6366f1'
            }
        ]
        return Response(stats)