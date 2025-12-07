from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/employee/', include('employee.urls')),
    path('api/holidays/', include('holiday.urls')),
    path('api/', include('library.urls')),
    path('api/leaves/', include('leaves.urls')),
    path('api/recruitment/', include('recruitment.urls')),
]
