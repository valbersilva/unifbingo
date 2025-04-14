from rest_framework import serializers
from .models import GameSession, DrawnNumber, GameAuditLog, GameHistory

class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = '__all__'


class DrawnNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrawnNumber
        fields = '__all__'


class GameAuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = GameAuditLog
        fields = ['id', 'session', 'actor_username', 'action', 'timestamp']


class GameHistorySerializer(serializers.ModelSerializer):
    winner_username = serializers.CharField(source='winner.username', read_only=True)

    class Meta:
        model = GameHistory
        fields = ['id', 'session', 'room_code', 'winner_username', 'winning_card_hash',
                  'drawn_numbers', 'started_at', 'ended_at', 'is_completed']
