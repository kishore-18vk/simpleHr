from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from .serializers import EmployeeSerializer

# 1️⃣ Get all employees
@api_view(['GET'])
def get_employees(request):
    name = request.GET.get('name')
    emp_id = request.GET.get('employee_id')

    employees = Employee.objects.all()

    if name:
        employees = employees.filter(name__icontains=name)

    if emp_id:
        employees = employees.filter(employee_id=emp_id)

    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_employee(request):
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Employee created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 3️⃣ Update employee
@api_view(['PUT'])
def update_employee(request):
    emp_id = request.data.get("id")
    try:
        employee = Employee.objects.get(id=emp_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EmployeeSerializer(employee, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Employee updated successfully"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 4️⃣ Delete employee
@api_view(['DELETE'])
def delete_employee(request):
    emp_id = request.data.get("id")
    try:
        employee = Employee.objects.get(id=emp_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    
    employee.delete()
    return Response({"message": "Employee deleted successfully"})
