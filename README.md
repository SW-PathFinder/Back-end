# 🧠 Voice Chat & Saboteur API Server

Django 기반의 사보타지 게임 백엔드 서버  
**OpenVidu 기반 n:n 음성 채팅**, **턴제 게임 API**, **WebSocket 기반 실시간 통신**,  
**템플릿 기반 채팅 룸 제공**, **AI 추론 서버 연동**을 지원합니다.


## 📌 Features

- 🎙 OpenVidu 기반 n:n 음성 채팅
- 🧩 사보타지 게임 API (게임 생성, 참여, 진행 로직 포함)
- 🧠 AI 인턴 / 의사 / FAQ 응답 API 연동
- 🔄 WebSocket 기반 실시간 메시징 서버 (`SOCKET_server.py`)
- 💬 템플릿 기반 채팅방 및 게임 목록 제공 (`chat_room.html`, `game_list.html`)
- 🧪 테스트 코드 포함 (`apps/saboteur/voice_chat/tests/`)




## 🧑‍💻 Contributors

| Name        | 
|-------------|
| Doohyun Kim | 
| Dami Lee    | 
| Namhoon Cho  | 
| Jiwoo Park  | 

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
# 🔐 Django 기본 설정
# ----------------------------
SECRET_KEY=
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=Asia/Seoul

# ----------------------------
# 🔗 OpenVidu 연동 설정
# ----------------------------
OPENVIDU_URL=
OPENVIDU_SECRET=
SESSION_TIMEOUT_MINUTES=60
OPENVIDU_VERIFY_SSL=false

# ----------------------------
# ⚙️ Django 실행 환경 설정 (선택)
# ----------------------------
DJANGO_SETTINGS_MODULE=config.settings.base
```

---

## 🏃 서버 실행

```bash
python manage.py runserver
```

→ 기본 접속 주소: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔍 Swagger API 문서 확인

→ 기본 접속 주소: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📡 OpenVidu 접근 방법

1. 브라우저에서 아래 주소 접속  
   [https://13.125.231.212:4443](https://13.125.231.212:4443)

2. "이 사이트는 안전하지 않음" → "고급" 클릭
3. "예외적으로 계속" 또는 "무시하고 접속" 선택

---

## 💬 WebSocket 서버 실행

```bash
python SOCKET_server.py
```

- WebSocket 연결 및 실시간 처리 담당
- 향후 게임 턴/채팅 메시지 처리 예정

---

## 📁 디렉토리 구조

```
├── apps/                                 # Django 앱 디렉토리
│   ├── logic/                            # 게임 핵심 로직 모듈 (룰, 처리 등)
│   └── saboteur/                         # 사보타지 게임 관련 기능 구현
│       ├── admin.py                      # Django admin 등록 설정
│       ├── apps.py                       # 앱 설정 클래스
│       ├── models.py                     # 게임 관련 데이터 모델 정의
│       ├── urls.py                       # 게임 관련 URL 라우팅
│       ├── views.py                      # 게임 API 핸들러
│       └── voice_chat/                   # OpenVidu 기반 음성 채팅 기능 모듈
│           ├── openvidu_client.py        # OpenVidu REST API 연동 함수
│           ├── session_store.py          # 세션 상태를 관리하는 임시 저장소
│           ├── urls.py                   # 음성 채팅 관련 URL 설정
│           ├── views.py                  # 음성 채팅 API 처리 뷰
│           └── tests/                    # 음성 채팅 관련 단위 테스트
│               ├── __init__.py
├── config/                               # Django 전체 프로젝트 설정
│   └── settings/                         # 환경별 분리된 설정 모듈
│       ├── __init__.py
│       ├── asgi.py                       # ASGI 서버 설정 (WebSocket 등 비동기 대응)
│       ├── urls.py                       # 프로젝트 루트 URL 라우팅
│       └── wsgi.py                       # WSGI 서버 설정 (Gunicorn 등과 연동)
├── templates/                            # Django 템플릿 디렉토리
│   └── saboteur/
│       ├── chat_room.html                # 채팅방 웹 페이지
│       └── game_list.html                # 게임 목록 웹 페이지
├── static/                               # 정적 파일 (JS, CSS, 이미지 등)
├── manage.py                             # Django 명령행 실행 스크립트
├── SOCKET_server.py                      # WebSocket 서버 실행용 스크립트
├── requirements.txt                      # 프로젝트 Python 패키지 의존성 목록
├── .env.example                          # 환경변수 예시 파일
├── .gitignore                            # Git 추적 제외 파일 목록
└── README.md                             # 프로젝트 설명 문서

```

---

## 🛠️ Tech Stack

| Tool / Library        | Description                           |
|-----------------------|---------------------------------------|
| Django                | 메인 백엔드 프레임워크                |
| Django REST Framework | RESTful API 구성                       |
| OpenVidu              | WebRTC 기반 음성 채팅 라이브러리       |
| Channels       | WebSocket/비동기 처리를 위한 Django 확장 |
| python-dotenv         | `.env` 환경변수 로딩                   |
| HTML Template         | 채팅방 및 대기실 페이지 제공           |
| requests              | 외부 API 호출 (OpenVidu 연동 등)       |

---

## 🧪 테스트 실행

```bash
python manage.py test
```

---

## 📜 Scripts

| Command                        | Description                    |
|-------------------------------|--------------------------------|
| `python manage.py runserver`  | Django 개발 서버 실행          |
| `python SOCKET_server.py`     | WebSocket 서버 실행            |
| `python manage.py test`       | 유닛 테스트 실행               |
| `python manage.py migrate`    | DB 마이그레이션                |
| `python manage.py createsuperuser` | 관리자 계정 생성         |

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

| Tool / Library        | Version / Info                | Description                           |
|-----------------------|-------------------------------|---------------------------------------|
| Python                | ^3.9                          | 백엔드 언어                           |
| Django                | ~4.2                          | 메인 백엔드 프레임워크                |
| Django REST Framework | ^3.14                         | RESTful API 구성                       |
| OpenVidu              | ^2.31                         | WebRTC 기반 음성 채팅 라이브러리       |
| python-dotenv         | latest                        | `.env` 환경변수 로딩                   |
| requests              | latest                        | OpenVidu 외부 API 호출용               |
| HTML (Django Template)| -                             | 채팅방, 대기실 등 HTML 제공           |
| SQLite (기본)         | 내장 DB                        | 개발용 데이터베이스                    |
| Channels (선택사항)   | ^4.0                          | Django의 WebSocket 처리 확장           |
| Gunicorn / Uvicorn    | 선택 시 사용                   | 운영 서버용 WSGI/ASGI 인터페이스       |

