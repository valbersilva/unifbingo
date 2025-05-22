from rest_framework import serializers

class RoomParticipantSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    username = serializers.CharField()
    joined_at = serializers.DateTimeField()

class BingoCardSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    room = serializers.CharField()
    owner_id = serializers.CharField()
    numbers = serializers.ListField(child=serializers.ListField(child=serializers.IntegerField()))
    card_hash = serializers.CharField()

class BingoRoomSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    room_code = serializers.CharField()
    created_by_id = serializers.CharField()
    participants = RoomParticipantSerializer(many=True)
    is_closed = serializers.BooleanField()
    created_at = serializers.DateTimeField()