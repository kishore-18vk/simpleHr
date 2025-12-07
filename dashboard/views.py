from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone

# Import models from other apps
from employee.models import Employee
from recruitment.models import JobPosting
from leaves.models import LeaveRequest
from attendance.models import Attendance

class DashboardStatsView(APIView):
    def get(self, request):
        today = timezone.now().date()

        # --- 1. KEY STATS ---
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(is_active=True).count()

        # On Leave Today (from LeaveRequest)
        on_leave_count = LeaveRequest.objects.filter(
            status='Approved',
            start_date__lte=today,
            end_date__gte=today
        ).count()

        # Present Today (from Attendance)
        present_today = Attendance.objects.filter(
            date=today,
            status__in=['Present', 'Late', 'Working']
        ).count()

        # Open Positions
        open_positions = JobPosting.objects.filter(status='Active').count()

        # --- 2. DEPARTMENT DISTRIBUTION (Pie Chart) ---
        dept_counts = Employee.objects.values('department').annotate(count=Count('id'))
        department_data = [
            {'name': item['department'], 'value': item['count']}
            for item in dept_counts
        ]

        # --- 3. RECENT ACTIVITIES ---
        activities = []

        # A) New Employees (Last 3)
        recent_hires = Employee.objects.order_by('-date_of_joining')[:3]
        for emp in recent_hires:
            activities.append({
                'id': f"emp-{emp.id}",
                'action': 'New employee joined',
                'name': f"{emp.first_name} {emp.last_name}",
                'dept': emp.department,
                'time': str(emp.date_of_joining),
                'type': 'join'
            })

        # B) Approved Leaves (Last 3)
        recent_leaves = LeaveRequest.objects.filter(status='Approved').order_by('-created_at')[:3]
        for leave in recent_leaves:
            activities.append({
                'id': f"leave-{leave.id}",
                'action': 'Leave approved',
                'name': f"{leave.employee.first_name} {leave.employee.last_name}",
                'dept': leave.leave_type,
                'time': str(leave.created_at.date()),
                'type': 'leave'
            })

        # Sort activities by date (most recent first) and take top 5
        activities.sort(key=lambda x: x['time'], reverse=True)
        recent_activities = activities[:5]

        # --- 4. ATTENDANCE DATA (from real data) ---
        attendance_data = []
        from datetime import timedelta
        for i in range(5):
            day = today - timedelta(days=4-i)
            day_name = day.strftime('%a')
            present = Attendance.objects.filter(date=day, status__in=['Present', 'Late']).count()
            absent = Attendance.objects.filter(date=day, status='Absent').count()
            attendance_data.append({
                'name': day_name,
                'present': present,
                'absent': absent
            })

        # Construct Final Response
        data = {
            'stats': [
                {'title': 'Total Employees', 'value': total_employees, 'change': '+12%', 'trend': 'up', 'color': '#6366f1'},
                {'title': 'Present Today', 'value': present_today, 'change': '+5%', 'trend': 'up', 'color': '#22c55e'},
                {'title': 'On Leave', 'value': on_leave_count, 'change': '-2', 'trend': 'down', 'color': '#f59e0b'},
                {'title': 'Open Positions', 'value': open_positions, 'change': '+3', 'trend': 'up', 'color': '#ec4899'},
            ],
            'department_distribution': department_data,
            'recent_activities': recent_activities,
            'attendance_data': attendance_data
        }

        return Response(data)