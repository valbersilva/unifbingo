from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    BingoRoomViewSet,
    BingoCardViewSet,
    JoinRoomAPIView,
    LeaveRoomAPIView,
    MyRoomAPIView,
)

router = DefaultRouter()
router.register(r'bingo-rooms', BingoRoomViewSet, basename='bingoroom')
router.register(r'bingo-cards', BingoCardViewSet, basename='bingocard')

urlpatterns = router.urls + [
    path('join-room/', JoinRoomAPIView.as_view(), name='join-room'),
    path('leave-room/', LeaveRoomAPIView.as_view(), name='leave-room'),
    path('my-room/', MyRoomAPIView.as_view(), name='my-room'),
]
