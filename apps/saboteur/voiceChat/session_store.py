import time

SESSION_STORE = {}
SESSION_TIMEOUT_SECONDS = 3600  # 60분

def create_session(session_id, owner_id):
    SESSION_STORE[session_id] = {
        "created_at": time.time(),
        "last_active": time.time(),
        "owner": owner_id,
        "participants": {owner_id},
    }

def touch_session(session_id):
    if session_id in SESSION_STORE:
        SESSION_STORE[session_id]["last_active"] = time.time()

def session_exists(session_id):
    return session_id in SESSION_STORE

def remove_session(session_id):
    SESSION_STORE.pop(session_id, None)

def cleanup_sessions(force=False):
    """
    force=True인 경우 모든 세션을 강제 제거
    force=False인 경우 last_active가 timeout 지난 세션만 제거
    """
    now = time.time()
    expired = []

    for sid, meta in list(SESSION_STORE.items()):
        if force or (now - meta["last_active"] > SESSION_TIMEOUT_SECONDS):
            expired.append(sid)

    for sid in expired:
        remove_session(sid)

def add_participant(session_id, user_id):
    if session_id in SESSION_STORE:
        SESSION_STORE[session_id]["participants"].add(user_id)

def get_participants(session_id):
    return list(SESSION_STORE.get(session_id, {}).get("participants", []))

def remove_participant(session_id, user_id):
    """해당 세션에서 특정 참여자 제거"""
    if session_id in SESSION_STORE:
        SESSION_STORE[session_id]["participants"].discard(user_id)
        # 참여자 없으면 세션도 제거
        if not SESSION_STORE[session_id]["participants"]:
            remove_session(session_id)
