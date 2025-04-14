from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import BingoRoom, BingoCard, RoomParticipant
from .serializers import BingoRoomSerializer, BingoCardSerializer
from .permissions import IsHostOrAdmin
from users.models import AuditLog


class BingoRoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating and listing Bingo Rooms.
    Only hosts and admins can create.
    """
    queryset = BingoRoom.objects.all()
    serializer_class = BingoRoomSerializer
    permission_classes = [IsAuthenticated, IsHostOrAdmin]

    def perform_create(self, serializer):
        room = serializer.save(created_by=self.request.user)
        AuditLog.objects.create(
            actor=self.request.user,
            action=f"Created Bingo Room with code {room.room_code}",
            target=None
        )


class BingoCardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for generating and listing Bingo Cards.
    Only allowed if user is in the room.
    """
    queryset = BingoCard.objects.all()
    serializer_class = BingoCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BingoCard.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        room = serializer.validated_data.get('room')

        try:
            participant = RoomParticipant.objects.get(user=user)
            if participant.room != room:
                raise ValueError("User must be in the selected room to generate a card.")
        except RoomParticipant.DoesNotExist:
            raise ValueError("User must join the room before generating a card.")

        serializer.save(owner=user)


class JoinRoomAPIView(APIView):
    """
    Allows user to join a room if not already in one.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        room_id = request.data.get("room")
        room = get_object_or_404(BingoRoom, id=room_id)

        if RoomParticipant.objects.filter(user=request.user).exists():
            return Response({"detail": "User already in a room."}, status=status.HTTP_400_BAD_REQUEST)

        RoomParticipant.objects.create(user=request.user, room=room)
        return Response({"detail": f"User joined room {room.room_code}."}, status=status.HTTP_200_OK)


class LeaveRoomAPIView(APIView):
    """
    Allows user to leave the current room.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            participant = RoomParticipant.objects.get(user=request.user)
            participant.delete()
            return Response({"detail": "User left the room."}, status=status.HTTP_204_NO_CONTENT)
        except RoomParticipant.DoesNotExist:
            return Response({"detail": "User is not in any room."}, status=status.HTTP_400_BAD_REQUEST)


class MyRoomAPIView(APIView):
    """
    Returns the current room of the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            participant = RoomParticipant.objects.get(user=request.user)
            return Response({"room": BingoRoomSerializer(participant.room).data})
        except RoomParticipant.DoesNotExist:
            return Response({"room": None})
