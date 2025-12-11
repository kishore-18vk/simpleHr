from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Employee
from .serializers import (
    EmployeeSerializer, 
    EmployeeRegisterSerializer, 
    SetPasswordSerializer,
    EmployeeLoginSerializer,
    EmployeeProfileSerializer
)
from .permissions import IsAdmin, IsEmployee


class EmployeeProfileView(APIView):
    """CRUD operations for employee profiles (Admin access)."""
    
    def get(self, request):
        emp_id = request.query_params.get('employee_id')
        dept = request.query_params.get('department')
        employees = Employee.objects.all()
        if emp_id:
            employees = employees.filter(employee_id=emp_id)
        if dept:
            employees = employees.filter(department__icontains=dept)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Employee profile created successfully", 
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk = request.data.get("id")
        if not pk:
            return Response({"error": "ID is required for update"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(id=pk)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Employee profile updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk = request.data.get("id")
        if not pk:
            return Response({"error": "ID is required for deletion"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(id=pk)
            employee.delete()
            return Response({"message": "Employee profile deleted successfully"})
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)


class EmployeeRegisterView(APIView):
    """
    Admin creates a new employee account.
    Returns invitation token for the employee to set their password.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = EmployeeRegisterSerializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save()
            return Response({
                "message": "Employee registered successfully",
                "employee_id": employee.employee_id,
                "username": employee.user.username,
                "invitation_token": employee.invitation_token,
                "token_expires": employee.token_expires.isoformat(),
                "set_password_url": f"/api/employee/set-password/?token={employee.invitation_token}"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordView(APIView):
    """
    Employee sets their password using invitation token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        
        # Find employee with this token
        try:
            employee = Employee.objects.get(invitation_token=token)
        except Employee.DoesNotExist:
            return Response({
                "error": "Invalid or expired token"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate token
        if not employee.is_token_valid(token):
            return Response({
                "error": "Token has expired. Please contact admin for a new invitation."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set password
        if employee.user:
            employee.user.set_password(password)
            employee.user.save()
            employee.clear_token()
            
            return Response({
                "message": "Password set successfully. You can now login.",
                "username": employee.user.username
            }, status=status.HTTP_200_OK)
        
        return Response({
            "error": "No user account linked to this employee"
        }, status=status.HTTP_400_BAD_REQUEST)


class EmployeeLoginView(APIView):
    """
    Employee login - returns JWT tokens with role information.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmployeeLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                "error": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                "error": "Account is disabled"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get employee profile
        try:
            employee = user.employee_profile
        except Employee.DoesNotExist:
            return Response({
                "error": "No employee profile found for this user"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not employee.is_active:
            return Response({
                "error": "Employee account is deactivated"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "employee": {
                "id": employee.id,
                "employee_id": employee.employee_id,
                "name": f"{employee.first_name} {employee.last_name}",
                "department": employee.department,
                "designation": employee.designation,
                "role": employee.role
            }
        }, status=status.HTTP_200_OK)


class MyProfileView(APIView):
    """
    Employee views their own profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            return Response({
                "error": "No employee profile found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EmployeeProfileSerializer(employee)
        return Response(serializer.data)

    def put(self, request):
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            return Response({
                "error": "No employee profile found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Only allow updating certain fields
        allowed_fields = ['phone', 'address']
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = EmployeeProfileSerializer(employee, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegenerateTokenView(APIView):
    """
    Admin regenerates invitation token for an employee.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        employee_id = request.data.get('employee_id')
        
        if not employee_id:
            return Response({
                "error": "employee_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({
                "error": "Employee not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        token = employee.generate_invitation_token()
        
        return Response({
            "message": "New invitation token generated",
            "employee_id": employee.employee_id,
            "invitation_token": token,
            "token_expires": employee.token_expires.isoformat(),
            "set_password_url": f"/api/employee/set-password/?token={token}"
        }, status=status.HTTP_200_OK)
