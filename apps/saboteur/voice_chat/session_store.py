# apps/saboteur/voice_chat/session_store.py

import time
from random import choice

# 메모리 기반 세션 저장소: sessionId → session metadata
sessionStore = {}

# 세션 만료 시간 (초) - 기본값은 1시간
sessionTimeoutSeconds = 3600


def createSession(sessionId, ownerId):
    """
    새로운 세션을 생성하고 세션 소유자를 등록
    - createdAt: 세션 생성 시간
    - lastActive: 최근 접근 시간
    - owner: 세션 소유자
    - participants: 참가자 집합 (소유자 포함)
    """
    sessionStore[sessionId] = {
        "createdAt": time.time(),
        "lastActive": time.time(),
        "owner": ownerId,
        "participants": {ownerId},
    }


def touchSession(sessionId):
    """
    세션의 최근 접근 시간을 갱신
    - 세션 유지 또는 만료 판단 기준이 되는 시간
    """
    if sessionId in sessionStore:
        sessionStore[sessionId]["lastActive"] = time.time()


def sessionExists(sessionId):
    """
    세션 존재 여부 확인
    """
    return sessionId in sessionStore


def removeSession(sessionId):
    """
    세션을 메모리 저장소에서 제거
    """
    sessionStore.pop(sessionId, None)


def cleanupSessions(force=False):
    """
    비활성 세션 또는 강제 플래그에 따라 세션을 정리
    - force=True: 모든 세션 제거
    - force=False: lastActive 시간이 만료 기준을 초과한 세션만 제거
    - 제거된 세션 ID 목록 반환
    """
    now = time.time()
    expired = []
    for sid, meta in list(sessionStore.items()):
        if force or (now - meta["lastActive"] > sessionTimeoutSeconds):
            expired.append(sid)
    for sid in expired:
        removeSession(sid)
    return expired


def addParticipant(sessionId, userId):
    """
    세션에 참가자를 추가
    - 이미 존재하는 경우 중복 방지됨 (set 구조)
    """
    if sessionId in sessionStore:
        sessionStore[sessionId]["participants"].add(userId)


def getParticipants(sessionId):
    """
    세션의 참가자 목록을 반환 (list 형태)
    """
    return list(sessionStore.get(sessionId, {}).get("participants", []))


def removeParticipant(sessionId, userId):
    """
    세션에서 특정 참가자를 제거
    - 소유자가 나가는 경우: 남은 참가자 중 1명을 새로운 소유자로 설정
    - 아무도 남지 않은 경우: 세션 자체를 제거
    """
    if sessionId in sessionStore:
        store = sessionStore[sessionId]
        store["participants"].discard(userId)

        if userId == store.get("owner"):
            remaining = list(store["participants"])
            if remaining:
                store["owner"] = choice(remaining)
            else:
                removeSession(sessionId)


def getSessionOwner(sessionId):
    """
    세션의 현재 소유자를 반환
    """
    return sessionStore.get(sessionId, {}).get("owner")

def getParticipantCount(sessionId: str) -> int:
    """
    세션의 참가자 수 반환
    """
    return len(getParticipants(sessionId))