# apps/saboteur/voice_chat/openvidu_client.py

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth("OPENVIDUAPP", settings.OPENVIDU_SECRET)
headers = {"Content-Type": "application/json"}


def createOpenviduSession(sessionId: str) -> str:
    url = f"{settings.OPENVIDU_URL}/api/sessions"
    payload = {"customSessionId": sessionId}
    response = requests.post(
        url,
        json=payload,
        auth=auth,
        headers=headers,
        verify=settings.OPENVIDU_VERIFY_SSL
    )
    if response.status_code == 409:
        raise requests.exceptions.HTTPError(
            f"HTTP 409 Conflict: Session '{sessionId}' already exists."
        )
    response.raise_for_status()
    return response.json()["id"]


def generateOpenviduToken(sessionId: str, userId: str) -> str:
    url = f"{settings.OPENVIDU_URL}/api/tokens"
    payload = {"session": sessionId, "data": userId}
    response = requests.post(
        url,
        json=payload,
        auth=auth,
        headers=headers,
        verify=settings.OPENVIDU_VERIFY_SSL
    )
    response.raise_for_status()
    return response.json()["token"]
