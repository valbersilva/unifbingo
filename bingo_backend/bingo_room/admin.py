from django.contrib import admin
from .models import BingoRoom, BingoCard, RoomParticipant

@admin.register(BingoRoom)
class BingoRoomAdmin(admin.ModelAdmin):
    list_display = ('room_code', 'created_by', 'is_closed', 'created_at')

@admin.register(BingoCard)
class BingoCardAdmin(admin.ModelAdmin):
    list_display = ('card_hash', 'room', 'owner', 'created_at')

@admin.register(RoomParticipant)
class RoomParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'room')
