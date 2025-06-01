from django.urls import path
from . import views

urlpatterns = [
    path('session/', views.create_voice_session),
    path('join/', views.join_voice_session),
    path('token/', views.get_voice_token),
    path('cleanup/', views.cleanup_voice_sessions),
    path('participants/<str:session_id>/', views.get_session_participants),
    path('leave/', views.leave_voice_session),
]