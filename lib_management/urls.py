from django.contrib import admin
from django.urls import path, include
# === 1. IMPORT THESE VIEWS ===
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Refresh Token

    path('api/employee/', include('employee.urls')),
    path('api/holidays/', include('holiday.urls')),
    path('api/', include('library.urls')),
    path('api/leaves/', include('leaves.urls')),
    path('api/recruitment/', include('recruitment.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/payroll/', include('payroll.urls')), 
    path('api/onboarding/', include('onboarding.urls')),
    path('api/assets/', include('assets.urls')),
    path('api/settings/', include('settings_app.urls')),
]