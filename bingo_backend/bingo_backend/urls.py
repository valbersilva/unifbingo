from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),  # All user endpoints will be under /api/users/
    path('api/', include('bingo_room.urls')),
    path('api/', include('game_session.urls')),
]