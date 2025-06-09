from enum import Enum
from typing import Dict, List, Any, Literal
from .card import Card
class Player:
    def __init__(self, name):
        self.id = ""
        self.name = name
        self.hand : List[Card] = []
        self.alive = True
    def __repr__(self):
        return self.__dict__.__repr__()