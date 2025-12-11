from django.urls import path
from .views import (
    EmployeeProfileView,
    EmployeeRegisterView,
    SetPasswordView,
    EmployeeLoginView,
    MyProfileView,
    RegenerateTokenView
)

urlpatterns = [
    # Existing endpoint
    path('employee-profile/', EmployeeProfileView.as_view(), name='employee-profile'),
    
    # New Auth endpoints
    path('register/', EmployeeRegisterView.as_view(), name='employee-register'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('login/', EmployeeLoginView.as_view(), name='employee-login'),
    
    # Profile management
    path('me/', MyProfileView.as_view(), name='my-profile'),
    path('regenerate-token/', RegenerateTokenView.as_view(), name='regenerate-token'),
]
