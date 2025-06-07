
import random

SUIT_DICT = {
    "spade": "♠",
    "heart": "♥",
    "diamond": "♦",
    "club": "♣",
    "joker": "🃏"
}  # 카드 무늬 딕셔너리
class CardSet:
    def __init__(self):
        self.cards = [Card(suit, num) for num in range(1, 14) for suit in SUIT_DICT if suit != "joker"]
        self.cards.append(Card("joker", 0))  # 조커 추가
        print(self.cards)
        self.shuffle()
    def shuffle(self):
        random.shuffle(self.cards)
    def __call__(self, *args, **kwds):
        return self.cards.copy()
    def __str__(self):
        return str(self.cards)




class Card:
    def __init__(self, suit,num):
        self.num : int = num  # 카드 번호
        self.suit : str = suit
        self.color : str = "red" if suit in ["heart", "diamond"] else "black"  # 카드 색상
        self.map = self._getCardMap(num,suit)  # 카드 모양

    def _getCardMap(self,num,suit):
        match num:
            case 0:
                return "┏┳┳┳┳┳┓\n┣╋╋╋╋╋┫\n┣╋╋╋╋╋┫\n┣╋╋╋╋╋┫\n┕┻┻┻┻┻┚"  # 조커 카드 모양
            case 1:
                number = " A"  # Ace
            case 11:
                number = " J"  # Jack
            case 12:
                number = " Q"  # Queen
            case 13:
                number = " K"  # King
            case _:
                number = f"{num:2d}"  # 일반 숫자 카드
        simbol = SUIT_DICT[suit]  # 카드 무늬에 해당하는 심볼 가져오기
        map =[
            f"┏-----┓",
            f"|{number:<5}|",
            f"|  {simbol}  |",
            f"|     |",
            f"┕-----┚"
        ]
        return "\n".join(map)  # 카드 모양 반환 함수
    def __str__(self, *args, **kwds):
        return f"({self.suit}, {self.num})"
    def __repr__(self):
        """객체의 공식적인 문자열 표현 (디버깅용)"""
        return {"suit": self.suit, "num": self.num, "color": self.color, "map": self.map}.__repr__()
