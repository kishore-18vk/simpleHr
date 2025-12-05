from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeProfileView(APIView):
    
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