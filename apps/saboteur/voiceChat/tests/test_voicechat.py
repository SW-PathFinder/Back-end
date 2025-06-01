import os
from django.test import TestCase
from dotenv import load_dotenv
from django.conf import settings

load_dotenv()

class VoiceChatTestCase(TestCase):

    def test_voice_session_flow(self):
        # 1. 세션 생성
        res = self.client.post("/voice/session/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        session_id = data["session_id"]
        user_id = data["user_id"]
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(user_id)

        # 2. 세션 참가
        join_res = self.client.post("/voice/join/", data={"session_id": session_id}, content_type="application/json")
        self.assertEqual(join_res.status_code, 200)
        join_data = join_res.json()
        self.assertIn("user_id", join_data)

        # 3. 토큰 요청
        token_res = self.client.post("/voice/token/", data={
            "session_id": session_id,
            "user_id": join_data["user_id"]
        }, content_type="application/json")
        self.assertEqual(token_res.status_code, 200)
        self.assertIn("token", token_res.json())

        # 4. 참가자 조회
        part_res = self.client.get(f"/voice/participants/{session_id}/")
        self.assertEqual(part_res.status_code, 200)
        participants = part_res.json().get("participants", [])
        self.assertIn(user_id, participants)
        self.assertIn(join_data["user_id"], participants)

        # 5. 퇴장 처리
        leave_res = self.client.post("/voice/leave/", data={
            "session_id": session_id,
            "user_id": join_data["user_id"]
        }, content_type="application/json")
        self.assertEqual(leave_res.status_code, 200)

    def test_invalid_session_access(self):
        # 존재하지 않는 세션에 접근 시도
        invalid_session_id = "non-existent-session"
        invalid_user_id = "non-existent-user"

        token_res = self.client.post("/voice/token/", data={
            "session_id": invalid_session_id,
            "user_id": invalid_user_id
        }, content_type="application/json")
        self.assertEqual(token_res.status_code, 404)

        part_res = self.client.get(f"/voice/participants/{invalid_session_id}/")
        self.assertEqual(part_res.status_code, 404)

    def test_missing_fields(self):
        # 필드 누락 시 400 응답 확인
        res1 = self.client.post("/voice/token/", data={}, content_type="application/json")
        self.assertEqual(res1.status_code, 400)

        res2 = self.client.post("/voice/leave/", data={"session_id": "abc"}, content_type="application/json")
        self.assertEqual(res2.status_code, 400)

        res3 = self.client.post("/voice/leave/", data={"user_id": "abc"}, content_type="application/json")
        self.assertEqual(res3.status_code, 400)

    def test_cleanup_sessions(self):
        res1 = self.client.post("/voice/session/")
        session_id = res1.json()["session_id"]

        # 강제 cleanup 요청
        res2 = self.client.post("/voice/cleanup/", data={"force": True}, content_type="application/json")
        self.assertEqual(res2.status_code, 200)
        remaining = res2.json().get("remaining", [])
        self.assertNotIn(session_id, remaining)
