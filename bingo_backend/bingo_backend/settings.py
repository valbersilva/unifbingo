from pathlib import Path
import mongoengine

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Chave secreta (não usar em produção)
SECRET_KEY = 'django-insecure-7iudv=7*r*gq^zuf9ag-jn7!v5lse9w9&2j%3-1cr#%$-l+ewt'

# Ativa modo debug
DEBUG = True

# Hosts permitidos
ALLOWED_HOSTS = ['*']

# Aplicativos instalados
INSTALLED_APPS = [
    'django.contrib.admin',
    # 'django.contrib.auth',  # Desativado para uso exclusivo do MongoDB
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'users',
    'bingo_room',
    'game_session',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',  # Desativado
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs
ROOT_URLCONF = 'bingo_backend.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                # 'django.contrib.auth.context_processors.auth',  # Desativado
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'bingo_backend.wsgi.application'

# Conexão com MongoDB via mongoengine
mongoengine.connect(
    db='unibingo',
    host='localhost',
    port=27017,
    alias='default'  # Define como a conexão padrão
)

# Banco relacional desativado
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Validações de senha desativadas
AUTH_PASSWORD_VALIDATORS = []

# Internacionalização
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos
STATIC_URL = 'static/'

# Chave primária padrão (não usada com mongoengine, mas mantém compatibilidade com admin)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# Desativado: modelo customizado de usuário com Django
# AUTH_USER_MODEL = 'users.User'
