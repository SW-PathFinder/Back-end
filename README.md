# Voice Chat & Saboteur API 서버

Django 기반 음성채팅 및 Saboteur 게임 API 제공  
OpenVidu 기반 n:n 음성채팅 기능 포함

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

`.env` slack 팀 채팅방에 공유 완료, 복사하여 사용

---

## 🏃 서버 실행

```bash
# 가상환경 실행된 상태에서
python manage.py runserver
```

→ 접속 주소: http://127.0.0.1:8000

---

## 🔍 Swagger API 문서 확인

```bash
# Swagger 문서 접근
http://127.0.0.1:8000/swagger/
```

---

## 🧪 테스트 실행

```bash
python manage.py test
```

---

## 📁 기본 디렉토리 구조

```
├── manage.py
├── config/
│   └── urls.py
├── apps/
│   └── saboteur/
│       ├── views.py
│       └── voiceChat/
│           ├── views.py
│           ├── urls.py
│           └── session_store.py
├── .env.example
├── requirements.txt
```
