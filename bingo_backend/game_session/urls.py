from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameSessionViewSet, DrawnNumberViewSet, GameAuditLogViewSet, GameHistoryViewSet

router = DefaultRouter()
router.register('game-sessions', GameSessionViewSet, basename='game-session')
router.register('drawn-numbers', DrawnNumberViewSet, basename='drawn-number')
router.register('game-audit-logs', GameAuditLogViewSet, basename='game-audit-log')
router.register('game-history', GameHistoryViewSet, basename='game-history')

urlpatterns = [
    path('', include(router.urls)),
]
