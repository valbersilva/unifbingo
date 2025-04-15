from django.contrib import admin
from .models import BingoRoom, RoomParticipant, BingoCard

@admin.register(BingoRoom)
class BingoRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_code', 'created_by', 'created_at', 'is_closed')
    search_fields = ('room_code', 'created_by__username')
    list_filter = ('is_closed', 'created_at')


@admin.register(RoomParticipant)
class RoomParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'joined_at')
    search_fields = ('user__username', 'room__room_code')
    list_filter = ('joined_at',)


@admin.register(BingoCard)
class BingoCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'card_hash', 'owner', 'room', 'created_at')
    search_fields = ('card_hash', 'owner__username', 'room__room_code')
    list_filter = ('created_at',)
