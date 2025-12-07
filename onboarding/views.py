from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import OnboardingTask
from .serializers import OnboardingTaskSerializer, NewHireSerializer
from employee.models import Employee

class OnboardingViewSet(viewsets.ModelViewSet):
    queryset = OnboardingTask.objects.all()
    serializer_class = OnboardingTaskSerializer

    # 1. Get tasks for a specific employee (e.g., ?employee_id=1)
    def get_queryset(self):
        queryset = super().get_queryset()
        emp_id = self.request.query_params.get('employee_id')
        if emp_id:
            queryset = queryset.filter(employee_id=emp_id)
        return queryset

    # 2. Get "New Hires" list with progress (Joined in last 60 days)
    @action(detail=False, methods=['get'])
    def new_hires(self, request):
        cutoff_date = timezone.now().date() - timedelta(days=60)
        # Fetch employees joined recently
        recent_hires = Employee.objects.filter(date_of_joining__gte=cutoff_date).order_by('-date_of_joining')
        
        serializer = NewHireSerializer(recent_hires, many=True)
        return Response(serializer.data)

    # 3. Helper to auto-generate default tasks for an employee
    @action(detail=False, methods=['post'])
    def generate_tasks(self, request):
        emp_id = request.data.get('employee_id')
        if not emp_id:
            return Response({'error': 'Employee ID required'}, status=400)
        
        try:
            employee = Employee.objects.get(id=emp_id)
            default_tasks = [
                {'title': 'Complete Profile', 'desc': 'Fill personal details', 'days': 2},
                {'title': 'Upload Documents', 'desc': 'ID and Certificates', 'days': 3},
                {'title': 'IT Setup', 'desc': 'Get laptop and email access', 'days': 5},
                {'title': 'Training Videos', 'desc': 'Watch security compliance', 'days': 7},
            ]
            
            for task in default_tasks:
                OnboardingTask.objects.create(
                    employee=employee,
                    title=task['title'],
                    description=task['desc'],
                    due_date=timezone.now().date() + timedelta(days=task['days'])
                )
            return Response({'message': 'Default tasks created'})
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=404)