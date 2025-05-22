"""
WSGI config for bingo_backend project.

This exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import mongoengine
from django.core.wsgi import get_wsgi_application

# Define o módulo de configurações
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_backend.settings')

# Conecta ao MongoDB com mongoengine (mesma config de settings.py)
mongoengine.connect(
    db='unibingo',
    host='localhost',
    port=27017
)

# Inicializa o WSGI
application = get_wsgi_application()
