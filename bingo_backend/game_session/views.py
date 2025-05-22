# game_session/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import GameSession, DrawnNumber, GameAuditLog, GameHistory
from bingo_room.models import BingoRoom, BingoCard
from .serializers import (
    GameSessionSerializer, DrawnNumberSerializer, GameAuditLogSerializer, GameHistorySerializer
)
import random
import uuid
from datetime import datetime

class GameSessionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        sessions = GameSession.objects.all()
        serializer = GameSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def create(self, request):
        room_id = request.data.get("room")
        if not room_id:
            return Response({"detail": "room field is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            room = BingoRoom.objects.get(id=room_id)
        except BingoRoom.DoesNotExist:
            return Response({"detail": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        session = GameSession(room_id=str(room.id))
        session.save()

        # Fecha a sala automaticamente
        room.is_closed = True
        room.save()

        # Cria log
        GameAuditLog(
            session_id=session.id,
            actor_id=str(request.user.id),
            action="Game session started — room closed"
        ).save()

        serializer = GameSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='draw-next')
    def draw_next_number(self, request, pk=None):
        try:
            session = GameSession.objects.get(id=pk)
        except GameSession.DoesNotExist:
            return Response({"detail": "Game session not found."}, status=status.HTTP_404_NOT_FOUND)
        if not session.is_active:
            return Response({"detail": "Game session is not active."}, status=status.HTTP_400_BAD_REQUEST)

        drawn_numbers = DrawnNumber.objects(session_id=session.id).only('number')
        drawn_set = {dn.number for dn in drawn_numbers}

        available_numbers = set(range(1, 76)) - drawn_set
        if not available_numbers:
            return Response({"detail": "No more numbers to draw."}, status=status.HTTP_400_BAD_REQUEST)

        number = random.choice(list(available_numbers))
        drawn_number = DrawnNumber(session_id=session.id, number=number)
        drawn_number.save()

        # Log
        GameAuditLog(session_id=session.id, actor_id=str(request.user.id), action=f"Number drawn: {number}").save()

        serializer = DrawnNumberSerializer(drawn_number)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='end')
    def end_session(self, request, pk=None):
        try:
            session = GameSession.objects.get(id=pk)
        except GameSession.DoesNotExist:
            return Response({"detail": "Game session not found."}, status=status.HTTP_404_NOT_FOUND)
        if not session.is_active:
            return Response({"detail": "Game session already ended."}, status=status.HTTP_400_BAD_REQUEST)

        winner_id = request.data.get("winner_id")
        winning_card_id = request.data.get("winning_card_id")

        session.is_active = False
        session.winner_id = winner_id
        session.winning_card_id = winning_card_id
        session.save()

        # Salvar histórico da partida
        drawn_numbers = DrawnNumber.objects(session_id=session.id)
        drawn_nums_list = [dn.number for dn in drawn_numbers]

        GameHistory(
            session_id=session.id,
            room_code="",  # Pode preencher com room_code se quiser
            winner_id=winner_id,
            winning_card_hash="",  # Buscar hash do cartão se necessário
            drawn_numbers=drawn_nums_list,
            started_at=session.created_at,
            ended_at=datetime.utcnow(),
            is_completed=True
        ).save()

        GameAuditLog(session_id=session.id, actor_id=str(request.user.id), action="Game session ended").save()

        return Response({"detail": "Game session ended."})
