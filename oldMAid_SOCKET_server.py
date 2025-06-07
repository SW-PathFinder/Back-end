"""game_socket_server.py
─────────────────────────────────────────────────────────────────
Python Socket.IO 게임 서버 (ASGI)
* python-socketio >= 5
* uvicorn >= 0.23

실행 방법
---------
개발 중 **자동 리로드**가 필요하면:
    uvicorn SOCKET_server:app --reload --port 3000

VS Code 디버거·단일 프로세스로 빠르게 띄우고 싶다면(리로드 없음):
    python SOCKET_server.py
"""

from __future__ import annotations

from typing import Dict, Any
import socketio
from pathlib import Path
import json
import random
import string
import asyncio  # 비동기 타이머를 위한 라이브러리

# ─────────────────────────  게임 로직 ─────────────────────────
from OldMaid.game import Game  # 기존 Game 클래스를 그대로 사용
from OldMaid.card import Card
# ─────────────────────────  전역 상수 ─────────────────────────
MIN_PLAYER_COUNT = 2  # 최소 플레이어 수
MAX_PLAYER_COUNT = 6  # 최대 플레이어 수
TURN_TIMER_DURATION = 30  # 기본 턴 타이머 시간 (초)
# ─────────────────────────  전역 저장소 ────────────────────────
game_sessions: Dict[str, Game] = {}   # room_name → Game 인스턴스
sid_to_user: Dict[str, str] = {}      # sid → username
user_to_sid: Dict[str, str] = {}      # username → sid (DM용)
connected_users: set = set()          # 연결된 사용자 이름 목록 (중복 방지용)
response_index:int = 0          # 응답 인덱스 (브로드캐스트 순서 보장용)
# 게임 방 정보를 저장하는 구조
class GameRoom:
    def __init__(self, room_id: str, host: str, is_public: bool, max_players: int, card_helper: bool):
        self.room_id = room_id              # 방 ID (고유)
        self.host = host                    # 방장 이름
        self.is_public = is_public          # 공개 여부
        self.max_players = max_players      # 최대 플레이어 수
        self.card_helper = card_helper      # 카드 배치 도우미 사용 여부
        self.players = []                   # 참가중인 플레이어 목록
        self.is_started = False             # 게임 시작 여부
        self.countdown_task = None          # 카운트다운 태스크 참조
        self.is_countdown_active = False    # 카운트다운 활성화 여부

        # ───────────────────────── 턴타이머 ────────────────────
        self.turn_timer_task = None         # 턴 타이머 태스크 참조
        self.current_turn_player = None     # 현재 턴 플레이어
        self.turn_timer_duration = 30       # 턴 타이머 시간 (초)

    def to_dict(self):
        """방 정보를 딕셔너리로 변환"""
        return {
            "room_id": self.room_id,
            "host": self.host,
            "is_public": self.is_public,
            "max_players": self.max_players,
            "card_helper": self.card_helper,
            "players": self.players,
            "player_count": len(self.players),
            "is_started": self.is_started
        }
    async def start_turn_timer(self, current_player: str, duration: int = 30):
        """턴 타이머 시작"""
        # 이전 타이머가 있다면 취소
        await self.cancel_turn_timer()
        
        self.current_turn_player = current_player
        self.turn_timer_duration = duration
        
        print(f"방 {self.room_id} - {current_player}의 턴 타이머 시작 ({duration}초)")
        
        # 턴 타이머 시작 알림
        await broadcast(self.room_id, "turn_timer_started", {
            "current_player": current_player,
            "duration": duration,
            "message": f"{current_player}님의 턴입니다. {duration}초 안에 행동하세요!"
        })
        
        # 비동기 타이머 시작
        self.turn_timer_task = asyncio.create_task(self._run_turn_timer(current_player, duration))

    async def _run_turn_timer(self, current_player: str, duration: int):
        """턴 타이머 실행 (내부 메서드)"""
        try:
            # 타이머 진행
            for i in range(duration, 0, -1):
                # 방이 삭제되었거나 게임이 끝난 경우 종료
                if not self.is_started:
                    print(f"턴 타이머 취소: 방 {self.room_id} - 게임 종료")
                    return
                
                # 게임에서 현재 플레이어가 변경된 경우 (이미 행동을 했을 경우) 종료
                game = get_game(self.room_id)
                if game.currentPlayer != current_player:
                    print(f"턴 타이머 취소: 플레이어가 이미 행동함 ({current_player} -> {game.currentPlayer})")
                    return
                    
                # 10초, 5초, 3초, 2초, 1초일 때만 알림 (너무 많은 알림 방지)
                if i in [10, 5, 3, 2, 1]:
                    # await broadcast(self.room_id, "turn_timer_tick", {
                    #     "current_player": current_player,
                    #     "seconds_left": i,
                    #     "message": f"{current_player}님의 턴 - 남은 시간: {i}초"
                    # })
                    await chat("server", {"room": self.room_id, "message": '' + current_player + '님의 턴 - 남은 시간: ' + str(i) + '초'})
                
                await asyncio.sleep(1)
            
            # 타이머 종료 후 자동 턴 변경
            if self.is_started:
                game = get_game(self.room_id)
                
                # 여전히 같은 플레이어의 턴인 경우에만 자동 턴 변경
                if game.currentPlayer == current_player:
                    print(f"방 {self.room_id} - {current_player}의 시간 초과, 자동 턴 변경")
                    
                    # 자동 턴 변경 알림
                    # await broadcast(self.room_id, "turn_timeout", {
                    #     "player": current_player,
                    #     "message": f"{current_player}님이 시간 초과로 턴이 넘어갑니다."
                    # })
                    await chat("server", {"room": self.room_id, "message": '' + current_player + '님이 시간 초과로 턴이 넘어갑니다.'})
                    
                    
                    # 게임 로직에서 턴 변경 실행
                    try:
                        await chat(user_to_sid.get(self.current_turn_player), {"room": self.room_id, "message": '{"type":"endTime"}'})
                    except Exception as e:
                        print(f"자동 턴 변경 중 오류: {e}")
                        
        except asyncio.CancelledError:
            print(f"방 {self.room_id}의 턴 타이머가 취소되었습니다.")
        finally:
            # 타이머 정리
            self.turn_timer_task = None
            self.current_turn_player = None

    async def cancel_turn_timer(self):
        """현재 진행 중인 턴 타이머 취소"""
        if self.turn_timer_task and not self.turn_timer_task.done():
            self.turn_timer_task.cancel()
            try:
                await self.turn_timer_task
            except asyncio.CancelledError:
                pass
            print(f"방 {self.room_id}의 턴 타이머가 취소되었습니다.")
        
        self.turn_timer_task = None
        self.current_turn_player = None


