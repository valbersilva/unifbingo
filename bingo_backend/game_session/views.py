from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import GameSession, DrawnNumber, GameAuditLog, GameHistory
from .serializers import (
    GameSessionSerializer,
    DrawnNumberSerializer,
    GameAuditLogSerializer,
    GameHistorySerializer
)
import random


class GameSessionViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        session = serializer.save()

        # FECHA AUTOMATICAMENTE A SALA
        room = session.room
        room.is_closed = True
        room.save()

        GameAuditLog.objects.create(
            session=session,
            actor=self.request.user,
            action="Game session started — room closed"
        )

    @action(detail=True, methods=['post'], url_path='draw-next')
    def draw_next_number(self, request, pk=None):
        session = get_object_or_404(GameSession, pk=pk)
        if not session.is_active:
            return Response({"detail": "This game session is not active."}, status=status.HTTP_400_BAD_REQUEST)

        drawn_numbers = DrawnNumber.objects.filter(session=session).values_list('number', flat=True)
        all_numbers = set(range(1, 76))
        remaining_numbers = list(all_numbers - set(drawn_numbers))

        if not remaining_numbers:
            return Response({"detail": "All numbers have already been drawn."}, status=status.HTTP_400_BAD_REQUEST)

        number = random.choice(remaining_numbers)
        draw = DrawnNumber.objects.create(session=session, number=number)

        GameAuditLog.objects.create(
            session=session,
            actor=request.user,
            action=f"Drew number {number}"
        )

        return Response(DrawnNumberSerializer(draw).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='end')
    def end_session(self, request, pk=None):
        session = get_object_or_404(GameSession, pk=pk)

        if request.user != session.room.created_by and request.user.role != 'admin':
            return Response({"detail": "Only the creator of the room or an admin can end this session."},
                            status=status.HTTP_403_FORBIDDEN)

        if not session.is_active:
            return Response({"detail": "This session is already ended."}, status=status.HTTP_400_BAD_REQUEST)

        session.is_active = False
        session.save()

        GameAuditLog.objects.create(
            session=session,
            actor=request.user,
            action="Ended the game session"
        )

        self._save_history(session)

        return Response({"detail": "Game session successfully ended."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='validate-bingo')
    def validate_bingo(self, request, pk=None):
        from bingo_room.models import BingoCard

        session = get_object_or_404(GameSession, pk=pk)

        if not session.is_active:
            return Response({"detail": "Game session is already ended."}, status=400)

        if session.winner:
            return Response({"detail": "A winner has already been declared."}, status=400)

        try:
            card = BingoCard.objects.get(owner=request.user, room=session.room)
        except BingoCard.DoesNotExist:
            return Response({"detail": "You do not have a card in this room."}, status=404)

        numbers_drawn = set(session.draws.values_list('number', flat=True))
        matrix = card.numbers

        for row in matrix:
            if all(num in numbers_drawn or num == 0 for num in row):
                return self._declare_winner(session, request.user, card, "row")

        for col in zip(*matrix):
            if all(num in numbers_drawn or num == 0 for num in col):
                return self._declare_winner(session, request.user, card, "column")

        if all(matrix[i][i] in numbers_drawn or matrix[i][i] == 0 for i in range(5)):
            return self._declare_winner(session, request.user, card, "main diagonal")

        if all(matrix[i][4 - i] in numbers_drawn or matrix[i][4 - i] == 0 for i in range(5)):
            return self._declare_winner(session, request.user, card, "anti-diagonal")

        GameAuditLog.objects.create(
            session=session,
            actor=request.user,
            action="Invalid BINGO attempt"
        )

        return Response({"detail": "BINGO is not valid."}, status=400)

    def _declare_winner(self, session, user, card, pattern):
        session.winner = user
        session.winning_card = card
        session.is_active = False
        session.save()

        GameAuditLog.objects.create(
            session=session,
            actor=user,
            action=f"🎉 BINGO VALIDATED — WINNER by {pattern}"
        )

        self._save_history(session)

        return Response({"detail": f"🎉 BINGO! You are the winner by {pattern}."}, status=200)

    def _save_history(self, session):
        GameHistory.objects.create(
            session=session,
            room_code=session.room.room_code,
            winner=session.winner,
            winning_card_hash=session.winning_card.card_hash if session.winning_card else None,
            drawn_numbers=list(session.draws.values_list('number', flat=True)),
            started_at=session.created_at,
            is_completed=True
        )


class DrawnNumberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DrawnNumber.objects.all()
    serializer_class = DrawnNumberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        session_id = self.request.query_params.get('session')
        if session_id:
            return self.queryset.filter(session__id=session_id)
        return self.queryset.none()


class GameAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GameAuditLog.objects.all()
    serializer_class = GameAuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        session_id = self.request.query_params.get('session')
        if session_id:
            return self.queryset.filter(session__id=session_id)
        return self.queryset.none()


class GameHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GameHistory.objects.all()
    serializer_class = GameHistorySerializer
    permission_classes = [IsAuthenticated]
