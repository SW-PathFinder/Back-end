# apps/saboteur/voice_chat/openvidu_client.py

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

headers = {"Content-Type": "application/json"}

def get_auth():
    return HTTPBasicAuth("OPENVIDUAPP", settings.OPENVIDU_SECRET)


def deleteOpenviduSession(session_id: str):
    """
    OpenVidu 세션을 강제로 삭제 (강제 종료 포함)
    """
    url = f"{settings.OPENVIDU_URL}/api/sessions/{session_id}"
    response = requests.delete(
        url,
        auth=get_auth(),
        headers=headers,
        verify=settings.OPENVIDU_VERIFY_SSL
    )
    if response.status_code not in (204, 404):
        response.raise_for_status()


def createOpenviduSession(sessionId: str) -> str:
    url = f"{settings.OPENVIDU_URL}/api/sessions"
    payload = {"customSessionId": sessionId}
    response = requests.post(
        url,
        json=payload,
        auth=get_auth(),
        headers=headers,
        verify=settings.OPENVIDU_VERIFY_SSL
    )
    # 409 Conflict → 세션이 이미 존재하는 경우, 예외를 발생시키지 않고 그대로 sessionId 반환
    if response.status_code == 409:
        return sessionId
    response.raise_for_status()
    return response.json()["id"]


def generateOpenviduToken(sessionId: str, userId: str) -> str:
    url = f"{settings.OPENVIDU_URL}/api/tokens"
    payload = {"session": sessionId, "data": userId}
    response = requests.post(
        url,
        json=payload,
        auth=get_auth(),
        headers=headers,
        verify=settings.OPENVIDU_VERIFY_SSL
    )
    response.raise_for_status()
    return response.json()["token"]

