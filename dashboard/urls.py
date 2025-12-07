from django.urls import path
from .views import DashboardStatsView

urlpatterns = [
    # API Path: /api/dashboard/
    path('', DashboardStatsView.as_view(), name='dashboard-stats'),
]