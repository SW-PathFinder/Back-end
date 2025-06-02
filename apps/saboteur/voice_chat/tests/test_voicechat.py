import os
from django.test import TestCase
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

class VoiceChatTestCase(TestCase):

    def setUp(self):
        self.baseUrl = "/voice"
        self.userId1 = str(uuid4())
        self.userId2 = str(uuid4())

    def test_voice_session_flow(self):
        # 1. 세션 생성
        res = self.client.post(f"{self.baseUrl}/session/", data={"userId": self.userId1}, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        sessionId = data["sessionId"]
        self.assertIsNotNone(sessionId)

        # 2. 세션 참가 (userId2)
        joinRes = self.client.post(f"{self.baseUrl}/join/", data={"sessionId": sessionId, "userId": self.userId2}, content_type="application/json")
        self.assertEqual(joinRes.status_code, 200)
        self.assertIn("participants", joinRes.json())

        # 3. 토큰 요청 (userId2)
        tokenRes = self.client.post(f"{self.baseUrl}/token/", data={"sessionId": sessionId, "userId": self.userId2}, content_type="application/json")
        self.assertEqual(tokenRes.status_code, 200)
        token = tokenRes.json()["token"]

        # ✅ 토큰 중복 요청 시 동일한 토큰 반환 확인
        tokenRes2 = self.client.post(f"{self.baseUrl}/token/", data={"sessionId": sessionId, "userId": self.userId2}, content_type="application/json")
        self.assertEqual(tokenRes2.status_code, 200)
        self.assertEqual(token, tokenRes2.json()["token"])

        # 4. 참가자 조회
        partRes = self.client.get(f"{self.baseUrl}/participants/{sessionId}/")
        self.assertEqual(partRes.status_code, 200)
        participants = partRes.json().get("participants", [])
        self.assertIn(self.userId1, participants)
        self.assertIn(self.userId2, participants)

        # ✅ 재참여 시 중복 참가자 없이 유지
        joinRes2 = self.client.post(f"{self.baseUrl}/join/", data={"sessionId": sessionId, "userId": self.userId2}, content_type="application/json")
        self.assertEqual(joinRes2.status_code, 200)
        participants2 = joinRes2.json().get("participants", [])
        self.assertEqual(participants2.count(self.userId2), 1)

        # 5. 퇴장 처리 (userId2)
        leaveRes = self.client.post(f"{self.baseUrl}/leave/", data={"sessionId": sessionId, "userId": self.userId2}, content_type="application/json")
        self.assertEqual(leaveRes.status_code, 200)

        # 6. 남은 참가자 확인
        partAfter = self.client.get(f"{self.baseUrl}/participants/{sessionId}/")
        self.assertIn(self.userId1, partAfter.json().get("participants", []))
        self.assertNotIn(self.userId2, partAfter.json().get("participants", []))

        # ✅ 세션 완전 삭제 후 접근 제한 확인
        leaveOwner = self.client.post(f"{self.baseUrl}/leave/", data={"sessionId": sessionId, "userId": self.userId1}, content_type="application/json")
        self.assertEqual(leaveOwner.status_code, 200)

        partAfterFinal = self.client.get(f"{self.baseUrl}/participants/{sessionId}/")
        self.assertEqual(partAfterFinal.status_code, 404)

    def test_invalid_session_access(self):
        invalidSession = "invalid-session"
        invalidUser = "invalid-user"

        tokenRes = self.client.post(f"{self.baseUrl}/token/", data={"sessionId": invalidSession, "userId": invalidUser}, content_type="application/json")
        self.assertEqual(tokenRes.status_code, 404)

        partRes = self.client.get(f"{self.baseUrl}/participants/{invalidSession}/")
        self.assertEqual(partRes.status_code, 404)

        leaveRes = self.client.post(f"{self.baseUrl}/leave/", data={"sessionId": invalidSession, "userId": invalidUser}, content_type="application/json")
        self.assertEqual(leaveRes.status_code, 404)

    def test_missing_fields(self):
        res1 = self.client.post(f"{self.baseUrl}/token/", data={}, content_type="application/json")
        self.assertEqual(res1.status_code, 400)

        res2 = self.client.post(f"{self.baseUrl}/leave/", data={"sessionId": "abc"}, content_type="application/json")
        self.assertEqual(res2.status_code, 400)

        res3 = self.client.post(f"{self.baseUrl}/leave/", data={"userId": "abc"}, content_type="application/json")
        self.assertEqual(res3.status_code, 400)

        res4 = self.client.post(f"{self.baseUrl}/join/", data={"sessionId": "abc"}, content_type="application/json")
        self.assertEqual(res4.status_code, 400)

    def test_cleanup_sessions(self):
        userId = str(uuid4())
        res1 = self.client.post(f"{self.baseUrl}/session/", data={"userId": userId}, content_type="application/json")
        sessionId = res1.json()["sessionId"]

        res2 = self.client.post(f"{self.baseUrl}/cleanup/", data={"force": True}, content_type="application/json")
        self.assertEqual(res2.status_code, 200)
        remaining = res2.json().get("remaining", [])
        self.assertNotIn(sessionId, remaining)

    def test_create_session_missing_user(self):
        res = self.client.post(f"{self.baseUrl}/session/", data={}, content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_join_session_with_invalid_data(self):
        res = self.client.post(f"{self.baseUrl}/join/", data={}, content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_token_creation_without_participation(self):
        userId = str(uuid4())
        sessionRes = self.client.post(f"{self.baseUrl}/session/", data={"userId": userId}, content_type="application/json")
        sessionId = sessionRes.json()["sessionId"]

        tokenRes = self.client.post(f"{self.baseUrl}/token/", data={"sessionId": sessionId, "userId": "stranger"}, content_type="application/json")
        self.assertEqual(tokenRes.status_code, 403)  # stranger는 참여자가 아니므로 거부

# ✅ 통합 테스트: 여러 사용자의 흐름을 한 번에 시뮬레이션
class VoiceChatIntegrationTestCase(TestCase):
    def test_multi_user_voice_flow(self):
        userA = str(uuid4())
        userB = str(uuid4())

        # 세션 생성 by A
        sessionRes = self.client.post("/voice/session/", data={"userId": userA}, content_type="application/json")
        sessionId = sessionRes.json()["sessionId"]

        # A 참가자 목록 확인
        partA = self.client.get(f"/voice/participants/{sessionId}/")
        self.assertIn(userA, partA.json().get("participants", []))

        # B 참가
        self.client.post("/voice/join/", data={"sessionId": sessionId, "userId": userB}, content_type="application/json")

        # B 토큰 요청
        token = self.client.post("/voice/token/", data={"sessionId": sessionId, "userId": userB}, content_type="application/json")
        self.assertIn("token", token.json())

        # A와 B 모두 퇴장
        self.client.post("/voice/leave/", data={"sessionId": sessionId, "userId": userB}, content_type="application/json")
        self.client.post("/voice/leave/", data={"sessionId": sessionId, "userId": userA}, content_type="application/json")

        # 세션 삭제 확인
        finalCheck = self.client.get(f"/voice/participants/{sessionId}/")
        self.assertEqual(finalCheck.status_code, 404)