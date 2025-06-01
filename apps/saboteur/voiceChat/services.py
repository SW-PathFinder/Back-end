import requests
import os

VOICE_CHAT_SERVER_URL = os.getenv("spring_boot_url")  # 기본값은 로컬호스트의 8080 포트로 설정


def create_openvidu_session(room_id: str):
    res = requests.post(f"{VOICE_CHAT_SERVER_URL}/api/sessions", json={"roomId": room_id})
    res.raise_for_status()
    return res.json()["sessionId"]


def create_openvidu_token(session_id: str, nickname: str):
    res = requests.post(
        f"{VOICE_CHAT_SERVER_URL}/api/tokens",
        json={"sessionId": session_id, "nickname": nickname}
    )
    res.raise_for_status()
    return res.json()["token"]
