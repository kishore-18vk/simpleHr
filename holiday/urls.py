from django.urls import path
from .views import HolidayListCreateView, HolidayDetailView

urlpatterns = [
    path('holidays/', HolidayListCreateView.as_view(), name='holiday-list-create'),
    path('holidays/<int:pk>/', HolidayDetailView.as_view(), name='holiday-detail'),
]
