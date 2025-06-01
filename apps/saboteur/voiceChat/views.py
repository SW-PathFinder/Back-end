import urllib3
import requests
from uuid import uuid4
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .session_store import (
    SESSION_STORE, create_session, touch_session,
    session_exists, cleanup_sessions,
    add_participant, get_participants, remove_participant
)

urllib3.disable_warnings()

OPENVIDU_URL = settings.OPENVIDU_URL
OPENVIDU_SECRET = settings.OPENVIDU_SECRET
OPENVIDU_AUTH = ("OPENVIDUAPP", OPENVIDU_SECRET)

# === [OpenVidu 관련 함수 정의] ===

def create_openvidu_session(session_id):
    url = f"{OPENVIDU_URL}/api/sessions"
    payload = {"customSessionId": session_id}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, auth=OPENVIDU_AUTH, headers=headers, verify=False)

    if response.status_code == 409:
        return session_id
    response.raise_for_status()
    return response.json()["id"]

def generate_openvidu_token(session_id, user_id):
    url = f"{OPENVIDU_URL}/api/tokens"
    payload = {
        "session": session_id,
        "data": user_id
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, auth=OPENVIDU_AUTH, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()["token"]

# === [View 함수들] ===

@swagger_auto_schema(method='post', operation_description="OpenVidu 세션 생성")
@api_view(["POST"])
def create_voice_session(request):
    session_id = str(uuid4())
    user_id = str(uuid4())

    try:
        create_openvidu_session(session_id)
    except Exception as e:
        return Response({"error": f"Failed to create session: {str(e)}"}, status=500)

    create_session(session_id, owner_id=user_id)
    return Response({"session_id": session_id, "user_id": user_id})


@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['session_id'],
    properties={
        'session_id': openapi.Schema(type=openapi.TYPE_STRING)
    }
), operation_description="세션 참가")
@api_view(["POST"])
def join_voice_session(request):
    session_id = request.data.get("session_id")
    if not session_exists(session_id):
        return Response({"error": "Session not found"}, status=404)

    user_id = str(uuid4())
    add_participant(session_id, user_id)
    touch_session(session_id)
    return Response({"message": "joined", "user_id": user_id, "participants": get_participants(session_id)})


@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['session_id', 'user_id'],
    properties={
        'session_id': openapi.Schema(type=openapi.TYPE_STRING),
        'user_id': openapi.Schema(type=openapi.TYPE_STRING)
    }
), operation_description="토큰 발급")
@api_view(["POST"])
def get_voice_token(request):
    session_id = request.data.get("session_id")
    user_id = request.data.get("user_id")

    if not session_id or not user_id:
        return Response({"error": "Missing session_id or user_id"}, status=400)
    if not session_exists(session_id):
        return Response({"error": "Session not found"}, status=404)

    try:
        token = generate_openvidu_token(session_id, user_id)
    except Exception as e:
        return Response({"error": f"Token creation failed: {str(e)}"}, status=500)

    return Response({"token": token})


@swagger_auto_schema(method='post', operation_description="세션 정리")
@api_view(["POST"])
def cleanup_voice_sessions(request):
    force = request.data.get("force", False)
    cleanup_sessions(force=force)
    return Response({"message": "cleanup complete", "remaining": list(SESSION_STORE.keys())})


@swagger_auto_schema(method='get', operation_description="참여자 목록 조회")
@api_view(["GET"])
def get_session_participants(request, session_id):
    if not session_exists(session_id):
        return Response({"error": "session not found"}, status=404)
    return Response({"participants": get_participants(session_id)})


@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['session_id', 'user_id'],
    properties={
        'session_id': openapi.Schema(type=openapi.TYPE_STRING),
        'user_id': openapi.Schema(type=openapi.TYPE_STRING)
    }
), operation_description="세션 떠나기")
@api_view(["POST"])
def leave_voice_session(request):
    session_id = request.data.get("session_id")
    user_id = request.data.get("user_id")

    if not session_id or not user_id:
        return Response({"error": "Missing session_id or user_id"}, status=400)

    if not session_exists(session_id):
        return Response({"error": "Session not found"}, status=404)

    remove_participant(session_id, user_id)
    return Response({"message": "user removed", "session_id": session_id})
