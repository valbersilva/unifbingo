from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import BingoRoomSerializer, BingoCardSerializer
from .models import BingoRoom, BingoCard
import uuid

class BingoRoomViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        rooms = BingoRoom.objects.all()
        serializer = BingoRoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def create(self, request):
        # Cria a sala com room_code único simples
        room_code = str(uuid.uuid4())[:8]
        created_by_id = str(request.user.id)  # espere que user.id seja string ou adapte

        room = BingoRoom(room_code=room_code, created_by_id=created_by_id, participants=[])
        room.save()
        serializer = BingoRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            room = BingoRoom.objects.get(id=pk)
        except BingoRoom.DoesNotExist:
            return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BingoRoomSerializer(room)
        return Response(serializer.data)