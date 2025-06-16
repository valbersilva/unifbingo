from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import BingoRoom, BingoCard, RoomParticipant
from .serializers import BingoRoomSerializer, BingoCardSerializer
from .permissions import IsHostOrAdmin
from users.models import AuditLog
from game_session.models import GameSession  # necessário para verificar sessões ativas


class BingoRoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating and listing Bingo Rooms.
    Only hosts and admins can create.
    """
    queryset = BingoRoom.objects.all()
    serializer_class = BingoRoomSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsHostOrAdmin()]

    def perform_create(self, serializer):
        room = serializer.save(created_by=self.request.user)
        RoomParticipant.objects.create(user=self.request.user, room=room)
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

        if room.is_closed:
            return Response({"detail": "Room is closed."}, status=status.HTTP_403_FORBIDDEN)

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
            room = participant.room
            participant.delete()

            # Se a sala ficou vazia e não tem sessão ativa, exclui a sala
            room_empty = not RoomParticipant.objects.filter(room=room).exists()
            session_active = GameSession.objects.filter(room=room, is_active=True).exists()

            if room_empty and not session_active:
                AuditLog.objects.create(
                    actor=request.user,
                    action=f"Room {room.room_code} deleted automatically (empty and no active session)",
                    target=None
                )
                room.delete()

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


class DeleteRoomAPIView(APIView):
    """
    Allows the room creator to delete a room manually, if no session is active.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id):
        room = get_object_or_404(BingoRoom, id=room_id)

        if room.created_by != request.user:
            return Response({"detail": "Only the creator can delete this room."}, status=status.HTTP_403_FORBIDDEN)

        if GameSession.objects.filter(room=room, is_active=True).exists():
            return Response({"detail": "Cannot delete room with active session."}, status=status.HTTP_400_BAD_REQUEST)

        room.delete()

        AuditLog.objects.create(
            actor=request.user,
            action=f"Room {room.room_code} manually deleted by creator",
            target=None
        )

        return Response({"detail": "Room deleted successfully."}, status=status.HTTP_200_OK)


class RoomParticipantsView(APIView):
    """
    Lista todos os participantes de uma sala de bingo pelo room_code.
    O host aparece como role 'host' e os demais como 'player'.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, room_code):
        try:
            room = BingoRoom.objects.get(room_code=room_code)
        except BingoRoom.DoesNotExist:
            return Response({"detail": "Sala não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        participants = RoomParticipant.objects.filter(room=room)
        data = []
        # Adiciona o host
        data.append({
            "id": str(room.created_by.id),
            "name": room.created_by.username,
            "role": "host"
        })
        # Adiciona os jogadores (excluindo o host se ele também estiver em RoomParticipant)
        for p in participants:
            if p.user.id != room.created_by.id:
                data.append({
                    "id": str(p.user.id),
                    "name": p.user.username,
                    "role": "player"
                })
        return Response(data)
