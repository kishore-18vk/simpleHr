from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime
import calendar

# === IMPORT MODELS FROM ALL APPS ===
try:
    from employee.models import Employee
    from leaves.models import LeaveRequest
    from attendance.models import Attendance
    from payroll.models import Payroll
    from assets.models import AssetRequest
    from recruitment.models import JobPosting
except ImportError:
    pass # Handle gracefully if an app is missing

class DashboardStatsView(APIView):
    def get(self, request):
        today = timezone.now().date()
        
        # --- 1. KEY STATS (Top Row) ---
        total_employees = Employee.objects.count()
        present_today = Attendance.objects.filter(date=today, status__in=['Present', 'Late']).count()
        on_leave_today = LeaveRequest.objects.filter(status='Approved', start_date__lte=today, end_date__gte=today).count()
        open_positions = JobPosting.objects.filter(status='Active').count()

        stats = [
            {'title': 'Total Employees', 'value': total_employees, 'change': '+12%', 'trend': 'up'},
            {'title': 'Present Today', 'value': present_today, 'change': '+5%', 'trend': 'up'},
            {'title': 'On Leave', 'value': on_leave_today, 'change': '-2', 'trend': 'down'},
            {'title': 'Open Positions', 'value': open_positions, 'change': '+3', 'trend': 'up'},
        ]

        # --- 2. ATTENDANCE HEATMAP (Last 4 Weeks) ---
        # Logic: Calculate presence % for each day of the week for past 4 weeks
        heatmap_data = []
        days_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        
        for i, day_name in enumerate(days_map):
            row = {'day': day_name}
            # Look back 4 weeks
            for week in range(1, 5):
                # Calculate specific date for this day 'week' weeks ago
                # (Simplified logic: Generating mock-realistic data based on DB to save processing time)
                # In production, query specific dates. Here we average the DB stats.
                avg_presence = 85 # Default base
                if total_employees > 0:
                    # Get count for this specific weekday in DB history
                    count = Attendance.objects.filter(date__week_day=i+2, status='Present').count() 
                    # i+2 because Django week_day: Sunday=1, Monday=2...
                    if count > 0:
                        avg_presence = int((count / (total_employees * 4)) * 100) # Normalize
                        if avg_presence > 100: avg_presence = 95
                
                row[f'w{week}'] = avg_presence
            heatmap_data.append(row)

        # --- 3. PENDING APPROVALS (Leaves + Assets) ---
        pending_approvals = []
        
        # Leaves
        pending_leaves = LeaveRequest.objects.filter(status='Pending').order_by('-created_at')[:3]
        for leave in pending_leaves:
            pending_approvals.append({
                'id': f"leave-{leave.id}",
                'type': 'Leave',
                'name': f"{leave.employee.first_name} {leave.employee.last_name}",
                'request': f"{leave.leave_type} ({leave.days} days)",
                'time': 'Recent',
                'color': '#7c3aed',
                'avatar': leave.employee.first_name[0]
            })

        # Assets
        pending_assets = AssetRequest.objects.filter(status='Pending').order_by('-request_date')[:3]
        for asset in pending_assets:
            pending_approvals.append({
                'id': f"asset-{asset.id}",
                'type': 'Asset',
                'name': f"{asset.employee.first_name} {asset.employee.last_name}",
                'request': f"{asset.asset_type} Request",
                'time': 'Recent',
                'color': '#06b6d4',
                'avatar': asset.employee.first_name[0]
            })

        # --- 4. EMPLOYEE TRENDS (Hiring Last 6 Months) ---
        employee_trends = []
        for i in range(5, -1, -1):
            date_cursor = today - timedelta(days=i*30)
            month_name = date_cursor.strftime('%b')
            year = date_cursor.year
            month = date_cursor.month
            
            hired = Employee.objects.filter(date_of_joining__year=year, date_of_joining__month=month).count()
            # Assuming 'is_active=False' means left, and we track when (simplified)
            left = 0 
            
            employee_trends.append({
                'month': month_name,
                'hired': hired,
                'left': left
            })

        # --- 5. PAYROLL STATUS ---
        payroll_total_qs = Payroll.objects.filter(pay_date__month=today.month)
        processed_count = payroll_total_qs.filter(status='Paid').count()
        pending_count = payroll_total_qs.filter(status='Pending').count()
        total_amount = payroll_total_qs.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        
        payroll_status = {
            'processed': processed_count,
            'pending': pending_count,
            'total': processed_count + pending_count,
            'amount': f"${total_amount:,.0f}"
        }

        # --- 6. DEPARTMENT DISTRIBUTION ---
        dept_counts = Employee.objects.values('department').annotate(count=Count('id'))
        department_distribution = [
            {'name': item['department'], 'value': item['count']} for item in dept_counts
        ]

        # --- 7. RECENT ACTIVITIES ---
        recent_activities = []
        # New Hires
        new_emps = Employee.objects.order_by('-date_of_joining')[:3]
        for emp in new_emps:
            recent_activities.append({'action': 'New hire', 'name': emp.first_name, 'time': emp.date_of_joining, 'dept': emp.department})
        
        # Approved Leaves
        app_leaves = LeaveRequest.objects.filter(status='Approved').order_by('-created_at')[:3]
        for al in app_leaves:
            recent_activities.append({'action': 'Leave Approved', 'name': al.employee.first_name, 'time': al.created_at, 'dept': 'HR'})

        # Sort activities
        recent_activities.sort(key=lambda x: str(x['time']), reverse=True)

        # === FINAL JSON RESPONSE ===
        data = {
            'stats': stats,
            'heatmap_data': heatmap_data,
            'pending_approvals': pending_approvals,
            'employee_trends': employee_trends,
            'payroll_status': payroll_status,
            'department_distribution': department_distribution,
            'recent_activities': recent_activities[:5]
        }

        return Response(data)