# 게임방 컬렉션 (room_id → GameRoom)
game_rooms: Dict[str, GameRoom] = {} 

# ─────────────────────────  Socket.IO 초기화 ────────────────────
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

# ─────────────────────────  정적 파일 설정 ─────────────────────
# "/" 요청이 들어오면 client.html을 서빙한다고 가정
static_files: Dict[str, str] = {
    '/': 'OldMaid/oldMaidlobby.html',
    '/client.html': 'OldMaid/oldMaidclient.html',
    '/lobby.html': 'OldMaid/oldMaidlobby.html',
}


# ─────────────────────────  StaticApp 정의 ──────────────────────
class StaticApp:
    def __init__(self, socketio_app):
        # socketio_app: socketio.ASGIApp 인스턴스를 받는다.
        self.socketio_app = socketio_app

    async def __call__(self, scope, receive, send):
        scope_type = scope.get('type')

        # 1) HTTP 요청 처리
        if scope_type == 'http':
            path = scope.get('path', '')

            # 1-1) "/socket.io"로 시작하는 경로 → Socket.IO의 HTTP 폴링 또는 핸드셰이크
            if path.startswith('/socket.io'):
                await self.socketio_app(scope, receive, send)
                return

            # 1-2) 정적 파일 서빙 ("/" → client.html)
            if path in static_files:
                try:
                    file_path = Path(__file__).parent / static_files[path]
                    if file_path.exists():
                        content = file_path.read_bytes()
                        await send({
                            'type': 'http.response.start',
                            'status': 200,
                            'headers': [
                                (b'content-type', b'text/html; charset=utf-8'),
                            ],
                        })
                        await send({
                            'type': 'http.response.body',
                            'body': content,
                        })
                        return
                except Exception:
                    # 파일 읽기 중 오류 발생 시 404 처리
                    pass

            # 1-3) 그 외 HTTP 경로 → 404 응답
            await send({
                'type': 'http.response.start',
                'status': 404,
                'headers': [
                    (b'content-type', b'text/plain; charset=utf-8'),
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': b'Not Found',
            })
            return

        # 2) WebSocket 요청 처리
        if scope_type == 'websocket':
            path = scope.get('path', '')

            # 2-1) "/socket.io"로 시작하면 Socket.IO로 위임
            if path.startswith('/socket.io'):
                await self.socketio_app(scope, receive, send)
                return

            # 2-2) 그 외 WebSocket 경로라면 즉시 close
            await send({
                'type': 'websocket.close',
                'code': 1000,  # 정상 종료 코드
            })
            return

        # 3) lifespan 등 그 외 scope는 처리하지 않음
        return


# ─────────────────────────  최종 app 객체 생성 ───────────────────
# ① 순수 Socket.IO용 ASGIApp 생성 (정적 파일 처리 없이 오직 socket.io 전용)
socketio_asgi_app = socketio.ASGIApp(sio)

# ② StaticApp(정적 파일 + Socket.IO) 를 최종 ASGI 앱으로 사용
app = StaticApp(socketio_asgi_app)


# ─────────────────────────  헬퍼 함수 ─────────────────────────
def get_game(room: str) -> Game:
    """방에 대한 Game 인스턴스 확보"""
    if room not in game_sessions:
        game_sessions[room] = Game()
    return game_sessions[room]


async def broadcast(room: str, event: str, data: Any):
    """방 전체 브로드캐스트"""
    global response_index
    data["id"] = response_index
    response_index += 1
    await sio.emit(event, data, room=room)


async def send_private(username: str, event: str, data: Any):
    """특정 유저에게만 전송 (sid 매핑)"""
    global response_index
    data["id"] = response_index
    response_index += 1
    sid = user_to_sid.get(username)
    if sid:
        await sio.emit(event, data, to=sid)


def generate_room_code(length: int = 4) -> str:
    """무작위 방 코드 생성 (4자리 알파벳)"""
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))


