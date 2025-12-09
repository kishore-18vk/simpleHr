from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from .models import Attendance
from .serializers import AttendanceSerializer
from employee.models import Employee


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('employee').all().order_by('-date', 'employee__first_name')
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        # Filter by date if provided in URL (e.g. ?date=2024-12-07)
        queryset = super().get_queryset()
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)
        return queryset

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
                'value': daily_records.filter(status__in=['Present', 'Late']).count(),
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

    # Generate attendance for all employees for a given date
    @action(detail=False, methods=['post'])
    def generate_daily(self, request):
        date_str = request.data.get('date', str(timezone.now().date()))
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = timezone.now().date()

        employees = Employee.objects.filter(is_active=True)
        created_count = 0

        for emp in employees:
            # Check if attendance already exists for this employee on this date
            exists = Attendance.objects.filter(employee=emp, date=target_date).exists()
            if not exists:
                Attendance.objects.create(
                    employee=emp,
                    date=target_date,
                    status='Absent'  # Default to Absent, can be updated via check-in
                )
                created_count += 1

        return Response({
            'message': f'Generated attendance records for {created_count} employees.',
            'date': str(target_date)
        })