from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/bingo_room/(?P<room_id>\d+)/$', consumers.BingoRoomConsumer.as_asgi()),
    # Adicione outras rotas de WebSocket específicas para bingo_room aqui
]