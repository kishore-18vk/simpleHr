from django.urls import path
from .views import get_employees, create_employee, update_employee, delete_employee

urlpatterns = [
    path('get/', get_employees, name='get-employees'),
    path('create/', create_employee, name='create-employee'),
    path('update/', update_employee, name='update-employee'),
    path('delete/', delete_employee, name='delete-employee'),
]
