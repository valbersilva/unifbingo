"""
ASGI config for bingo_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import mongoengine
from django.core.asgi import get_asgi_application

# Define o módulo de configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_backend.settings')

# Conecta ao MongoDB (mesma configuração do settings.py)
mongoengine.connect(
    db='unibingo',
    host='localhost',
    port=27017,
    alias='default'  # garante que seja o alias padrão do mongoengine
)

# Inicializa a aplicação ASGI
application = get_asgi_application()
