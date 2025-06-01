from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Saboteur Game & Voice Chat API",
        default_version='v1',
        description="Saboteur 실시간 게임과 n:n 음성채팅 기능을 위한 통합 API 명세서",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],  # 리스트로 수정
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.saboteur.urls')),

    # Swagger, ReDoc 문서 경로
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
