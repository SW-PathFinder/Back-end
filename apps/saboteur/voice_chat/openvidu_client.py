# apps/saboteur/voice_chat/openvidu_client.py

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth("OPENVIDUAPP", settings.OPENVIDU_SECRET)
headers = {"Content-Type": "application/json"}


def deleteOpenviduSession(session_id: str):
    """
    OpenVidu 세션을 강제로 삭제 (강제 종료 포함)
    """
    url = f"{settings.OPENVIDU_URL}/api/sessions/{session_id}"
    response = requests.delete(
        url,
        auth=auth,
        headers=headers,
        verify=settings.OPENVIDU_VERIFY_SSL
    )
    if response.status_code not in (204, 404):
        response.raise_for_status()


def createOpenviduSession(session_id: str) -> str:
    """
    항상 새로운 세션을 생성
    - 기존 세션이 존재하면 삭제 후 재생성
    """
    url = f"{settings.OPENVIDU_URL}/api/sessions"
    payload = {"customSessionId": session_id}

    try:
        response = requests.post(
            url,
            json=payload,
            auth=auth,
            headers=headers,
            verify=settings.OPENVIDU_VERIFY_SSL
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 409:
            # 기존 세션이 존재하므로 삭제 후 재시도
            deleteOpenviduSession(session_id)

            # 재시도
            retry_response = requests.post(
                url,
                json=payload,
                auth=auth,
                headers=headers,
                verify=settings.OPENVIDU_VERIFY_SSL
            )
            retry_response.raise_for_status()
            return session_id
        else:
            raise
    return session_id


def generateOpenviduToken(session_id: str, user_id: str) -> str:
    """
    OpenVidu Token 생성
    """
    url = f"{settings.OPENVIDU_URL}/api/tokens"
    payload = {
        "session": session_id,
        "data": f"userId={user_id}",
    }

    response = requests.post(
        url,
        json=payload,
        auth=auth,
        headers=headers,
        verify=settings.OPENVIDU_VERIFY_SSL
    )
    response.raise_for_status()
    return response.json().get("token")
