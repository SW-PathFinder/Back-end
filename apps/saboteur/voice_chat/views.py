# apps/saboteur/voice_chat/views.py

from collections import deque
from rest_framework.decorators import api_view
from rest_framework.response import Response
import urllib3
import traceback
import time
import threading
from requests.exceptions import HTTPError
from .openvidu_client import createOpenviduSession, generateOpenviduToken
from .session_store import (
    sessionStore, createSession, touchSession,
    sessionExists, cleanupSessions,
    addParticipant, getParticipants, removeParticipant, getSessionOwner
)

# SSL 경고 비활성화
urllib3.disable_warnings()

# roomId → sessionId 매핑 저장
ROOM_SESSION_MAP = {}
ROOM_SESSION_MAP_LOCK = threading.Lock()

# sessionId → userId → OpenVidu token 캐시
TOKEN_CACHE = {}

# 로그 기록용 (최근 1000개만 유지하여 메모리 누수 방지)
VOICE_SESSION_LOGS = deque(maxlen=1000)


@api_view(["POST"])
def createVoiceSession(request):
    """
    방 생성 API (항상 새 세션 생성)
    - roomId를 기반으로 OpenVidu 세션을 강제로 재생성
    - sessionStore에 세션 생성
    """
    roomId = request.data.get("roomId")
    userId = request.data.get("userId")

    if not userId or not roomId:
        return Response({"error": "Missing userId or roomId"}, status=400)

    sessionId = roomId  # roomId 자체를 세션 ID로 사용

    try:
        createOpenviduSession(sessionId)
    except Exception as e:
        traceback.print_exc()
        return Response({"error": f"Failed to create session: {str(e)}"}, status=500)

    # 내부 세션 생성 및 매핑 저장
    createSession(sessionId, ownerId=userId)
    ROOM_SESSION_MAP[roomId] = sessionId

    VOICE_SESSION_LOGS.append({
        "event": "create_session",
        "timestamp": time.time(),
        "sessionId": sessionId,
        "userId": userId
    })

    return Response({"sessionId": sessionId})


@api_view(["POST"])
def joinVoiceSession(request):
    sessionId = request.data.get("sessionId")
    userId = request.data.get("userId")

    if not sessionId or not userId:
        return Response({"error": "Missing sessionId or userId"}, status=400)

    if not sessionExists(sessionId):
        return Response({"error": "Session not found"}, status=404)

    if userId not in getParticipants(sessionId):
        addParticipant(sessionId, userId)

    touchSession(sessionId)

    VOICE_SESSION_LOGS.append({
        "event": "join_session",
        "timestamp": time.time(),
        "sessionId": sessionId,
        "userId": userId
    })

    return Response({"message": "joined", "participants": getParticipants(sessionId)})


@api_view(["POST"])
def getVoiceToken(request):
    sessionId = request.data.get("sessionId")
    userId = request.data.get("userId")

    if not sessionId or not userId:
        return Response({"error": "Missing sessionId or userId"}, status=400)

    if not sessionExists(sessionId):
        return Response({"error": "Session not found"}, status=404)

    if userId not in getParticipants(sessionId):
        return Response({"error": "User not in session"}, status=403)

    if sessionId in TOKEN_CACHE and userId in TOKEN_CACHE[sessionId]:
        return Response({"token": TOKEN_CACHE[sessionId][userId]})

    try:
        token = generateOpenviduToken(sessionId, userId)
    except Exception as e:
        traceback.print_exc()
        return Response({"error": f"Token creation failed: {str(e)}"}, status=500)

    if sessionId not in TOKEN_CACHE:
        TOKEN_CACHE[sessionId] = {}
    TOKEN_CACHE[sessionId][userId] = token

    VOICE_SESSION_LOGS.append({
        "event": "get_token",
        "timestamp": time.time(),
        "sessionId": sessionId,
        "userId": userId,
        "token": token
    })

    return Response({"token": token})


@api_view(["POST"])
def cleanupVoiceSessions(request):
    force = request.data.get("force", False)
    removed_sessions = cleanupSessions(force=force)

    for sessionId in removed_sessions:
        for roomId, sId in list(ROOM_SESSION_MAP.items()):
            if sId == sessionId:
                del ROOM_SESSION_MAP[roomId]
        TOKEN_CACHE.pop(sessionId, None)

        VOICE_SESSION_LOGS.append({
            "event": "cleanup_session",
            "timestamp": time.time(),
            "sessionId": sessionId
        })

    return Response({"message": "cleanup complete", "remaining": list(sessionStore.keys())})


@api_view(["GET"])
def getSessionParticipants(request, sessionId):
    if not sessionExists(sessionId):
        return Response({"error": "Session not found"}, status=404)
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

    if sessionId in TOKEN_CACHE:
        TOKEN_CACHE[sessionId].pop(userId, None)

    VOICE_SESSION_LOGS.append({
        "event": "leave_session",
        "timestamp": time.time(),
        "sessionId": sessionId,
        "userId": userId
    })

    return Response({"message": "user removed", "sessionId": sessionId})
