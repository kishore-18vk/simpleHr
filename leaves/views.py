# leaves/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LeaveRequest
from employee.models import Employee # Make sure to import Employee
from .serializers import LeaveRequestSerializer

class LeaveRequestView(APIView):
    
    def get(self, request):
        status_filter = request.query_params.get('status')
        emp_id = request.query_params.get('employee_id')
        
        # Order by newest first
        leaves = LeaveRequest.objects.all().order_by('-created_at')
        
        if status_filter and status_filter != 'All':
            leaves = leaves.filter(status=status_filter)
        if emp_id:
            leaves = leaves.filter(employee_id=emp_id)
            
        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response(serializer.data)

    def post(self, request):
        # 1. Create a mutable copy of the data so we can modify it
        data = request.data.copy()
        
        # 2. Check if 'employee' field is missing or empty
        if not data.get('employee'):
            # Ensure user is authenticated before checking their profile
            if not request.user or not request.user.is_authenticated:
                 return Response({"error": "You must be logged in or provide an Employee ID."}, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                # 3. Find the Employee profile linked to this User
                # (This assumes your Employee model has a OneToOneField or ForeignKey to User)
                current_emp = Employee.objects.get(user=request.user)
                
                # 4. Fill the missing field with the correct ID/slug
                data['employee'] = current_emp.employee_id 
                
            except Employee.DoesNotExist:
                return Response({"error": "Logged-in user is not linked to an Employee profile."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # Catch field name errors (e.g., if your model uses 'user_id' instead of 'user')
                return Response({"error": f"System error finding employee profile: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 5. Proceed with normal validation using the modified data
        serializer = LeaveRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Leave request submitted successfully", 
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk = request.data.get("id")
        if not pk:
            return Response({"error": "ID is required for update"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            leave = LeaveRequest.objects.get(id=pk)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = LeaveRequestSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Leave request updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk = request.data.get("id")
        if not pk:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            leave = LeaveRequest.objects.get(id=pk)
            leave.delete()
            return Response({"message": "Leave request deleted successfully"})
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found"}, status=status.HTTP_404_NOT_FOUND)