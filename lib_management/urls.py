from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # LOGIN ROUTES
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/', TokenObtainPairView.as_view(), name='login'),  # <––– IMPORTANT FIX
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # APP ROUTES
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
