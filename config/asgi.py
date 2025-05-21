"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

# settings 경로 수정 (dev 환경 사용하는 경우)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
# 아래는 기존 내용
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

django.setup()

application = get_asgi_application()

import apps.saboteur.routing


# ASGI application 설정
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.saboteur.routing.websocket_urlpatterns
        )
    ),
})
