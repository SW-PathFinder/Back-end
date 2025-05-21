from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    #웹소켓 URL과 consumer 연결
    re_path(r'ws/game/(?P<room_code>\w+)/$', consumers.GameConsumer.as_asgi()),
]
