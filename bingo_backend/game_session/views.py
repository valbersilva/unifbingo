from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import GameSession, DrawnNumber, GameAuditLog
from .serializers import GameSessionSerializer, DrawnNumberSerializer, GameAuditLogSerializer
import random

class GameSessionViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticated]

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
