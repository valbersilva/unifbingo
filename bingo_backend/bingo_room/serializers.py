from rest_framework import serializers
from .models import BingoRoom, BingoCard, RoomParticipant


class BingoRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = BingoRoom
        fields = ['id', 'room_code', 'created_by', 'created_at', 'is_closed']
        read_only_fields = ['room_code', 'created_by', 'created_at', 'is_closed']


class BingoCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BingoCard
        fields = ['id', 'card_hash', 'room', 'owner', 'numbers', 'created_at']
        read_only_fields = ['card_hash', 'numbers', 'created_at', 'owner']


class RoomParticipantSerializer(serializers.ModelSerializer):
    room = BingoRoomSerializer(read_only=True)

    class Meta:
        model = RoomParticipant
        fields = ['user', 'room', 'joined_at']
