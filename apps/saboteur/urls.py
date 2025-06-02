from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('voice/', include('apps.saboteur.voice_chat.urls')),
]