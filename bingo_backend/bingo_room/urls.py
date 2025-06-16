from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    BingoRoomViewSet,
    BingoCardViewSet,
    JoinRoomAPIView,
    LeaveRoomAPIView,
    MyRoomAPIView,
    DeleteRoomAPIView,  # NOVO ENDPOINT
    RoomParticipantsView,
)

router = DefaultRouter()
router.register(r'bingo-rooms', BingoRoomViewSet, basename='bingoroom')
router.register(r'bingo-cards', BingoCardViewSet, basename='bingocard')

urlpatterns = router.urls + [
    path('join-room/', JoinRoomAPIView.as_view(), name='join-room'),
    path('leave-room/', LeaveRoomAPIView.as_view(), name='leave-room'),
    path('my-room/', MyRoomAPIView.as_view(), name='my-room'),
    path('delete-room/<uuid:room_id>/', DeleteRoomAPIView.as_view(), name='delete-room'),  # <- aqui
    path('bingo-rooms/<str:room_code>/participants/', RoomParticipantsView.as_view(), name='room-participants'),
]
