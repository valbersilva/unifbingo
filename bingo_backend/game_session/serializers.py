from rest_framework import serializers

class GameSessionSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    room_id = serializers.CharField()
    created_at = serializers.DateTimeField()
    is_active = serializers.BooleanField()
    winner_id = serializers.CharField(allow_null=True, required=False)
    winning_card_id = serializers.UUIDField(allow_null=True, required=False)

class DrawnNumberSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    session_id = serializers.UUIDField()
    number = serializers.IntegerField()
    drawn_at = serializers.DateTimeField()

class GameAuditLogSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    session_id = serializers.UUIDField()
    actor_id = serializers.CharField(allow_null=True)
    action = serializers.CharField()
    timestamp = serializers.DateTimeField()

class GameHistorySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    session_id = serializers.UUIDField()
    room_code = serializers.CharField()
    winner_id = serializers.CharField(allow_null=True)
    winning_card_hash = serializers.CharField(allow_null=True)
    drawn_numbers = serializers.ListField(child=serializers.IntegerField())
    started_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField()
    is_completed = serializers.BooleanField()