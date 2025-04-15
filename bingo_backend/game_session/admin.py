from django.contrib import admin
from .models import GameSession, DrawnNumber, GameAuditLog, GameHistory

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'created_at', 'is_active', 'winner')
    list_filter = ('is_active', 'created_at')
    search_fields = ('room__room_code', 'winner__username')


@admin.register(DrawnNumber)
class DrawnNumberAdmin(admin.ModelAdmin):
    list_display = ('number', 'session', 'drawn_at')
    list_filter = ('drawn_at',)
    search_fields = ('number', 'session__room__room_code')


@admin.register(GameAuditLog)
class GameAuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'action', 'session')
    list_filter = ('timestamp',)
    search_fields = ('actor__username', 'action', 'session__room__room_code')


@admin.register(GameHistory)
class GameHistoryAdmin(admin.ModelAdmin):
    list_display = ('session', 'room_code', 'winner', 'started_at', 'ended_at', 'is_completed')
    list_filter = ('is_completed', 'ended_at')
    search_fields = ('room_code', 'winner__username')
