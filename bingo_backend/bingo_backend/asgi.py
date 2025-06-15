"""
ASGI config for bingo_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""
import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack # Para autenticação de usuário no WebSocket

import bingo_room.routing
import game_session.routing # Você provavelmente terá rotas aqui também

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Adicione a camada de autenticação para WebSockets
    "websocket": AuthMiddlewareStack(
        URLRouter(
            bingo_room.routing.websocket_urlpatterns +
            game_session.routing.websocket_urlpatterns # Combine as rotas de todas as suas apps
        )
    ),
})