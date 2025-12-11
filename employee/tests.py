from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Employee
from datetime import date


class EmployeeAuthenticationTests(TestCase):
    """Tests for employee authentication system."""

    def setUp(self):
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        
        # Create admin employee profile
        self.admin_employee = Employee.objects.create(
            user=self.admin_user,
            first_name='Admin',
            last_name='User',
            employee_id='EMP001',
            email='admin@test.com',
            phone='1234567890',
            gender='Male',
            department='Management',
            designation='Admin',
            date_of_joining=date.today(),
            role='admin'
        )

    def test_admin_can_register_employee(self):
        """Test that admin can successfully register a new employee."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'employee_id': 'EMP002',
            'username': 'johndoe',
            'email': 'john@test.com',
            'phone': '9876543210',
            'gender': 'Male',
            'department': 'Engineering',
            'designation': 'Developer',
            'date_of_joining': str(date.today()),
            'role': 'employee'
        }
        
        response = self.client.post('/api/employee/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('invitation_token', response.data)
        self.assertIn('set_password_url', response.data)

    def test_invalid_registration_without_emp_in_id(self):
        """Test that registration fails if employee_id doesn't contain EMP."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'employee_id': 'E002',
            'username': 'janedoe',
            'email': 'jane@test.com',
            'phone': '9876543211',
            'gender': 'Female',
            'department': 'HR',
            'designation': 'Manager',
            'date_of_joining': str(date.today()),
        }
        
        response = self.client.post('/api/employee/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_password_with_valid_token(self):
        """Test that employee can set password with valid token."""
        self.client.force_authenticate(user=self.admin_user)
        
        # First register employee
        register_data = {
            'first_name': 'Test',
            'last_name': 'Employee',
            'employee_id': 'EMP003',
            'username': 'testemployee',
            'phone': '1111111111',
            'gender': 'Male',
            'department': 'IT',
            'designation': 'Analyst',
            'date_of_joining': str(date.today()),
        }
        
        response = self.client.post('/api/employee/register/', register_data)
        token = response.data['invitation_token']
        
        # Set password
        self.client.force_authenticate(user=None)
        password_data = {
            'token': token,
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        response = self.client.post('/api/employee/set-password/', password_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_password_with_invalid_token(self):
        """Test that setting password fails with invalid token."""
        data = {
            'token': 'invalid_token_12345',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        response = self.client.post('/api/employee/set-password/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employee_login_returns_role(self):
        """Test that login returns correct role information."""
        # Create employee with password
        user = User.objects.create_user(
            username='logintest',
            email='login@test.com',
            password='TestPass123!'
        )
        
        employee = Employee.objects.create(
            user=user,
            first_name='Login',
            last_name='Test',
            employee_id='EMP004',
            email='login@test.com',
            phone='2222222222',
            gender='Male',
            department='Sales',
            designation='Executive',
            date_of_joining=date.today(),
            role='employee'
        )
        
        response = self.client.post('/api/employee/login/', {
            'username': 'logintest',
            'password': 'TestPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('employee', response.data)
        self.assertEqual(response.data['employee']['role'], 'employee')

    def test_employee_cannot_access_admin_routes(self):
        """Test that employee role cannot access admin-only endpoints."""
        user = User.objects.create_user(
            username='regularuser',
            email='regular@test.com',
            password='TestPass123!'
        )
        
        employee = Employee.objects.create(
            user=user,
            first_name='Regular',
            last_name='User',
            employee_id='EMP005',
            email='regular@test.com',
            phone='3333333333',
            gender='Female',
            department='Support',
            designation='Agent',
            date_of_joining=date.today(),
            role='employee'
        )
        
        self.client.force_authenticate(user=user)
        
        # Try to register new employee (admin-only)
        data = {
            'first_name': 'New',
            'last_name': 'Employee',
            'employee_id': 'EMP006',
            'username': 'newemployee',
            'phone': '4444444444',
            'gender': 'Male',
            'department': 'IT',
            'designation': 'Developer',
            'date_of_joining': str(date.today()),
        }
        
        response = self.client.post('/api/employee/register/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EmployeeTokenTests(TestCase):
    """Tests for invitation token functionality."""

    def test_token_generation(self):
        """Test that token is generated correctly."""
        employee = Employee.objects.create(
            first_name='Token',
            last_name='Test',
            employee_id='EMP100',
            email='token@test.com',
            phone='5555555555',
            gender='Male',
            department='IT',
            designation='Tester',
            date_of_joining=date.today()
        )
        
        token = employee.generate_invitation_token()
        self.assertIsNotNone(token)
        self.assertIsNotNone(employee.token_expires)
        self.assertTrue(len(token) > 20)

    def test_token_validation(self):
        """Test token validation logic."""
        employee = Employee.objects.create(
            first_name='Validate',
            last_name='Test',
            employee_id='EMP101',
            email='validate@test.com',
            phone='6666666666',
            gender='Female',
            department='HR',
            designation='Manager',
            date_of_joining=date.today()
        )
        
        token = employee.generate_invitation_token()
        
        # Valid token
        self.assertTrue(employee.is_token_valid(token))
        
        # Invalid token
        self.assertFalse(employee.is_token_valid('wrong_token'))

    def test_token_clearing(self):
        """Test that token is cleared after password is set."""
        employee = Employee.objects.create(
            first_name='Clear',
            last_name='Test',
            employee_id='EMP102',
            email='clear@test.com',
            phone='7777777777',
            gender='Male',
            department='Finance',
            designation='Accountant',
            date_of_joining=date.today()
        )
        
        employee.generate_invitation_token()
        employee.clear_token()
        
        self.assertIsNone(employee.invitation_token)
        self.assertIsNone(employee.token_expires)
