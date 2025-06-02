# apps/saboteur/voice_chat/tests/test_voicechat.py

import os
import time
from uuid import uuid4
from functools import wraps
from django.test import TestCase
from unittest.mock import patch
from dotenv import load_dotenv

from apps.saboteur.voice_chat import session_store

load_dotenv()

# 테스트 시작-종료 시간 측정을 위한 데코레이터
def timed_test(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"\nSTART: {func.__name__}")
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.time() - start
            print(f"END: {func.__name__} (elapsed: {elapsed:.3f}s)")
    return wrapper


class VoiceChatTestCase(TestCase):

    def setUp(self):
        # 테스트용 사용자와 방 ID 설정
        self.baseUrl = "/voice"
        self.userId1 = str(uuid4())
        self.userId2 = str(uuid4())
        self.userId3 = str(uuid4())
        self.userId4 = str(uuid4())
        self.roomId = f"room-{uuid4()}"

    @timed_test
    def test_voice_session_flow(self):
        """
        음성 세션의 생성, 참가, 토큰 발급, 소유자 위임, 세션 종료 전체 흐름 테스트
        """
        # 세션 생성
        res = self.client.post(f"{self.baseUrl}/session/", data={"userId": self.userId1, "roomId": self.roomId}, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        sessionId = res.json()["sessionId"]
        self.assertEqual(sessionId, self.roomId)

        # 나머지 유저 참가
        for userId in [self.userId2, self.userId3, self.userId4]:
            joinRes = self.client.post(f"{self.baseUrl}/join/", data={"sessionId": sessionId, "userId": userId}, content_type="application/json")
            self.assertEqual(joinRes.status_code, 200)

        # 중복 참가 확인 (동일 유저 2번 참가 시도)
        dupJoin = self.client.post(f"{self.baseUrl}/join/", data={"sessionId": sessionId, "userId": self.userId2}, content_type="application/json")
        self.assertEqual(dupJoin.status_code, 200)
        participants = dupJoin.json().get("participants", [])
        self.assertEqual(participants.count(self.userId2), 1)

        # 참가자별 토큰 요청 (캐싱 확인 포함)
        for userId in [self.userId2, self.userId3, self.userId4]:
            tokenRes = self.client.post(f"{self.baseUrl}/token/", data={"sessionId": sessionId, "userId": userId}, content_type="application/json")
            self.assertEqual(tokenRes.status_code, 200)
            token = tokenRes.json()["token"]

            tokenRepeat = self.client.post(f"{self.baseUrl}/token/", data={"sessionId": sessionId, "userId": userId}, content_type="application/json")
            self.assertEqual(tokenRepeat.status_code, 200)
            self.assertEqual(token, tokenRepeat.json()["token"])

        # 참가자 목록 확인
        partRes = self.client.get(f"{self.baseUrl}/participants/{sessionId}/")
        self.assertEqual(partRes.status_code, 200)
        participants = partRes.json().get("participants", [])
        self.assertEqual(set(participants), {self.userId1, self.userId2, self.userId3, self.userId4})

        # 소유자 퇴장 후 위임 확인
        leaveOwner = self.client.post(f"{self.baseUrl}/leave/", data={"sessionId": sessionId, "userId": self.userId1}, content_type="application/json")
        self.assertEqual(leaveOwner.status_code, 200)
        new_owner = session_store.getSessionOwner(sessionId)
        self.assertIn(new_owner, [self.userId2, self.userId3, self.userId4])

        # 나머지 유저들도 퇴장
        for userId in [self.userId2, self.userId3, self.userId4]:
            leaveRes = self.client.post(f"{self.baseUrl}/leave/", data={"sessionId": sessionId, "userId": userId}, content_type="application/json")
            self.assertEqual(leaveRes.status_code, 200)

        # 모든 유저 퇴장 후 세션 삭제 확인
        partAfterFinal = self.client.get(f"{self.baseUrl}/participants/{sessionId}/")
        self.assertEqual(partAfterFinal.status_code, 404)

        # 존재하지 않거나 유효하지 않은 유저의 토큰 요청 → 403 또는 404
        invalidToken = self.client.post(f"{self.baseUrl}/token/", data={"sessionId": sessionId, "userId": str(uuid4())}, content_type="application/json")
        if session_store.sessionExists(sessionId):
            self.assertEqual(invalidToken.status_code, 403)
        else:
            self.assertEqual(invalidToken.status_code, 404)

        # 동일 방 ID로 세션 재생성 → 중복 허용 여부 확인
        res_conflict = self.client.post(f"{self.baseUrl}/session/", data={"userId": self.userId2, "roomId": self.roomId}, content_type="application/json")
        self.assertEqual(res_conflict.status_code, 200)  # 409로 바꿔도 됨


    @timed_test
    def test_token_after_cleanup(self):
        """
        세션 삭제 후 토큰 요청 시 404 반환
        """
        userId = str(uuid4())
        roomId = f"room-{uuid4()}"
        sessionRes = self.client.post(f"{self.baseUrl}/session/", data={"userId": userId, "roomId": roomId}, content_type="application/json")
        sessionId = sessionRes.json()["sessionId"]

        self.client.post(f"{self.baseUrl}/cleanup/", data={"force": True}, content_type="application/json")

        tokenRes = self.client.post(f"{self.baseUrl}/token/", data={"sessionId": sessionId, "userId": userId}, content_type="application/json")
        self.assertEqual(tokenRes.status_code, 404)


    @timed_test
    def test_join_after_cleanup(self):
        """
        세션 삭제 후 참가 시도 시 404 반환
        """
        userId = str(uuid4())
        roomId = f"room-{uuid4()}"
        sessionRes = self.client.post(f"{self.baseUrl}/session/", data={"userId": userId, "roomId": roomId}, content_type="application/json")
        sessionId = sessionRes.json()["sessionId"]

        self.client.post(f"{self.baseUrl}/cleanup/", data={"force": True}, content_type="application/json")

        joinRes = self.client.post(f"{self.baseUrl}/join/", data={"sessionId": sessionId, "userId": userId}, content_type="application/json")
        self.assertEqual(joinRes.status_code, 404)


    @timed_test
    @patch("apps.saboteur.voice_chat.views.generateOpenviduToken", side_effect=Exception("Mocked OpenVidu failure"))
    def test_openvidu_server_failure(self, mock_generate_token):
        """
        OpenVidu 서버 장애 시 토큰 요청 실패 → 500 반환 확인
        """
        user_id = str(uuid4())
        room_id = f"room-{uuid4()}"

        session_res = self.client.post("/voice/session/", data={"userId": user_id, "roomId": room_id}, content_type="application/json")
        session_id = session_res.json()["sessionId"]

        self.client.post("/voice/join/", data={"sessionId": session_id, "userId": user_id}, content_type="application/json")

        fail_res = self.client.post("/voice/token/", data={"sessionId": session_id, "userId": user_id}, content_type="application/json")
        self.assertEqual(fail_res.status_code, 500)
        self.assertIn("Token creation failed", fail_res.json().get("error", ""))


    @timed_test
    def test_session_expiration_by_timeout(self):
        """
        세션이 timeout 후 cleanup 되었는지 확인
        """
        session_store.sessionTimeoutSeconds = 1  # 1초로 설정

        userId = str(uuid4())
        roomId = f"room-{uuid4()}"

        sessionRes = self.client.post(f"{self.baseUrl}/session/", data={"userId": userId, "roomId": roomId}, content_type="application/json")
        sessionId = sessionRes.json()["sessionId"]

        time.sleep(1.5)  # timeout 유도
        self.client.post(f"{self.baseUrl}/cleanup/", data={}, content_type="application/json")

        check = self.client.get(f"{self.baseUrl}/participants/{sessionId}/")
        self.assertEqual(check.status_code, 404)


class VoiceChatIntegrationTestCase(TestCase):

    @timed_test
    def test_multi_user_voice_flow(self):
        """
        4명 이상 유저의 세션 참가 → 토큰 요청 → 순차 퇴장 → 세션 삭제까지 전체 흐름 확인
        """
        users = [str(uuid4()) for _ in range(4)]
        roomId = f"room-{uuid4()}"

        sessionRes = self.client.post("/voice/session/", data={"userId": users[0], "roomId": roomId}, content_type="application/json")
        sessionId = sessionRes.json()["sessionId"]
        self.assertEqual(sessionId, roomId)

        for user in users[1:]:
            self.client.post("/voice/join/", data={"sessionId": sessionId, "userId": user}, content_type="application/json")

        for user in users:
            tokenRes = self.client.post("/voice/token/", data={"sessionId": sessionId, "userId": user}, content_type="application/json")
            self.assertIn("token", tokenRes.json())

        for user in reversed(users):
            self.client.post("/voice/leave/", data={"sessionId": sessionId, "userId": user}, content_type="application/json")

        finalCheck = self.client.get(f"/voice/participants/{sessionId}/")
        self.assertEqual(finalCheck.status_code, 404)