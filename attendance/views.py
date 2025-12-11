from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, date, time
from .models import Attendance
from .serializers import AttendanceSerializer
from employee.models import Employee
from employee.permissions import IsAdmin, IsAdminOrOwner


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
            },
            {
                'label': 'Half Day',
                'value': daily_records.filter(status='Half Day').count(),
                'icon': 'clock',
                'color': '#8b5cf6'
            },
            {
                'label': 'Working',
                'value': daily_records.filter(status='Working').count(),
                'icon': 'activity',
                'color': '#06b6d4'
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

    # ========== NEW CHECK-IN/CHECK-OUT ENDPOINTS ==========

    @action(detail=False, methods=['post'], url_path='check-in')
    def check_in(self, request):
        """
        Employee check-in for the day.
        Creates or updates attendance record with check-in time.
        """
        # Get employee from request user or from request data
        employee_id = request.data.get('employee_id')
        
        if employee_id:
            try:
                employee = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                return Response({
                    'error': 'Employee not found'
                }, status=status.HTTP_404_NOT_FOUND)
        elif hasattr(request.user, 'employee_profile'):
            employee = request.user.employee_profile
        else:
            return Response({
                'error': 'Employee ID required or login required'
            }, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.now().date()
        current_time = timezone.now().time()

        # Get or create attendance for today
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={'status': 'Absent'}
        )

        # Validation: No double check-in
        if attendance.check_in:
            return Response({
                'error': 'Already checked in today',
                'check_in_time': attendance.check_in.strftime('%H:%M:%S'),
                'status': attendance.status
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set check-in time
        attendance.check_in = current_time
        attendance.status = 'Working'
        attendance.save()

        return Response({
            'message': 'Check-in successful',
            'employee_id': employee.employee_id,
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'date': str(today),
            'check_in_time': attendance.check_in.strftime('%H:%M:%S'),
            'status': attendance.status
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='check-out')
    def check_out(self, request):
        """
        Employee check-out for the day.
        Updates attendance with check-out time and calculates working hours.
        """
        # Get employee from request user or from request data
        employee_id = request.data.get('employee_id')
        
        if employee_id:
            try:
                employee = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                return Response({
                    'error': 'Employee not found'
                }, status=status.HTTP_404_NOT_FOUND)
        elif hasattr(request.user, 'employee_profile'):
            employee = request.user.employee_profile
        else:
            return Response({
                'error': 'Employee ID required or login required'
            }, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.now().date()
        current_time = timezone.now().time()

        # Get attendance for today
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response({
                'error': 'No attendance record found for today. Please check in first.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validation: Cannot check-out before check-in
        if not attendance.check_in:
            return Response({
                'error': 'Cannot check out before checking in'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validation: No double check-out
        if attendance.check_out:
            return Response({
                'error': 'Already checked out today',
                'check_out_time': attendance.check_out.strftime('%H:%M:%S'),
                'working_hours': attendance.working_hours,
                'status': attendance.status
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set check-out time (this will auto-calculate status in save())
        attendance.check_out = current_time
        attendance.save()

        return Response({
            'message': 'Check-out successful',
            'employee_id': employee.employee_id,
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'date': str(today),
            'check_in_time': attendance.check_in.strftime('%H:%M:%S'),
            'check_out_time': attendance.check_out.strftime('%H:%M:%S'),
            'working_hours': attendance.working_hours,
            'status': attendance.status
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='today/(?P<employee_id>[^/.]+)')
    def today(self, request, employee_id=None):
        """
        Get today's attendance for a specific employee.
        """
        if not employee_id:
            return Response({
                'error': 'Employee ID required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({
                'error': 'Employee not found'
            }, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()

        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
            serializer = AttendanceSerializer(attendance)
            return Response(serializer.data)
        except Attendance.DoesNotExist:
            return Response({
                'employee_id': employee.employee_id,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'date': str(today),
                'status': 'Not Checked In',
                'check_in': None,
                'check_out': None,
                'working_hours': '-'
            })

    @action(detail=False, methods=['get'], url_path='report')
    def report(self, request):
        """
        Get monthly attendance report.
        Query params: month (format: YYYY-MM), employee_id (optional)
        """
        month_str = request.query_params.get('month')
        employee_id = request.query_params.get('employee_id')

        if not month_str:
            # Default to current month
            month_str = timezone.now().strftime('%Y-%m')

        try:
            year, month = month_str.split('-')
            year, month = int(year), int(month)
        except ValueError:
            return Response({
                'error': 'Invalid month format. Use YYYY-MM'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Build query
        queryset = Attendance.objects.filter(
            date__year=year,
            date__month=month
        ).select_related('employee').order_by('date', 'employee__first_name')

        if employee_id:
            queryset = queryset.filter(employee__employee_id=employee_id)

        serializer = AttendanceSerializer(queryset, many=True)

        # Calculate summary stats
        present_count = queryset.filter(status__in=['Present', 'Late']).count()
        absent_count = queryset.filter(status='Absent').count()
        half_day_count = queryset.filter(status='Half Day').count()
        leave_count = queryset.filter(status='On Leave').count()
        late_count = queryset.filter(status='Late').count()

        return Response({
            'month': month_str,
            'employee_id': employee_id,
            'summary': {
                'present': present_count,
                'absent': absent_count,
                'half_day': half_day_count,
                'on_leave': leave_count,
                'late': late_count,
                'total_records': queryset.count()
            },
            'records': serializer.data
        })

    @action(detail=False, methods=['post'], url_path='auto-absent')
    def auto_absent(self, request):
        """
        Mark all employees as absent if they haven't checked in by 12 PM.
        This can be called by a cron job or scheduled task.
        """
        today = timezone.now().date()
        current_time = timezone.now().time()
        
        # Only run if it's after 12 PM
        noon = time(12, 0, 0)
        if current_time < noon:
            return Response({
                'message': 'Auto-absent only runs after 12 PM',
                'current_time': current_time.strftime('%H:%M:%S')
            }, status=status.HTTP_400_BAD_REQUEST)

        employees = Employee.objects.filter(is_active=True)
        marked_count = 0

        for emp in employees:
            attendance, created = Attendance.objects.get_or_create(
                employee=emp,
                date=today,
                defaults={'status': 'Absent'}
            )
            
            # If no check-in and status is not already set to leave
            if not attendance.check_in and attendance.status not in ['On Leave', 'Absent']:
                attendance.status = 'Absent'
                attendance.save()
                marked_count += 1

        return Response({
            'message': f'Marked {marked_count} employees as absent',
            'date': str(today),
            'time': current_time.strftime('%H:%M:%S')
        })