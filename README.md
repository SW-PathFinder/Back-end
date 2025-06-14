# 🧠 Voice Chat & Saboteur API Server

Django 기반의 사보타지 게임 백엔드 서버  
**OpenVidu 기반 n:n 음성 채팅**, **턴제 게임 API**, **WebSocket 기반 실시간 통신**,  
**템플릿 기반 채팅 룸 제공**, **AI 추론 서버 연동**을 지원합니다.


## 📌 Features

<!-- - 🧩 사보타지 게임 API (게임 생성, 참여, 진행 로직 포함) -->
- 🃏 Saboteur 게임 로직 (`logic/`)
  - 게임 보드 관리 (`board.py`)
  - 카드 및 플레이어 클래스 (`card.py`, `player.py`)
  - 게임 진행 로직 (`game.py`)
-  🔄 WebSocket 기반 실시간 게임 서버 (`SOCKET_server.py`)
  - 게임 상태 동기화 및 실시간 이벤트 처리
  - 게임 인증 및 관전 기능 제공
  - 🎙 OpenVidu 기반 n:n 음성 채팅
- 🔗 OpenVidu 인증 서버 (`openvidu-basic-python/`)
- 🎮 도둑잡기 게임 구현 - 게임서버 재사용 (`OldMaid/`)
- 🖥️ 프론트엔드 테스트 페이지 (`client.html`, `lobby.html`)
- 🛠️ 관리자 페이지 (`client-server.html`)




## 🧑‍💻 Contributors & Role Distribution

