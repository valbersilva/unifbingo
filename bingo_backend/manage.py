#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Define o módulo de configurações e executa comandos Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. "
            "Verifique se ele está instalado e se o ambiente virtual está ativado."
        ) from exc
    sys.exit(execute_from_command_line(sys.argv))

if __name__ == '__main__':
    main()
