from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AuditLogViewSet, CustomAuthToken

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')

urlpatterns = router.urls + [
    path('login/', CustomAuthToken.as_view(), name='login'),
]
