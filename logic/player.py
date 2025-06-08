from enum import Enum
from typing import Dict, List, Any, Literal
from logic.card import Card

class PlayerRole(Enum):
    WORKER = "worker"
    SABOTEUR = "saboteur"
class PlayerStatus(Enum):
    ALIVE = "alive"
    DEAD = "dead"
    DISCONNECTED = "disconnected"


class Player:
    def __init__(self, name):
        self.id = ""
        self.name = name
        self.role = "worker"  # 기본 역할: worker / saboteur
        self.hand : List[Card] = []
        self.gold = 0
        self.limit : Dict[str,bool] = {"mineCart":False,"pickaxe":False,"lantern":False} #[a,b,c]

        self.alive = True

    def setRole(self, role):
        self.role = role # worker / saboteur
    def addGold(self, gold:int):
        if gold < 0:
            return False, "금은 음수일 수 없습니다."
        self.gold += gold
        return True

    def getLimitStatus(self):
        return True in self.limit.values()
    def getLimit(self):
        return list[filter(lambda x: self.limit[x], self.limit.keys())]
    
    def setLimit(self, cardType:str):
        if self.limit[cardType] == False:
            self.limit[cardType] = True
            return True
        else:
            return False, "이미 제한된 장비입니다."
    def repairLimit(self, cardType:list[str],toolType):
        print("수리 전")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        print(f"toolType: {toolType}, cardType: {cardType}, limit: {self.limit}")
        if toolType not in cardType:
            return False, "수리할 장비가 카드와 일치하지 않습니다."
        if self.limit[toolType] == True:
            self.limit[toolType] = False
            print("수리 후", self.limit)
            return True, toolType
        return False, "수리할 수 있는 장비가 없습니다."

    def discard(self, handNum:int):
        # 손패에서 카드를 버리는 로직
        if handNum < len(self.hand):
            card = self.hand.pop(handNum)
            return card
        else:
            return False, "잘못된 카드 번호입니다."
    def drawCard(self, card):
        # 손패에 카드를 추가하는 로직
        self.hand.append(card)
        return True