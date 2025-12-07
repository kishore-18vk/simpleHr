from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, AssetRequestViewSet

router = DefaultRouter()
router.register(r'inventory', AssetViewSet, basename='inventory')
router.register(r'requests', AssetRequestViewSet, basename='requests')

urlpatterns = [
    path('', include(router.urls)),
]