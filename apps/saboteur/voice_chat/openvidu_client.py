# apps/saboteur/voice_chat/openvidu_client.py

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

from apps.saboteur.voice_chat import session_store

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

    if response.status_code == 409:
        # 이미 세션이 존재하므로 참가자 수 확인
        if session_store.getParticipantCount(sessionId) == 0:
            # 참가자 없음 → 삭제 후 재시도
            deleteOpenviduSession(sessionId)
            retry = requests.post(
                url,
                json=payload,
                auth=get_auth(),
                headers=headers,
                verify=settings.OPENVIDU_VERIFY_SSL
            )
            retry.raise_for_status()
            return retry.json()["id"]
        else:
            # 참가자 있음 → 그냥 기존 세션 사용
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
