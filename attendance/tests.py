from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Attendance
from employee.models import Employee
from datetime import date, time, timedelta
from django.utils import timezone


class AttendanceCheckInOutTests(TestCase):
    """Tests for attendance check-in/check-out system."""

    def setUp(self):
        self.client = APIClient()
        
        # Create employee
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.employee = Employee.objects.create(
            user=self.user,
            first_name='Test',
            last_name='Employee',
            employee_id='EMP001',
            email='test@example.com',
            phone='1234567890',
            gender='Male',
            department='Engineering',
            designation='Developer',
            date_of_joining=date.today(),
            role='employee'
        )
        
        self.client.force_authenticate(user=self.user)

    def test_check_in_creates_attendance_record(self):
        """Test that check-in creates attendance record correctly."""
        response = self.client.post('/api/attendance/check-in/', {
            'employee_id': 'EMP001'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Working')
        
        # Verify record exists
        attendance = Attendance.objects.get(employee=self.employee, date=date.today())
        self.assertIsNotNone(attendance.check_in)

    def test_double_check_in_blocked(self):
        """Test that double check-in is prevented."""
        # First check-in
        self.client.post('/api/attendance/check-in/', {'employee_id': 'EMP001'})
        
        # Second check-in should fail
        response = self.client.post('/api/attendance/check-in/', {'employee_id': 'EMP001'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Already checked in', response.data['error'])

    def test_check_out_before_check_in_blocked(self):
        """Test that check-out before check-in is prevented."""
        response = self.client.post('/api/attendance/check-out/', {'employee_id': 'EMP001'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_out_calculates_working_hours(self):
        """Test that check-out calculates working hours."""
        # Create attendance with check-in
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in=time(9, 0, 0),
            status='Working'
        )
        
        response = self.client.post('/api/attendance/check-out/', {'employee_id': 'EMP001'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('working_hours', response.data)

    def test_get_today_attendance(self):
        """Test getting today's attendance for an employee."""
        # Create attendance
        Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in=time(9, 0, 0),
            status='Working'
        )
        
        response = self.client.get('/api/attendance/today/EMP001/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_id'], 'EMP001')

    def test_monthly_report(self):
        """Test monthly attendance report."""
        # Create some attendance records
        Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in=time(9, 0),
            check_out=time(18, 0),
            status='Present'
        )
        
        month_str = date.today().strftime('%Y-%m')
        response = self.client.get(f'/api/attendance/report/?month={month_str}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('records', response.data)


class AttendanceStatusLogicTests(TestCase):
    """Tests for attendance status logic based on working hours."""

    def setUp(self):
        self.employee = Employee.objects.create(
            first_name='Status',
            last_name='Test',
            employee_id='EMP002',
            email='status@test.com',
            phone='9876543210',
            gender='Female',
            department='HR',
            designation='Manager',
            date_of_joining=date.today()
        )

    def test_half_day_for_4_to_8_hours(self):
        """Test Half Day status for 4-8 hours work."""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in=time(9, 0),
            check_out=time(14, 0)  # 5 hours
        )
        
        self.assertEqual(attendance.status, 'Half Day')

    def test_absent_for_less_than_4_hours(self):
        """Test Absent status for less than 4 hours work."""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in=time(9, 0),
            check_out=time(11, 0)  # 2 hours
        )
        
        self.assertEqual(attendance.status, 'Absent')

    def test_present_for_8_plus_hours(self):
        """Test Present status for 8+ hours work."""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in=time(9, 0),
            check_out=time(18, 0)  # 9 hours
        )
        
        self.assertIn(attendance.status, ['Present', 'Late'])

    def test_late_for_after_930(self):
        """Test Late status for check-in after 9:30 AM."""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in=time(10, 0),  # 10 AM (late)
            check_out=time(19, 0)  # 9 hours
        )
        
        self.assertEqual(attendance.status, 'Late')

    def test_working_status_during_shift(self):
        """Test Working status when checked in but not checked out."""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in=time(9, 0)
            # No check_out
        )
        
        self.assertEqual(attendance.status, 'Working')

    def test_unique_attendance_per_day(self):
        """Test that only one attendance record per employee per day is allowed."""
        Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            check_in=time(9, 0)
        )
        
        # Trying to create another should raise error
        with self.assertRaises(Exception):
            Attendance.objects.create(
                employee=self.employee,
                date=date.today(),
                check_in=time(10, 0)
            )