| Name        | Role & Responsibilities |
|-------------|------------------------|
| **김도훈 (Dohoon Kim)** | **🎯 전체 기획 및 설계**<br/>• Saboteur 게임 로직 개발 (`logic/`)<br/>• WebSocket 서버 구축 (`SOCKET_server.py`)<br/>• OpenVidu 음성채팅 인증 서버 구축 (`openvidu-basic-python/`)<br/>• 백엔드-프론트엔드 통합 및 고도화<br/>• OpenVidu 서버 Deploy using Physical Server <br/>• Physical Server 구축(네트워크, SSL 인증)|
| **조남훈 (Namhoon Cho)** | **🔄 게이트웨이 재사용성 검증**<br/>• 도둑잡기 게임 로직 개발 (`OldMaid/`)<br/>• 도둑잡기 게임 프론트엔드 개발 (`oldMaidClient.html`, `oldMaidLobby.html`) |
| **이다미 (Dami Lee)** | **🎨 프론트엔드 개발**<br/>• 게임 테스트 페이지 개발 (`client.html`)<br/>• 관리자 페이지 개발 (`client-server.html`)<br/>• 게임 로비 UI/UX 구현 (`lobby.html`) |
| **박지우 (Jiwoo Park)** | **🔧 인프라 구축**<br/>• OpenVidu 서버 Deploy using AWS [참고자료](https://openvidu.io/latest/docs/self-hosting/single-node/aws/install/#configuration-and-administration)|



---

## 🔧 패키지 설치

```bash
# 가상환경 생성 (최초 1회)
python3 -m venv venv

# 가상환경 활성화
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

---

## 🗂️ 환경 변수 설정

`.env.example`을 복사하여 `.env` 생성 후, Slack에 공유된 정보를 기반으로 설정하세요.

```env
# ----------------------------
# 🔗 OpenVidu 연동 설정
# ----------------------------
OPENVIDU_URL=
OPENVIDU_SECRET=
SESSION_TIMEOUT_MINUTES=60
OPENVIDU_VERIFY_SSL=false
```

---

## 🏃 Openvidu 인증 서버 실행

```bash
python /openvidu-basic-python/app.py
```

## 📡 프론트엔드 및 테스트 페이지 접근 방법 (openvidu selfsign 무시)

1. 브라우저에서 아래 주소 접속  
   [https://13.125.231.212:4443](https://13.125.231.212:4443)

2. "이 사이트는 안전하지 않음" → "고급" 클릭
3. "예외적으로 계속" 또는 "무시하고 접속" 선택
4. 로그인창 접근 완료시 창 닫기 후 프론트엔드 접속
<!-- 프론트엔드 페이지는 해당 url, 테스트페이지는  -->

---

## 💬 WebSocket 서버 실행

```bash
python SOCKET_server.py
```

- WebSocket 연결 및 실시간 처리 담당
- 테스트 페이지 구현 (게임 인증 기능 완벽 구현)
[http://127.0.0.1:3000](http://127.0.0.1:3000)

- 서버 페이지 구현 (게임 관전 기능)
1. username을 server로 로그인
2. 코드검색으로 방 진입 시 관전 가능. 

---

## 💬 OldMaid 서버 실행  
- gateway의 재사용을 확인하기 위한 추가 게임 개발


```bash
python oldMAid_SOCKET_server.py
```

- WebSocket 연결 및 실시간 처리 담당
- 테스트 페이지 구현 (모든 기능 구현)
[http://127.0.0.1:4000](http://127.0.0.1:4000)

---


## 📁 디렉토리 구조

```
Back-end/
├── 📁 logic/                           # 게임 핵심 로직 모듈
│   ├── board.py                        # 게임 보드 관리 (카드 배치, 경로 검증)
│   ├── card.py                         # 카드 클래스 및 카드 타입 정의
│   ├── game.py                         # 게임 메인 로직 (플레이어 관리, 턴 처리)
│   └── player.py                       # 플레이어 클래스 (역할, 손패, 도구 제한)
│
├── 📁 OldMaid/                         # 도둑잡기 게임 구현 (별도 게임)
│   ├── __init__.py
│   ├── card.py                         # 도둑잡기 카드 로직
│   ├── deck.py                         # 덱 관리
│   ├── game.py                         # 도둑잡기 게임 로직
│   ├── gameTest.py                     # 게임 테스트 스크립트
│   ├── oldMaidClient.html              # 도둑잡기 클라이언트 HTML
│   ├── oldMaidLobby.html               # 도둑잡기 로비 HTML
│   └── player.py                       # 도둑잡기 플레이어 클래스
│
├── 📁 openvidu-basic-python/           # OpenVidu 음성 채팅 서버
│   ├── app.py                          # Flask 기반 OpenVidu API 서버
│   ├── openvidu-selfsigned.crt         # SSL 인증서
│   ├── openvidu-selfsigned.key         # SSL 개인키
│   ├── README.md                       # OpenVidu 서버 설명서
│   └── requirements.txt                # Python 의존성 목록
│
├── 📁 public/                          # 게임 리소스 (이미지, 아이콘)
│
├── 📁 SSL/                             # SSL 인증서 디렉토리
│   ├── openvidu-selfsigned.crt
│   └── openvidu-selfsigned.key
│
├── 📄 SOCKET_server.py                 # 메인 WebSocket 게임 서버 (Saboteur)
├── 📄 oldMAid_SOCKET_server.py         # 도둑잡기 WebSocket 서버
├── 📄 lobby.html                       # Saboteur 게임 로비 페이지
├── 📄 client.html                      # Saboteur 게임 클라이언트 페이지
├── 📄 client-server.html               # Saboteur 관리자용 클라이언트
├── 📄 openvidu-browser-2.30.0.min.js   # OpenVidu 브라우저 라이브러리
├── 📄 openvidu_app.js                  # OpenVidu 애플리케이션 스크립트
├── 📄 requirements.txt                 # Python 패키지 의존성
├── 📄 README.md                        # 프로젝트 메인 문서

```

---

## 🛠️ Tech Stack

| Tool / Library        | Description                           |
|-----------------------|---------------------------------------|
| uvicorn                | 메인 백엔드 프레임워크                |
| OpenVidu              | WebRTC 기반 음성 채팅 라이브러리       |
| Socket.io       | WebSocket/비동기 처리를 위한 확장 |
| python-dotenv         | `.env` 환경변수 로딩                   |
| requests              | 외부 API 호출 (OpenVidu 연동 등)       |

---

## 📜 Scripts

| Command                        | Description                    |
|-------------------------------|--------------------------------|
| `python openvidu-basic-python/app.py`  | openvidu 인증서버 서버 실행          |
| `python SOCKET_server.py`     | WebSocket 서버 실행            |
| `python oldMAid_SOCKET_server.py` | 도둑잡기 게임 WebSocket 서버 실행 |

---

## 🔗 Project Links

- [🗂 View the project board on JIRA](https://hyu-sw-pathfinder.atlassian.net/jira/software/projects/SWPF/boards/1)
- [📘 View documentation on Notion](https://www.notion.so/Path-Finder-1b3ee3f05d4081d99993c086806cdd25?source=copy_link)
- [🔗 View the repository on GitHub](https://github.com/SW-PathFinder/Back-end.git)

---

## 📄 License

This project is for internal use only.


---

## 🛠️ Tech Stack
## 🛠️ 기술 스택 및 의존성

| Tool / Library        | Version / Info                | Description                           |
|-----------------------|-------------------------------|---------------------------------------|
| Python                | ^3.9                          | 백엔드 메인 언어                       |
| Flask                 | ~2.1.2                        | OpenVidu API 서버 프레임워크           |
| Flask-CORS            | ~3.0.10                       | CORS 정책 처리                        |
| Socket.IO             | ^4.6.1                        | 실시간 양방향 통신                     |
| python-socketio       | ^5.0                          | Python Socket.IO 서버 구현             |
| uvicorn               | ^0.23                         | ASGI 서버 (WebSocket 서버용)           |
| OpenVidu              | 2.30.0                        | WebRTC 기반 음성 채팅 라이브러리       |
| NetworkX              | latest                        | 게임 보드 경로 검증용 그래프 라이브러리  |
| requests              | ~2.28.0                       | OpenVidu 외부 API 호출용               |
| python-dotenv         | ~0.20.0                       | `.env` 환경변수 관리                   |
| urllib3               | latest                        | HTTP 클라이언트 (SSL 경고 처리)        |
| pyOpenSSL             | ~22.0.0                       | SSL/TLS 암호화 지원                    |
| Bootstrap             | 5.3.0                         | 프론트엔드 UI 프레임워크               |
| Font Awesome          | 6.0.0                         | 아이콘 라이브러리                      |
| HTML5 Canvas          | -                             | 게임 보드 렌더링                       |
| JavaScript (ES6+)     | -                             | 클라이언트 사이드 로직                 |
| SSL Certificate       | CA                   | HTTPS/WSS 보안 연결                    |

### 🔧 개발 도구
| Tool                  | Purpose                       | Description                           |
|-----------------------|-------------------------------|---------------------------------------|
| Jupyter Notebook      | 게임 로직 테스트               | 대화형 게임 테스트 환경                |
| VS Code               | 개발 환경                      | 통합 개발 환경                        |
| Git                   | 버전 관리                      | 소스코드 버전 관리                     |

### 🏗️ 아키텍처 구성 요소
| Component             | Technology                    | Description                           |
|-----------------------|-------------------------------|---------------------------------------|
| WebSocket Server      | python-socketio + ASGI        | 실시간 게임 상태 동기화                |
| Voice Chat Server     | Flask + OpenVidu API          | WebRTC 기반 음성 채팅 중계             |
| Game Engine           | Pure Python + NetworkX       | Saboteur 게임 로직 처리                |
| Static File Server    | Custom ASGI App               | HTML/CSS/JS 파일 서빙                  |
| SSL/TLS               | Self-signed Certificate       | 보안 연결 (개발 환경)                  |