def find_matching_rooms(player_count: int, card_helper: bool) -> list:
    """조건에 맞는 공개 방 찾기"""
    matching_rooms = []
    
    for room_id, room in game_rooms.items():
        # 공개방이고, 시작하지 않았으며, 인원 조건 맞고, 자리가 남아있는 방
        if (room.is_public and 
            not room.is_started and 
            room.max_players == player_count and
            room.card_helper == card_helper and
            len(room.players) < room.max_players):
            matching_rooms.append(room.to_dict())
            
    return matching_rooms


# ─────────────────────────  Socket.IO 이벤트 ───────────────────
@sio.event
async def connect(sid, environ):
    # 모든 플레이어에게 현재 플레이어 목록 을 알림
    print("★ 연결:", sid)


@sio.event
async def set_username(sid, data):
    """사용자 이름 설정 및 검증"""
    username = data.get("username", "").strip()
    requestID = data.get("requestId","server_response")
    if not username:
        await sio.emit("username_result", {"requestId":requestID,"success": False, "message": "사용자 이름이 비어있습니다."}, to=sid)
        return
    
    if username in connected_users:
        await sio.emit("username_result", {"requestId":requestID,"success": False, "message": "이미 사용 중인 사용자 이름입니다."}, to=sid)
        return
    
    # 기존 사용자 이름이 있다면 제거
    old_username = sid_to_user.get(sid)
    if old_username:
        connected_users.discard(old_username)
        user_to_sid.pop(old_username, None)
    
    # 새 사용자 이름 설정
    connected_users.add(username)
    sid_to_user[sid] = username
    user_to_sid[username] = sid
    
    await sio.emit("username_result", {"requestId":requestID,"success": True, "username": username}, to=sid)
    print(f"사용자 이름 설정: {username} (sid: {sid})")


@sio.event
async def disconnect(sid):
    """클라이언트 연결 해제"""
    username = sid_to_user.get(sid)
    if username:
        connected_users.discard(username)
        user_to_sid.pop(username, None)
        sid_to_user.pop(sid, None)
        print(f"★ 연결 해제: {username} (sid: {sid})")
    else:
        print(f"★ 연결 해제: {sid}")


