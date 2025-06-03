
import random

SUIT_DICT = {
    "spade": "♠",
    "heart": "♥",
    "diamond": "♦",
    "club": "♣"
}  # 카드 무늬 딕셔너리
class CardSet:
    def __init__(self):
        self.cards = [Card(suit,num) for num in range(1,14) for suit in SUIT_DICT]  # 카드 목록

    def shuffle(self):
        random.shuffle(self.cards)
    




class Card:
    def __init__(self, suit,num):
        self.num : int = num  # 카드 번호
        self.suit : str = "spade"
        self.color : str = "red" if suit in ["heart", "diamond"] else "black"  # 카드 색상
        self.map = self._getCardMap(num,suit)  # 카드 모양

    def _getCardMap(self,num,suit):
        match num:
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
            f"|{number}   |",
            f"|  {simbol}  |",
            f"|     |",
            f"┕-----┚"
        ]
        return "\n".join(map)  # 카드 모양 반환 함수