from django.db import models
from bingo_room.models import BingoRoom, BingoCard
from users.models import User
import uuid

class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.OneToOneField(BingoRoom, on_delete=models.CASCADE, related_name='game_session')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_sessions')
    winning_card = models.ForeignKey(BingoCard, null=True, blank=True, on_delete=models.SET_NULL, related_name='winning_sessions')

    def __str__(self):
        return f"Game for Room {self.room.room_code}"


class DrawnNumber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='draws')
    number = models.PositiveSmallIntegerField()
    drawn_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'number')
        ordering = ['drawn_at']

    def __str__(self):
        return f"{self.number} in {self.session.room.room_code}"


class GameAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='audit_logs')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='game_actions')
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} - {self.actor.username if self.actor else 'System'} - {self.action}"


class GameHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(GameSession, on_delete=models.CASCADE, related_name='history')
    room_code = models.CharField(max_length=10)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='victory_history')
    winning_card_hash = models.CharField(max_length=64, null=True, blank=True)
    drawn_numbers = models.JSONField()
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=True)

    class Meta:
        ordering = ['-ended_at']

    def __str__(self):
        return f"History for Room {self.room_code}"
