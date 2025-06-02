# apps/saboteur/voice_chat/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('session/', views.createVoiceSession),
    path('join/', views.joinVoiceSession),
    path('token/', views.getVoiceToken),
    path('cleanup/', views.cleanupVoiceSessions),
    path('participants/<str:sessionId>/', views.getSessionParticipants),
    path('leave/', views.leaveVoiceSession),
]
