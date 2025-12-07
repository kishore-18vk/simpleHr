from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone

# === IMPORT MODELS FROM YOUR OTHER APPS ===
# If your app names are different, adjust these imports
try:
    from employee.models import Employee
except ImportError:
    Employee = None

try:
    from recruitment.models import JobPosting, LeaveRequest
    # Note: If LeaveRequest is in a separate 'leave' app, import it from there instead
except ImportError:
    JobPosting = None
    LeaveRequest = None

class DashboardStatsView(APIView):
    def get(self, request):
        today = timezone.now().date()
        
        # --- 1. KEY STATS ---
        total_employees = Employee.objects.count() if Employee else 0
        
        # Calculate Active Employees
        active_employees = Employee.objects.filter(is_active=True).count() if Employee else 0
        
        # Calculate On Leave Today
        on_leave_count = 0
        if LeaveRequest:
            on_leave_count = LeaveRequest.objects.filter(
                status='Approved',
                start_date__lte=today,
                end_date__gte=today
            ).count()
        
        present_today = active_employees - on_leave_count
        
        # Calculate Open Positions
        open_positions = 0
        if JobPosting:
            open_positions = JobPosting.objects.filter(status='Active').count()

        # --- 2. DEPARTMENT DISTRIBUTION (Pie Chart) ---
        department_data = []
        if Employee:
            dept_counts = Employee.objects.values('department').annotate(count=Count('id'))
            department_data = [
                {'name': item['department'], 'value': item['count']} 
                for item in dept_counts
            ]

        # --- 3. RECENT ACTIVITIES ---
        activities = []
        
        # A) New Employees (Last 3)
        if Employee:
            recent_hires = Employee.objects.order_by('-date_of_joining')[:3]
            for emp in recent_hires:
                activities.append({
                    'id': f"emp-{emp.id}",
                    'action': 'New employee joined',
                    'name': f"{emp.first_name} {emp.last_name}",
                    'dept': emp.department,
                    'time': emp.date_of_joining, 
                    'type': 'join'
                })

        # B) Approved Leaves (Last 3)
        if LeaveRequest:
            recent_leaves = LeaveRequest.objects.filter(status='Approved').order_by('-applied_on')[:3]
            for leave in recent_leaves:
                activities.append({
                    'id': f"leave-{leave.id}",
                    'action': 'Leave approved',
                    'name': f"{leave.employee_id}", 
                    'dept': leave.leave_type,
                    'time': leave.applied_on,
                    'type': 'leave'
                })

        # Sort activities by date (most recent first) and take top 5
        activities.sort(key=lambda x: str(x['time']), reverse=True)
        recent_activities = activities[:5]

        # --- 4. MOCK ATTENDANCE DATA (Area Chart) ---
        # Since we don't have an Attendance model yet, we send mock data for the graph
        attendance_data = [
            { 'name': 'Mon', 'present': int(total_employees * 0.9), 'absent': int(total_employees * 0.1) },
            { 'name': 'Tue', 'present': int(total_employees * 0.92), 'absent': int(total_employees * 0.08) },
            { 'name': 'Wed', 'present': int(total_employees * 0.88), 'absent': int(total_employees * 0.12) },
            { 'name': 'Thu', 'present': int(total_employees * 0.95), 'absent': int(total_employees * 0.05) },
            { 'name': 'Fri', 'present': int(total_employees * 0.85), 'absent': int(total_employees * 0.15) },
        ]

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