@sio.event
async def join_game(sid, data):
    """기존 게임 참가 로직 (backward compatibility)"""
    room = data.get("room")
    player = data.get("player")
    requestID = data.get("requestId","server_response")
    print(f"▶ join_game event: sid={sid}, room={room}, player={player}")
    print(f"▶ join_game raw data: {data}")
    if not room or not player:
        print(f"Invalid join_game data: {data}")
        return

    # 현재 사용자의 이름이 아닌 경우 (sid가 일치하지 않음)
    current_username = sid_to_user.get(sid)
    if current_username != player:
        await sio.emit("error", {"message": "사용자 이름이 일치하지 않습니다."}, to=sid)
        return

    # Socket.IO room 입장
    await sio.enter_room(sid, room)

    # 매핑 저장
    sid_to_user[sid] = player
    user_to_sid[player] = sid
    
    # Game 모델에 플레이어 등록 (이미 등록된 경우 무시)
    game = get_game(room)
    
    # 이미 해당 플레이어가 게임에 존재하는지 확인
    if player in game.players:
        print(f"플레이어 {player}는 이미 방 {room}에 참가중입니다.")
        # 이미 참가한 플레이어는 재알림 없이 조용히 재접속 처리
        return
    
    # 새로운 플레이어 추가
    if not player == "server":
        game.addPlayer(player)
    
    # 전체 알림
    print(f"▶ 새 플레이어 참가 알림: room={room}, player={player}")
    await broadcast(room, "player_joined", {'requestId':requestID,
        "player": player,
        "players": list(game.players.keys()),
        "room": room,
        "player_count": len(game.players) 
    })


@sio.event
async def start_game(sid, data):
    """기존 게임 시작 로직 (backward compatibility)"""
    room = data.get("room")
    requestID = data.get("requestId","server_response")
    if not room:
        return
    
    # 현재 연결된 사용자만 게임 시작 가능
    username = sid_to_user.get(sid)
    if not username:
        await sio.emit("error", {"message": "사용자 정보가 없습니다."}, to=sid)
        return
    
    # 새로운 방 시스템에서 관리하는 방이면 해당 방 정보 업데이트
    if room in game_rooms:
        game_room = game_rooms[room]
        if game_room.host != username:
            await sio.emit("error", {"message": "방장만 게임을 시작할 수 있습니다."}, to=sid)
            return
        
        # 최소 인원 확인
        if len(game_room.players) < 3:
            await sio.emit("error", {"message": "최소 3명의 플레이어가 필요합니다."}, to=sid)
            return
            
        game_room.is_started = True
        
    game = get_game(room)
    game.startGame()
    
    # 게임 시작 이벤트 브로드캐스트
    await broadcast(room, "game_started", {'requestId':requestID,
        "target": "all",
        "type": "game_started",
        "data": {
            "players": list(game.players.keys()),
            "current_player": game.currentPlayer,
        },
    })


@sio.event
async def game_action(sid, data):
    """플레이어의 액션을 Game 로직에 위임 → 응답 리스트 broadcast"""
    room = data.get("room")
    player = data.get("player")
    action = data.get("action")
    requestID = data.get("requestId","server_response")
    if not room or not player or not action:
        return
    
    # 현재 사용자의 이름이 아닌 경우 (sid가 일치하지 않음)
    current_username = sid_to_user.get(sid)
    if current_username != player:
        await sio.emit("error", {"message": "사용자 이름이 일치하지 않습니다."}, to=sid)
        return

    game = get_game(room)
    try:
        result = game.action(player, action)

        # 결과를 리스트로 정규화
        if result is None:
            responses = []
        elif isinstance(result, dict):
            responses = [result]
        elif isinstance(result, list):
            responses = result
        else:
            responses = []

    except Exception as exc:
        await send_private(player, "error", {"message": str(exc)})
        return

    # 브로드캐스트 또는 개인 전송
    for res in responses:
        res["requestId"] = requestID  # 응답에 requestId 추가
        if isinstance(res, dict) and res.get("target") == "all":
            await broadcast(room, "game_update", res)
        elif isinstance(res, dict):
            await send_private(res.get("target"), "private_game_update", res)


@sio.event
async def chat(sid, data):
    """일반 채팅 브로드캐스트 및 명령어 처리"""
    room = data.get("room")
    message = data.get("message", "")
    username = sid_to_user.get(sid, "Server")
    print(f"Chat message from {username}: {message}")
    game = get_game(room)
    # if message.startswith('/'):
    #     await process_chat_command(sid, room, username, message)
    if message.startswith('{'):
        await process_json_command(sid, room, username, message)
    else:
        if room:
            await broadcast(room, "chat", {
                "username": username,
                "message": message,
            })

    for player in game.players:
        await process_json_command(sid, room, player, '{"type": "playerState", "data": {}}')

