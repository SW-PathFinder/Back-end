"""
Old Maid Game Logic Package
===========================

이 패키지는 Old Maid(올드 메이드) 카드 게임의 핵심 로직을 포함합니다.

주요 모듈:
- game: 게임의 전체 로직과 상태 관리
- player: 플레이어 클래스와 관련 기능
- card: 카드 정의와 관련 기능
- deck: 덱 관리 및 카드 배치 로직
"""

from .game import Game
from .player import Player
from .card import Card

__version__ = "1.0.0"
__author__ = "Your Name"

# 패키지에서 공개할 클래스들
__all__ = [
    'Game',
    'Player', 
    'Card',
    'Deck'
]