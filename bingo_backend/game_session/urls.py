from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import GameSessionViewSet, DrawnNumberViewSet, GameAuditLogViewSet

router = DefaultRouter()
router.register(r'game-sessions', GameSessionViewSet, basename='game-session')
router.register(r'drawn-numbers', DrawnNumberViewSet, basename='drawn-number')
router.register(r'game-audit-logs', GameAuditLogViewSet, basename='game-audit-log')

urlpatterns = [
    path('', include(router.urls))
]
