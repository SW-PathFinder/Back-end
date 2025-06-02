# apps/saboteur/voice_chat/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from uuid import uuid4
import urllib3

from .openvidu_client import createOpenviduSession, generateOpenviduToken
from .session_store import (
    sessionStore, createSession, touchSession,
    sessionExists, cleanupSessions,
    addParticipant, getParticipants, removeParticipant
)

urllib3.disable_warnings()


@api_view(["POST"])
def createVoiceSession(request):
    sessionId = str(uuid4())
    userId = request.data.get("userId")

    if not userId:
        return Response({"error": "Missing userId"}, status=400)

    try:
        createOpenviduSession(sessionId)
    except Exception as e:
        return Response({"error": f"Failed to create session: {str(e)}"}, status=500)

    createSession(sessionId, ownerId=userId)
    return Response({"sessionId": sessionId})


@api_view(["POST"])
def joinVoiceSession(request):
    sessionId = request.data.get("sessionId")
    userId = request.data.get("userId")

    if not sessionExists(sessionId):
        return Response({"error": "Session not found"}, status=404)

    if not userId:
        return Response({"error": "Missing userId"}, status=400)

    addParticipant(sessionId, userId)
    touchSession(sessionId)
    return Response({"message": "joined", "participants": getParticipants(sessionId)})


@api_view(["POST"])
def getVoiceToken(request):
    sessionId = request.data.get("sessionId")
    userId = request.data.get("userId")

    if not sessionId or not userId:
        return Response({"error": "Missing sessionId or userId"}, status=400)
    if not sessionExists(sessionId):
        return Response({"error": "Session not found"}, status=404)

    try:
        token = generateOpenviduToken(sessionId, userId)
    except Exception as e:
        return Response({"error": f"Token creation failed: {str(e)}"}, status=500)

    return Response({"token": token})


@api_view(["POST"])
def cleanupVoiceSessions(request):
    force = request.data.get("force", False)
    cleanupSessions(force=force)
    return Response({"message": "cleanup complete", "remaining": list(sessionStore.keys())})


@api_view(["GET"])
def getSessionParticipants(request, sessionId):
    if not sessionExists(sessionId):
        return Response({"error": "session not found"}, status=404)
    return Response({"participants": getParticipants(sessionId)})


@api_view(["POST"])
def leaveVoiceSession(request):
    sessionId = request.data.get("sessionId")
    userId = request.data.get("userId")

    if not sessionId or not userId:
        return Response({"error": "Missing sessionId or userId"}, status=400)
    if not sessionExists(sessionId):
        return Response({"error": "Session not found"}, status=404)

    removeParticipant(sessionId, userId)
    return Response({"message": "user removed", "sessionId": sessionId})
