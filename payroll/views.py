from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from .models import Payroll
from .serializers import PayrollSerializer
from employee.models import Employee  # Import for batch generation

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.select_related('employee').all().order_by('-pay_date')
    serializer_class = PayrollSerializer

    # 1. Dashboard Stats (Total, Paid, Pending) - INR Currency
    @action(detail=False, methods=['get'])
    def payroll_stats(self, request):
        total_payroll = Payroll.objects.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        paid_amount = Payroll.objects.filter(status='Paid').aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        pending_amount = Payroll.objects.filter(status='Pending').aggregate(Sum('net_salary'))['net_salary__sum'] or 0

        stats = [
            {'label': 'Total Payroll', 'value': f"₹{total_payroll:,.2f}", 'color': '#6366f1', 'icon': 'dollar'},
            {'label': 'Paid', 'value': f"₹{paid_amount:,.2f}", 'color': '#22c55e', 'icon': 'trending'},
            {'label': 'Pending', 'value': f"₹{pending_amount:,.2f}", 'color': '#f59e0b', 'icon': 'calendar'},
        ]
        return Response(stats)

    # 2. Run Payroll (Batch Generate for all active employees)
    @action(detail=False, methods=['post'])
    def run_payroll(self, request):
        employees = Employee.objects.filter(is_active=True)
        created_count = 0
        current_month = timezone.now().month
        current_year = timezone.now().year

        for emp in employees:
            # Check if payroll already exists for this Employee ID this month
            exists = Payroll.objects.filter(
                employee=emp, 
                pay_date__month=current_month,
                pay_date__year=current_year
            ).exists()

            if not exists:
                Payroll.objects.create(
                    employee=emp, 
                    basic_salary=emp.basic_salary or 5000,
                    allowances=500, 
                    deductions=200, 
                    status='Pending'
                )
                created_count += 1
                
        if created_count > 0:
            return Response({'message': f'Successfully generated payroll for {created_count} employees.'})
        else:
            return Response({'message': 'Payroll for this month is up to date.'})

    # 3. Mark payroll as Paid
    @action(detail=True, methods=['post', 'patch'])
    def mark_paid(self, request, pk=None):
        try:
            payroll = Payroll.objects.get(pk=pk)
            payroll.status = 'Paid'
            payroll.save()
            return Response({'message': f'Payroll #{pk} marked as Paid.', 'status': 'Paid'})
        except Payroll.DoesNotExist:
            return Response({'error': 'Payroll not found'}, status=status.HTTP_404_NOT_FOUND)

    # 4. Update basic salary for an employee
    @action(detail=False, methods=['post'])
    def update_salary(self, request):
        employee_id = request.data.get('employee_id')  # e.g. "EMP006"
        new_salary = request.data.get('basic_salary')

        if not employee_id or not new_salary:
            return Response({'error': 'employee_id and basic_salary are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            emp = Employee.objects.get(employee_id=employee_id)
            emp.basic_salary = new_salary
            emp.save()
            return Response({
                'message': f'Basic salary updated for {emp.first_name} {emp.last_name}',
                'employee_id': employee_id,
                'basic_salary': f'₹{new_salary}'
            })
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)