from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import JobPosting
from .serializers import JobPostingSerializer

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all().order_by('-posted_date')
    serializer_class = JobPostingSerializer

    # API Endpoint: /api/recruitment/jobs/dashboard_stats/
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        total_jobs = JobPosting.objects.count()
        open_positions = JobPosting.objects.filter(status='Active').count()
        # Sum all applicants from all jobs
        total_applicants = JobPosting.objects.aggregate(Sum('applicants_count'))['applicants_count__sum'] or 0
        
        # Static data for demo (since we don't have an 'Application' model yet)
        in_progress = 34 
        hired_this_month = 5

        stats = [
            {'label': 'Open Positions', 'value': open_positions, 'color': '#6366f1'},
            {'label': 'Total Applicants', 'value': total_applicants, 'color': '#22c55e'},
            {'label': 'In Progress', 'value': in_progress, 'color': '#f59e0b'},
            {'label': 'Hired This Month', 'value': hired_this_month, 'color': '#ec4899'},
        ]
        return Response(stats)