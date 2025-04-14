from rest_framework import serializers
from .models import GameSession, DrawnNumber, GameAuditLog

class GameSessionSerializer(serializers.ModelSerializer):
    room_code = serializers.CharField(source='room.room_code', read_only=True)

    class Meta:
        model = GameSession
        fields = ['id', 'room', 'room_code', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'room_code']

class DrawnNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrawnNumber
        fields = ['id', 'session', 'number', 'drawn_at']
        read_only_fields = ['id', 'drawn_at']

class GameAuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = GameAuditLog
        fields = ['id', 'session', 'actor_username', 'action', 'timestamp']
