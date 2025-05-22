from django.urls import path, include

urlpatterns = [
    # Admin desativado — reative se necessário:
    # path('admin/', admin.site.urls),

    # Rotas da API
    path('api/users/', include('users.urls')),
    path('api/rooms/', include('bingo_room.urls')),
    path('api/sessions/', include('game_session.urls')),  # Certifique-se de incluir esta linha se ainda não tiver
]