async def process_json_command(sid, room, username, message):
    """JSON 명령어 처리"""
    try:
        # 1) JSON 파싱
        command_data = json.loads(message.replace("'", "\""))

        # 2) 게임 액션 실행
        game = get_game(room)
        result = game.action(username, command_data)

        # 3) 결과를 리스트로 정규화
        if result is None:
            responses = []
        elif isinstance(result, dict):
            responses = [result]
        elif isinstance(result, list):
            responses = result
        else:
            responses = []

        print(f"Command result: {responses}")

        # if RESPONSE에 game_end가 포함되어있다면 게임 종료 및 ROOM 설정, 인원체크 후 카운트다운 조건
        if any(res.get("type") == "game_end" for res in responses):
            game_room = game_rooms.get(room)
            if game_room:
                game_room.is_started = False
                # del game_room.game_sessions
                game_rooms[room].countdown_task = asyncio.create_task(start_countdown(room))
        if any(res.get("type") == "turn_change" for res in responses):
                # 방에서 턴 타이머 시작
                game_room = game_rooms.get(room)
                if game_room and game_room.is_started:
                    current_player = game.currentPlayer
                    if current_player:
                        # 30초 타이머 시작
                        await game_room.start_turn_timer(current_player, 30)
        # 5) 게임 상태 업데이트
        for res in responses:
            if isinstance(res, dict) and res.get("target") == "all":
                await broadcast(room, "game_update", res)
            elif isinstance(res, dict):
                await send_private(res.get("target"), "private_game_update", res)
            else:
                print(f"Warning: Invalid response format: {res}")

    except json.JSONDecodeError:
        await send_private(username, "error", {"message": f"잘못된 JSON 형식: {message}"})
    except Exception as e:
        await send_private(username, "error", {"message": f"명령어 실행 중 오류: {str(e)}"})


# async def process_chat_command(sid, room, username, message):
#     """채팅 명령어 처리"""
#     try:
        
#         # 1) "/" 제거 후 공백으로 분할
#         parts = message[1:].split()
#         game = get_game(room)
        
#         if not parts:
#             return

#         command = parts[0].lower()
#         print(f"Processing chat command: {command} from {username}")

#         match command:
#             case "board":
#                 recivedMessage = game.board.showBoard()
#                 responses = {
#                     "type": "board_info",
#                     "data": "\n"+recivedMessage
#                 }
#                 await send_private(username, "private_game_update", responses)
#                 return  
#             case "card":
#                 cardMap = Card(int(parts[1])).map
#                 for l in cardMap:
#                     responses = {
#                         "type": "card_info",
#                         "data": "\n".join([''.join(l) ])
#                     } 
#                     # print(responses)
#                     await send_private(username, "private_game_update", responses)
#                 return
#             case "hand":
#                 game = get_game(room)
#                 player = game.players.get(username)
#                 if not player:
#                     await send_private(username, "error", {"message": "게임에 참여하지 않았습니다."})
#                     return
#                 hand_cards = player.hand
#                 current_player = game.currentPlayer
#                 role = player.role
#                 hands = [" ".join(["".join(hand_cards[i].map[j]) for i in range(len(hand_cards))]) for j in range(5)]
#                 limits = str(player.limit)[1:-1]
#                 print  ([f"내 역할 : {role}   |   현재플레이어 : {current_player}"],[" ".join(f"   {j}   " for j in range(len(hand_cards)))],hands,[limits])
#                 hands = [f"내 역할 : {role}   |   현재플레이어 : {current_player}"]+[" ".join(f"   {j}   " for j in range(len(hand_cards)))]+hands+[limits]
#                 responses = {
#                     "type": "hand_info",
#                     "data": "\n".join(hands)
#                 }
#                 await send_private(username, "private_game_update", responses)
#                 return
                
#             case "roominfo":
#                 print("roominfo")
#                 print(game_rooms)
#                 roomInfo = room
#                 print("----------------",roomInfo)
#                 r = game_rooms.get(roomInfo)
#                 print("roomInfo", r)
#                 print("roomInfo", r.__dict__)
#                 if roomInfo:
#                     # 방 정보 요청
#                     responses = {
#                         "type": "room_info",
#                         "data":str(game_rooms.get(room).to_dict())
#                     }
#                     await send_private(username, "private_game_update", responses)
#                     return

#             case "playerstate":
#                 await process_json_command(sid, room, username, '{"type": "playerState", "data": {}}')
#                 return
            
