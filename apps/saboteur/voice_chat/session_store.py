# apps/saboteur/voice_chat/session_store.py

import time

sessionStore = {}
sessionTimeoutSeconds = 3600


def createSession(sessionId, ownerId):
    sessionStore[sessionId] = {
        "createdAt": time.time(),
        "lastActive": time.time(),
        "owner": ownerId,
        "participants": {ownerId},
    }


def touchSession(sessionId):
    if sessionId in sessionStore:
        sessionStore[sessionId]["lastActive"] = time.time()


def sessionExists(sessionId):
    return sessionId in sessionStore


def removeSession(sessionId):
    sessionStore.pop(sessionId, None)


def cleanupSessions(force=False):
    now = time.time()
    expired = []
    for sid, meta in list(sessionStore.items()):
        if force or (now - meta["lastActive"] > sessionTimeoutSeconds):
            expired.append(sid)
    for sid in expired:
        removeSession(sid)


def addParticipant(sessionId, userId):
    if sessionId in sessionStore:
        sessionStore[sessionId]["participants"].add(userId)


def getParticipants(sessionId):
    return list(sessionStore.get(sessionId, {}).get("participants", []))


def removeParticipant(sessionId, userId):
    if sessionId in sessionStore:
        sessionStore[sessionId]["participants"].discard(userId)
        if not sessionStore[sessionId]["participants"]:
            removeSession(sessionId)
