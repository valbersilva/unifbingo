from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # Exemplo: re_path(r'ws/game_session/(?P<session_id>\d+)/$', consumers.GameSessionConsumer.as_asgi()),
]