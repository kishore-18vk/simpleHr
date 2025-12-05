from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Holiday
from .serializers import HolidaySerializer

class HolidayListCreateView(APIView):
    """
    GET: List all holidays
    POST: Create a new holiday
    """
    def get(self, request):
        holidays = Holiday.objects.all()
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = HolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HolidayDetailView(APIView):
    """
    GET: Retrieve a holiday
    PUT: Update a holiday
    DELETE: Delete a holiday
    """
    def get_object(self, pk):
        try:
            return Holiday.objects.get(pk=pk)
        except Holiday.DoesNotExist:
            return None

    def get(self, request, pk):
        holiday = self.get_object(pk)
        if not holiday:
            return Response({"error": "Holiday not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = HolidaySerializer(holiday)
        return Response(serializer.data)

    def put(self, request, pk):
        holiday = self.get_object(pk)
        if not holiday:
            return Response({"error": "Holiday not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = HolidaySerializer(holiday, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        holiday = self.get_object(pk)
        if not holiday:
            return Response({"error": "Holiday not found"}, status=status.HTTP_404_NOT_FOUND)
        holiday.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
