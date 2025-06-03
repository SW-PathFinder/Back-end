from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('room/<str:room_name>/', views.chat_room, name='chat_room'),
    path('api/create-room/', views.create_room, name='create_room'),
]