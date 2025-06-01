from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]  # <path_finder> 기준
load_dotenv(BASE_DIR / ".env", override=True)