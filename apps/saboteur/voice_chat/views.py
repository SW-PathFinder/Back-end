# apps/saboteur/voice_chat/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
import urllib3
import traceback
import time
import requests
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

# sessionId → userId → OpenVidu token 캐시
TOKEN_CACHE = {}

# 로그 기록용 리스트
VOICE_SESSION_LOGS = []

@api_view(["POST"])
def createVoiceSession(request):
    """
    방 생성 API
    - roomId를 기반으로 OpenVidu 세션 생성
    - 중복 시 409 반환
    - sessionStore에 세션 생성
    """
    roomId = request.data.get("roomId")
    userId = request.data.get("userId")

    if not userId or not roomId:
        return Response({"error": "Missing userId or roomId"}, status=400)

    sessionId = roomId  # roomId 자체를 세션 ID로 사용

    try:
        # OpenVidu 서버에 세션 생성 요청
        createOpenviduSession(sessionId)
    except HTTPError as e:
        # 세션이 이미 존재할 경우
        if e.response.status_code == 409:
            return Response({"error": "Session already exists"}, status=409)
        traceback.print_exc()
        return Response({"error": f"Failed to create session: {str(e)}"}, status=500)
    except Exception as e:
        # 기타 예외 처리
        traceback.print_exc()
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)

    # 내부 세션 생성 및 매핑 저장
    createSession(sessionId, ownerId=userId)
    ROOM_SESSION_MAP[roomId] = sessionId

    # 로그 기록
    VOICE_SESSION_LOGS.append({
        "event": "create_session",
        "timestamp": time.time(),
        "sessionId": sessionId,
        "userId": userId
    })

    return Response({"sessionId": sessionId})


@api_view(["POST"])
def joinVoiceSession(request):
    """
    세션 참가 API
    - 세션 존재 여부 확인 후 참가자 목록에 추가
    """
    sessionId = request.data.get("sessionId")
    userId = request.data.get("userId")

    if not sessionId or not userId:
        return Response({"error": "Missing sessionId or userId"}, status=400)

    if not sessionExists(sessionId):
        return Response({"error": "Session not found"}, status=404)

    # 중복 참가 방지
    if userId not in getParticipants(sessionId):
        addParticipant(sessionId, userId)

    # 마지막 활성 시간 갱신
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
    """
    OpenVidu Token 발급 API
    - 유효한 세션과 참여자일 경우에만 토큰 발급
    - 토큰은 1회 생성 후 캐싱
    """
    sessionId = request.data.get("sessionId")
    userId = request.data.get("userId")

    if not sessionId or not userId:
        return Response({"error": "Missing sessionId or userId"}, status=400)

    if not sessionExists(sessionId):
        return Response({"error": "Session not found"}, status=404)

    if userId not in getParticipants(sessionId):
        return Response({"error": "User not in session"}, status=403)

    # 캐시된 토큰이 있으면 반환
    if sessionId in TOKEN_CACHE and userId in TOKEN_CACHE[sessionId]:
        return Response({"token": TOKEN_CACHE[sessionId][userId]})

    try:
        token = generateOpenviduToken(sessionId, userId)
    except Exception as e:
        traceback.print_exc()
        return Response({"error": f"Token creation failed: {str(e)}"}, status=500)

    # 캐시에 저장
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
    """
    세션 정리 API
    - 비활성화된 세션 또는 강제 정리 요청에 따라 세션 제거
    - 내부 세션 맵 및 토큰 캐시도 정리
    """
    force = request.data.get("force", False)
    removed_sessions = cleanupSessions(force=force)

    for sessionId in removed_sessions:
        # room → session 매핑 제거
        for roomId, sId in list(ROOM_SESSION_MAP.items()):
            if sId == sessionId:
                del ROOM_SESSION_MAP[roomId]
        # 토큰 캐시 제거
        TOKEN_CACHE.pop(sessionId, None)

        VOICE_SESSION_LOGS.append({
            "event": "cleanup_session",
            "timestamp": time.time(),
            "sessionId": sessionId
        })

    return Response({"message": "cleanup complete", "remaining": list(sessionStore.keys())})


@api_view(["GET"])
def getSessionParticipants(request, sessionId):
    """
    세션 참가자 목록 조회 API
    """
    if not sessionExists(sessionId):
        return Response({"error": "session not found"}, status=404)
    return Response({"participants": getParticipants(sessionId)})


@api_view(["POST"])
def leaveVoiceSession(request):
    """
    세션 나가기 API
    - 세션에서 사용자 제거 및 토큰 제거
    - 세션 소유자가 나가는 경우 소유자 변경 또는 세션 제거
    """
    sessionId = request.data.get("sessionId")
    userId = request.data.get("userId")

    if not sessionId or not userId:
        return Response({"error": "Missing sessionId or userId"}, status=400)

    if not sessionExists(sessionId):
        return Response({"error": "Session not found"}, status=404)

    removeParticipant(sessionId, userId)

    # 토큰 캐시 제거
    if sessionId in TOKEN_CACHE:
        TOKEN_CACHE[sessionId].pop(userId, None)

    VOICE_SESSION_LOGS.append({
        "event": "leave_session",
        "timestamp": time.time(),
        "sessionId": sessionId,
        "userId": userId
    })

    return Response({"message": "user removed", "sessionId": sessionId})