#             case "path":
#                 try:
#                     x = int(parts[1])
#                     y = int(parts[2])
#                     handNum = int(parts[3])
#                     message = {
#                         "type": "path",
#                         "data": {
#                             "x": x,
#                             "y": y,
#                             "handNum": handNum
#                         }
#                     }
#                     await process_json_command(sid, room, username, str(message))
#                     return
#                 except:
#                     await send_private(username, "error", {"message": "잘못된 명령어 형식입니다. 예: /path x y handNum"})
#                     return
#             case "sabotage":
#                 try:
#                     target = str(parts[1])
#                     handNum = int(parts[2])
#                     message = {
#                         "type": "sabotage",
#                         "data": {
#                             "target": target,
#                             "handNum": handNum
#                         }
#                     }
#                     await process_json_command(sid, room, username, str(message))
#                     return
#                 except:
#                     await send_private(username, "error", {"message": "잘못된 명령어 형식입니다. 예: /sabotage target handNum"})
#                     return
#             case "repair":
#                 try:
#                     target = str(parts[1])
#                     handNum = int(parts[2])
#                     message = {
#                         "type": "repair",
#                         "data": {
#                             "target": target,
#                             "handNum": handNum
#                         }
#                     }
#                     await process_json_command(sid, room, username, str(message))
#                     return
#                 except:
#                     await send_private(username, "error", {"message": "잘못된 명령어 형식입니다. 예: /repair target handNum"})
#                     return
#             case "discard":
#                 try:
#                     handNum = int(parts[1])
#                     message = {
#                         "type": "discard",
#                         "data": {
#                             "handNum": handNum
#                         }
#                     }
#                     await process_json_command(sid, room, username, str(message))
#                     return
#                 except:
#                     await send_private(username, "error", {"message": "잘못된 명령어 형식입니다. 예: /discard handNum"})
#                     return
#             case "reverse":
#                 try:
#                     handNum = int(parts[1])
#                     message = {
#                         "type": "reversePath",
#                         "data": {
#                             "handNum": handNum
#                         }
#                     }
#                     await process_json_command(sid, room, username, str(message))
#                     return
#                 except:
#                     await send_private(username, "error", {"message": "잘못된 명령어 형식입니다. 예: /reverse handNum"})
#                     return
#             case _:
#                 # 알 수 없는 명령어
#                 await send_private(username, "error", {"message": f"알 수 없는 명령어: {command}"})
#                 return

#     except (ValueError, IndexError):
#         await send_private(username, "error", {"message": f"명령어 형식이 잘못되었습니다: {message}"})
#     except Exception as e:
#         await send_private(username, "error", {"message": f"명령어 실행 중 오류: {str(e)}"})
#         # 오류 발생 시에도 원본 채팅을 보여줌
#         if room:
#             await broadcast(room, "chat", {
#                 "username": username,
#                 "message": message,
#             })


# ─────────────────────────  새로운 로비 관련 이벤트 핸들러  ─────────────────────

@sio.event
async def create_room(sid, data):
    """방 생성 이벤트"""
    username = sid_to_user.get(sid)
    requestID = data.get("requestId","server_response")
    if not username:
        await sio.emit("error", {"requestId":requestID,"message": "로그인이 필요합니다."}, to=sid)
        return
    
    max_players = data.get("max_players", 3)
    is_public = data.get("is_public", False)
    card_helper = data.get("card_helper", False)
    
    # 유효성 검사
    if not (MIN_PLAYER_COUNT <= max_players <= MAX_PLAYER_COUNT):
        await sio.emit("error", {"requestId":requestID,"message": "유효하지 않은 플레이어 수입니다."}, to=sid)
        return
    
    # 방 코드 생성
    room_id = generate_room_code()
    while room_id in game_rooms:  # 중복 방지
        room_id = generate_room_code()
    
    # 새로운 방 생성
    game_rooms[room_id] = GameRoom(
        room_id=room_id,
        host=username,
        is_public=is_public,
        max_players=max_players, 
        card_helper=card_helper
    )
    
    # 방장을 첫 번째 플레이어로 추가
    game_rooms[room_id].players.append(username)
    
    # 해당 방에 대한 게임 인스턴스도 생성
    game = Game()
    game.addPlayer(username)
    game_sessions[room_id] = game
    
    # Socket.IO 방에 입장
    await sio.enter_room(sid, room_id)
    
    # 방 생성 결과 알림
    await sio.emit("room_created", {"requestId":requestID,
        "success": True,
        "room_id": room_id,
        "room": game_rooms[room_id].to_dict()
    }, to=sid)
    
    print(f"방 생성: {room_id} (호스트: {username}, 최대 {max_players}명, 공개: {is_public})")


