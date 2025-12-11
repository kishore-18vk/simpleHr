from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from .models import Payroll, PayrollStatusLog
from .serializers import PayrollSerializer, PayrollStatusLogSerializer, SetPayrollStatusSerializer
from employee.models import Employee
from employee.permissions import IsAdmin


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
                payroll_month=current_month,
                payroll_year=current_year
            ).exists()

            if not exists:
                Payroll.objects.create(
                    employee=emp, 
                    basic_salary=emp.basic_salary or 5000,
                    allowances=500, 
                    deductions=200, 
                    status='Pending',
                    payroll_month=current_month,
                    payroll_year=current_year
                )
                created_count += 1
                
        if created_count > 0:
            return Response({'message': f'Successfully generated payroll for {created_count} employees.'})
        else:
            return Response({'message': 'Payroll for this month is up to date.'})

    # 3. Mark payroll as Paid (legacy endpoint)
    @action(detail=True, methods=['post', 'patch'])
    def mark_paid(self, request, pk=None):
        try:
            payroll = Payroll.objects.get(pk=pk)
            
            # Validation: Cannot set Paid twice
            if payroll.status == 'Paid':
                return Response({
                    'error': 'Payroll is already marked as Paid',
                    'payroll_id': pk,
                    'current_status': payroll.status
                }, status=status.HTTP_400_BAD_REQUEST)
            
            old_status = payroll.status
            payroll.status = 'Paid'
            payroll.save()
            
            # Log the status change
            PayrollStatusLog.objects.create(
                payroll=payroll,
                old_status=old_status,
                new_status='Paid',
                changed_by=request.user if request.user.is_authenticated else None,
                notes='Marked as paid via mark_paid endpoint'
            )
            
            return Response({
                'message': f'Payroll #{pk} marked as Paid.',
                'status': 'Paid',
                'employee_id': payroll.employee.employee_id
            })
        except Payroll.DoesNotExist:
            return Response({'error': 'Payroll not found'}, status=status.HTTP_404_NOT_FOUND)

    # 4. Update basic salary for an employee
    @action(detail=False, methods=['post'])
    def update_salary(self, request):
        employee_id = request.data.get('employee_id')
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

    # ========== NEW ENDPOINTS ==========

    # 5. Set Payroll Status with validation and logging
    @action(detail=False, methods=['post'], url_path='set-status')
    def set_status(self, request):
        """
        Set payroll status for an employee.
        Validates: cannot set Paid twice, status cannot be empty.
        Logs all status changes.
        """
        serializer = SetPayrollStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        new_status = data['status']
        notes = data.get('notes', '')
        
        # Find payroll record
        if data.get('payroll_id'):
            try:
                payroll = Payroll.objects.get(id=data['payroll_id'])
            except Payroll.DoesNotExist:
                return Response({'error': 'Payroll not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Find latest payroll for employee
            try:
                employee = Employee.objects.get(employee_id=data['employee_id'])
                payroll = Payroll.objects.filter(employee=employee).order_by('-pay_date').first()
                if not payroll:
                    return Response({
                        'error': 'No payroll record found for this employee'
                    }, status=status.HTTP_404_NOT_FOUND)
            except Employee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validation: Cannot set Paid twice
        if payroll.status == 'Paid' and new_status == 'Paid':
            return Response({
                'error': 'Cannot set status to Paid - payroll is already Paid',
                'payroll_id': payroll.id,
                'employee_id': payroll.employee.employee_id,
                'current_status': payroll.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Log the status change
        old_status = payroll.status
        PayrollStatusLog.objects.create(
            payroll=payroll,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user if request.user.is_authenticated else None,
            notes=notes
        )
        
        # Update status
        payroll.status = new_status
        payroll.save()
        
        return Response({
            'message': f'Payroll status updated from {old_status} to {new_status}',
            'payroll_id': payroll.id,
            'employee_id': payroll.employee.employee_id,
            'employee_name': f"{payroll.employee.first_name} {payroll.employee.last_name}",
            'old_status': old_status,
            'new_status': new_status
        })

    # 6. Get payroll for specific employee
    @action(detail=False, methods=['get'], url_path='employee/(?P<employee_id>[^/.]+)')
    def get_employee_payroll(self, request, employee_id=None):
        """
        Get all payroll records for a specific employee.
        """
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        payrolls = Payroll.objects.filter(employee=employee).order_by('-pay_date')
        serializer = PayrollSerializer(payrolls, many=True)
        
        return Response({
            'employee_id': employee_id,
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'total_records': payrolls.count(),
            'payrolls': serializer.data
        })

    # 7. Get all payroll records (with filters)
    @action(detail=False, methods=['get'], url_path='all')
    def get_all(self, request):
        """
        Get all payroll records with optional filters.
        Query params: status, month, year
        """
        queryset = Payroll.objects.select_related('employee').all()
        
        # Apply filters
        status_filter = request.query_params.get('status')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if month:
            queryset = queryset.filter(payroll_month=int(month))
        if year:
            queryset = queryset.filter(payroll_year=int(year))
        
        queryset = queryset.order_by('-pay_date')
        serializer = PayrollSerializer(queryset, many=True)
        
        # Summary stats
        total = queryset.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        paid = queryset.filter(status='Paid').aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        pending = queryset.filter(status='Pending').aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        
        return Response({
            'summary': {
                'total_amount': f"₹{total:,.2f}",
                'paid_amount': f"₹{paid:,.2f}",
                'pending_amount': f"₹{pending:,.2f}",
                'total_records': queryset.count(),
                'paid_count': queryset.filter(status='Paid').count(),
                'pending_count': queryset.filter(status='Pending').count()
            },
            'payrolls': serializer.data
        })

    # 8. Get status change logs
    @action(detail=False, methods=['get'], url_path='logs')
    def get_logs(self, request):
        """
        Get payroll status change logs.
        Query params: payroll_id, employee_id
        """
        queryset = PayrollStatusLog.objects.select_related('payroll', 'changed_by').all()
        
        payroll_id = request.query_params.get('payroll_id')
        employee_id = request.query_params.get('employee_id')
        
        if payroll_id:
            queryset = queryset.filter(payroll_id=payroll_id)
        if employee_id:
            queryset = queryset.filter(payroll__employee__employee_id=employee_id)
        
        queryset = queryset.order_by('-changed_at')[:100]  # Limit to last 100 logs
        serializer = PayrollStatusLogSerializer(queryset, many=True)
        
        return Response({
            'total_logs': queryset.count(),
            'logs': serializer.data
        })