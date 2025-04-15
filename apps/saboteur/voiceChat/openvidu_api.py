# apps/saboteur/voiceChat/openvidu_api.py

import requests

OPENVIDU_URL = "https://13.125.231.212:4443/openvidu"
OPENVIDU_SECRET = "VidU_3xS7_kEy9-Z1"
AUTH = ("OPENVIDUAPP", OPENVIDU_SECRET)


def create_openvidu_session(session_id: str) -> str:
    url = f"{OPENVIDU_URL}/api/sessions"
    payload = {"customSessionId": session_id}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, auth=AUTH, headers=headers, verify=False)
    response.raise_for_status()

    return response.json()["id"]


def generate_openvidu_token(session_id: str) -> str:
    url = f"{OPENVIDU_URL}/api/tokens"
    payload = {"session": session_id}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, auth=AUTH, headers=headers, verify=False)
    response.raise_for_status()

    return response.json()["token"]