@sio.event
async def search_room_by_code(sid, data):
    """방 코드로 검색"""
    username = sid_to_user.get(sid)
    requestID = data.get("requestId","server_response")
    if not username:
        await sio.emit("error", {"message": "로그인이 필요합니다."}, to=sid)
        return
    
    room_code = data.get("room_code")
    if not room_code or room_code not in game_rooms:
        await sio.emit("room_search_result", {"requestId":requestID,
            "success": False,
            "message": "존재하지 않는 방입니다."
        }, to=sid)
        return
    
    room = game_rooms[room_code]
    
    # 이미 시작된 방인지 확인
    if room.is_started:
        await sio.emit("room_search_result", {"requestId":requestID,
            "success": False,
            "message": "이미 게임이 시작된 방입니다."
        }, to=sid)
        return
    
    # 방 인원 초과 여부 확인
    if len(room.players) >= room.max_players:
        await sio.emit("room_search_result", {"requestId":requestID,
            "success": False,
            "message": "방 인원이 가득 찼습니다."
        }, to=sid)
        return
    
    # 방에 참가
    await join_room_by_id(sid, username, room_code)
    
    await sio.emit("room_search_result", {"requestId":requestID,
        "success": True,
        "room": room.to_dict()
    }, to=sid)


@sio.event
async def quick_match(sid, data):
    """빠른 매칭 기능"""
    username = sid_to_user.get(sid)
    requestID = data.get("requestId","server_response")
    if not username:
        await sio.emit("error", {"requestId":requestID,"message": "로그인이 필요합니다."}, to=sid)
        return
    
    max_players = data.get("max_players", 3)
    card_helper = data.get("card_helper", False)
    
    # 유효성 검사
    if not (MIN_PLAYER_COUNT <= max_players <= MAX_PLAYER_COUNT):
        await sio.emit("quick_match_result", {"requestId":requestID,
            "success": False,
            "message": "유효하지 않은 플레이어 수입니다."
        }, to=sid)
        return
    
    # 조건에 맞는 방 찾기
    matching_rooms = find_matching_rooms(max_players, card_helper)
    
    if not matching_rooms:
        # 매칭 실패시 새 방 생성
        await create_room(sid, {
            "max_players": max_players,
            "is_public": True,
            "card_helper": card_helper
        })
        
        # 새 방 정보로 결과 반환 (create_room에서 이미 알림을 보내므로 여기서는 불필요)
        return
    
    # 첫 번째 매칭 방에 입장
    best_match = matching_rooms[0]
    room_id = best_match["room_id"]
    
    # 방에 참가
    await join_room_by_id(sid, username, room_id)
    
    await sio.emit("quick_match_result", {"requestId":requestID,
        "success": True,
        "room": game_rooms[room_id].to_dict()
    }, to=sid)


async def join_room_by_id(sid, username, room_id):
    """방 ID로 입장 (도우미 함수)"""
    if room_id not in game_rooms:
        return False
    
    room = game_rooms[room_id]
    
    # 이미 참여 중인지 확인
    if username in room.players:
        return True
    
    # 방 인원 초과 여부 확인
    if len(room.players) >= room.max_players:
        return False
    
    # 방에 참가
    room.players.append(username)
    
    # 해당 방에 대한 게임 인스턴스에 플레이어 추가
    game = get_game(room_id)
    game.addPlayer(username)
    
    # Socket.IO 방에 입장
    await sio.enter_room(sid, room_id)
      # 모든 참가자에게 알림
    print(f"▶ Broadcasting player_joined: room={room_id}, player={username}, players={room.players}")
    await broadcast(room_id, "player_joined", {
        "player": username,
        "players": room.players,
        "room": room_id,
        "player_count": len(room.players)
    })
    
    # 방 인원이 가득 찼는지 확인하고 카운트다운 시작
    if len(room.players) >= room.max_players and not room.is_started and not room.is_countdown_active:
        print(f"방 {room_id} 인원이 가득 찼습니다. 카운트다운 시작!")
        # 카운트다운 시작 (비동기 태스크로 실행)
        room.countdown_task = asyncio.create_task(start_countdown(room_id))
    
    return True


