import os
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env', override=True)

# Django 설정 모듈 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# ASGI 애플리케이션 로드
from django.core.asgi import get_asgi_application
application = get_asgi_application()