async def start_countdown(room_id: str, seconds: int = 5):
    """방 인원이 가득차면 카운트다운 시작 후 게임 시작"""
    if room_id not in game_rooms:
        print(f"카운트다운 취소: 방 {room_id}이 존재하지 않음")
        return
    
    room = game_rooms[room_id]
    
    # 이미 게임이 시작되었거나 카운트다운이 활성화된 경우 무시
    if room.is_started or room.is_countdown_active:
        return
    
    room.is_countdown_active = True
    
    # 카운트다운 시작 알림
    await broadcast(room_id, "countdown_started", {
        "seconds": seconds,
        "message": f"방이 가득 찼습니다! {seconds}초 후에 게임이 자동으로 시작됩니다."
    })
    
    # 카운트다운 진행
    for i in range(seconds, 0, -1):
        # 중간에 방이 삭제되었거나 상태가 변경된 경우 종료
        if room_id not in game_rooms or not room.is_countdown_active or len(room.players)!= room.max_players:
            print(f"카운트다운 취소: 방 {room_id}")
            room.is_started = False
            room.is_countdown_active = False
            await chat("server", {"room": room_id, "message": '인원 변경으로 인하여 카운트다운이 취소되었습니다.'})
            return
            
        # 매 초마다 알림
        await broadcast(room_id, "countdown_tick", {
            "seconds_left": i,
            "message": f"게임 시작까지 {i}초..."
        })
        
        await asyncio.sleep(1)
    
    # 카운트다운 종료 후 게임 시작
    if room_id in game_rooms and not room.is_started and room.is_countdown_active :
        room.is_countdown_active = False
        room.is_started = True
        
        # 게임 시작
        print(f"방 {room_id} - 카운트다운 종료, 게임 시작")
        game = get_game(room_id)
        print(game)
        if game.startGame():
            res = {
                "type": "game_started","data": {
                    "players": list(game.players.keys()),}
            }
            await broadcast(room_id, "game_update", res)
            await chat("server", {"room": room_id, "message": '{"type": "roundStart", "data": {}}'})
            
            
        print(f"방 {room_id} - 자동 게임 시작 ({len(room.players)}/{room.max_players}명)")


@sio.event
async def leave_room(sid, data):
    """방 나가기 이벤트 처리"""
    room = data.get("room")
    player = data.get("player")
    print(f"▶ leave_room event: sid={sid}, room={room}, player={player}")
    
    if not room or not player:
        print(f"Invalid leave_room data: {data}")
        return
    
    # 현재 사용자의 이름이 일치하는지 확인
    current_username = sid_to_user.get(sid)
    if current_username != player:
        await sio.emit("error", {"message": "사용자 이름이 일치하지 않습니다."}, to=sid)
        return
        
    # 1. Socket.IO room에서 나가기
    await sio.leave_room(sid, room)
    
    # 2. 게임룸에서 플레이어 제거
    if room in game_rooms:
        game_room = game_rooms[room]
        if player in game_room.players:
            game_room.players.remove(player)
            print(f"플레이어 {player}가 방 {room}에서 나갔습니다.")
            
            # 방에 남은 인원에게 알림
            await broadcast(room, "player_left", {
                "player": player,
                "players": game_room.players,
                "room": room,
                "player_count": len(game_room.players)
            })
            
            # 방에 아무도 없으면 방 삭제
            if len(game_room.players) == 0:
                del game_rooms[room]
                if room in game_sessions:
                    del game_sessions[room]
                print(f"빈 방 {room}을 삭제했습니다.")
            # 방장이 나갔으면 다음 사람에게 방장 권한 이전
            elif game_room.host == player and game_room.players:
                game_room.host = game_room.players[0]
                print(f"새로운 방장: {game_room.host}")
                await broadcast(room, "host_changed", {
                    "new_host": game_room.host
                })
    
    # 3. 게임 인스턴스에서 플레이어 제거
    game = get_game(room)
    if player in game.players:
        game.exitPlayer(player)


# ─────────────────────────  스크립트 실행  ─────────────────────
if __name__ == "__main__":
    # reload 기능은 CLI로 실행할 때만 사용 가능하므로 직접 실행할 때는 끈다
    import uvicorn
    print("Server running → http://localhost:3000 (리로드 없음)")

    print("Server running → http://localhost:3000 (리로드 없음)")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=4000,
        ssl_keyfile="./SSL/openvidu-selfsigned.key",
        ssl_certfile="./SSL/openvidu-selfsigned.crt",
    )