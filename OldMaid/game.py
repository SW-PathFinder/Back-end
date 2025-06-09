
from .player import Player
from itertools import cycle
from .card import Card, CardSet
from typing import Dict, List, Tuple , Any
import random
class Game:
    def __init__(self):
        ### 공통
        self.players: Dict[str, Player] = {}      # 플레이어 객체들을 저장
        self.playerCycle : cycle = None  # 플레이어 순환을 위한 이터레이터
        self.tasks : List[Dict] = []           # [{type:"path"|"action", "data":{}}]

        # oldMaid 전용
        self.currentPlayer: str = None  # 현재 플레이어
        self.ranking: List[Player] = []  # 게임 종료 후 순위
        self.currentRound: int = 0
        self.cardset: CardSet = CardSet()
        self.deck: List[Card] = self.cardset.cards  # 카드 덱 초기화
        self.maxRound: int = 10  # 최대 라운드 수
    ##### 대기실 #######
    def addPlayer(self, player:str):
        self.players[player] = (Player(player))
        pass
    def exitPlayer(self, player:str):
        self.players.pop(player)
        pass

    def startGame(self):
        # 게임 시작 시 플레이어 초기화
        print("게임 시작")
        return True
    def roundStart(self):
        # 라운드 시작 시 현재 플레이어 설정
        self._initPlayer()
        self._shufflePlayers()
        self._dealCards()
        self.currentPlayer = list(self.players.keys())[0]
        print(f"현재 플레이어: {self.currentPlayer}")
        




    def action(self, player : str, action):



        print(action)

        data = action.get("data",{})
        action = action.get("type","action")
        beforePlayer = self._getBeforePlayer(player)
        if action == "roundStart":
            print("게임 시작")
            # 게임 시작
            self.roundStart()
            for name,player in self.players.items():
                hand = [card for card in player.hand]
                self.tasks.append({"player":"server","target":name,"type":"roundStart","data":{"hand":hand,"currnetRound":self.currentRound}})
            self.tasks.append({"player":"server","target":"all","type":"turn_change","data":self.currentPlayer})
            print("라운드 1이 시작됩니다.")
            response = self.tasks.copy()
            self.tasks.clear()
            return response
        


        
        if action == "playerState":
            print(f"{player}의 상태 요청")
            if player in self.players:
                playerState = {"currentPlayer":self.currentPlayer,"hand":[{"suit":hand.suit,"num":hand.num} for hand in self.players[player].hand]}
                playerState["handMaps"] = [hand.map for hand in self.players[player].hand]
                playerState["players"] = {name:{"alive":p.alive,"handCount":len(p.hand)} for name, p in self.players.items()}
                playerState["beforePlayerHnadCount"] = len(self.players[beforePlayer].hand)
                playerState["beforePlayer"] = beforePlayer
                self.tasks.append({"player":"server","target":player,"type":"playerState","data":playerState})
            else:
                self.tasks.append({"player":"server","target":player,"type":"error","data":"존재하지 않는 플레이어입니다."})
            response = self.tasks.copy()
            self.tasks.clear()
            return response
        if action == "gameState":
            print("게임 상태 요청")
            gameState = {
                "currentPlayer": self.currentPlayer,
                "players": {name: {"alive": p.alive, "hand": {p.hand.suit,p.hand.num}} for name, p in self.players.items()},
                "ranking": [p.name for p in self.ranking],
                "currentRound": self.currentRound,
                "maxRound": self.maxRound
            }
            self.tasks.append({"player":"server","target":player,"type":"gameState","data":gameState})
            response = self.tasks.copy()
            self.tasks.clear()
            return response

        ## 언제든 가능한 행동 // 도둑잡기 게임에서 같은 카드 두개를 내는 행동
        elif action == "dropCard":
            print(f"{player}가 카드를 냈습니다.")
            handNum1 = int(data.get("hand1"))
            handNum2 = int(data.get("hand2"))
            card1 = self.players[player].hand[handNum1]
            card2 = self.players[player].hand[handNum2]
            print(f"{player}가 낸 핸드 번호: {handNum1}, {handNum2}")
            print(f"{player}가 낸 카드: {card1}, {card2}")
            # 카드 번호가 잘못된 경우
            if handNum1 < 0 or handNum2 < 0 or handNum1 >= len(self.players[player].hand) or handNum2 >= len(self.players[player].hand):
                self.tasks.append({"player":self.currentPlayer,"target":player,"type":"error","data":"잘못된 카드 번호입니다."})
                response = self.tasks.copy()
                self.tasks.clear()
                return response
            # 같은 카드 두개를 냈을 때
            elif card1.num == card2.num:
                self.players[player].hand.remove(card1)
                self.players[player].hand.remove(card2)
                self.tasks.append({"player":self.currentPlayer,"target":"all","type":"takeCard","data":{"hand1":handNum1,"hand2":handNum2,"from":player}})
                self._checkPlayerAlive()
                # self._nextTrun()
                self._endCheck()
            else:
                self.tasks.append({"player":self.currentPlayer,"target":player,"type":"error","data":"같은 카드를 두개 내야 합니다."})
                response = self.tasks.copy()
                self.tasks.clear()
                
                return response
            

        ## 플레이어 턴 행동
        elif action == "takeCard":
            if player != self.currentPlayer:
                self.tasks.append({"player":"server","target":player,"type":"error","data":"현재 플레이어가 아닙니다."})
                response = self.tasks.copy()
                self.tasks.clear()
                return response
            handNum = int(data.get("hand"))
            beforePlayer = self._getBeforePlayer(player)
            if handNum < 0 or handNum >= len(self.players[beforePlayer].hand):
                self.tasks.append({"player":"server","target":player,"type":"error","data":"잘못된 카드 번호입니다."})
                response = self.tasks.copy()
                self.tasks.clear()
                return response
            card = self.players[beforePlayer].hand[handNum]
            self.players[beforePlayer].hand.remove(card)
            self.players[player].hand.append(card)
            self.tasks.append({"player":self.currentPlayer,"target":"all","type":"takeCard","data":{"hand":handNum,"from":beforePlayer}})
            self.tasks.append({"player":self.currentPlayer,"target":player,"type":"takeedCard","data":{"card":(card.suit,card.num),"from":beforePlayer}})
            if self._endCheck(): 
                response = self.tasks.copy()
                self.tasks.clear()
                return response        
            self._checkPlayerAlive()
            self._nextTurn()
            print(f"{player}가 {beforePlayer}에게서 카드를 가져왔습니다: {card}")
        elif action == "turnChange":
            self._nextTurn()
            
        elif action == "endTime":
            self.tasks.append({"player":"server","target":"all","type":"endTime","data":{}})
            self._nextTurn()

        response = self.tasks.copy()
        self.tasks.clear()
        return response
    


    def _nextTurn(self):
        # 다음 턴으로 넘어감
        # 다음 플레이어가 살아있는지 확인하고 살아있는 플레이어가 나올때까지 반복
        alivePlayers = [name for name, player in self.players.items() if player.alive or name == self.currentPlayer]
        
        # 살아있는 플레이어가 1명 이하면 턴을 넘길 수 없음
        if len(alivePlayers) <= 1:
            print("살아있는 플레이어가 1명 이하입니다. 게임을 종료합니다.")
            return
        
        try:
            # 살아있는 플레이어 리스트에서 현재 플레이어의 인덱스 찾기
            current_index = alivePlayers.index(self.currentPlayer)
            # 다음 플레이어는 현재 플레이어의 바로 다음 플레이어 (순환)
            next_index = (current_index + 1) % len(alivePlayers)
            self.currentPlayer = alivePlayers[next_index]
            
            print(f"다음 플레이어: {self.currentPlayer}")
            self.tasks.append({"player":"server","target":"all","type":"turn_change","data":self.currentPlayer})
            
        except ValueError:
            # 현재 플레이어가 살아있는 플레이어 리스트에 없는 경우
            print(f"Error: {self.currentPlayer}가 살아있는 플레이어 목록에 없습니다.")
            # 첫 번째 살아있는 플레이어로 설정
            if alivePlayers:
                self.currentPlayer = alivePlayers[0]
                print(f"첫 번째 살아있는 플레이어로 설정: {self.currentPlayer}")
                self.tasks.append({"player":"server","target":"all","type":"turn_change","data":self.currentPlayer})

    def _endCheck(self):
        # 게임 종료 조건 확인
        self._checkPlayerAlive()
        alivePlayers = [name for name, player in self.players.items() if player.alive]
        print(f"생존 플레이어: {alivePlayers}")
        # 생존 플레이어가 1명 이하일 경우 게임 종료
        if len(alivePlayers) <= 1:
            print("게임 종료")
            return self.tasks.append({"player":"server","target":"all","type":"game_end","data":{"rank":self.ranking}})
        return False
    
    def _checkPlayerAlive(self):
        # 플레이어의 생존 여부를 확인
        for player in self.players.values():
            if player.alive and len(player.hand) == 0:
                player.alive = False
                self.ranking.append(player.name)
                self.tasks.append({"player":"server","target":"all","type":"player_eliminated","data":{"name":player.name}})
                print(f"{player.name}이(가) 패를 모두 소진하여 승리하였습니다.")
        

    def _getBeforePlayer(self, player: str) -> str:
        # 현재 플레이어의 이전 플레이어를 반환 만약 이전 플레이어의 .alive가 False라면 그 이전 플레이어를 반환
        alivePlayers = [name for name, p in self.players.items() if p.alive or name == player]
        
        # 살아있는 플레이어가 1명 이하면 None 반환
        if len(alivePlayers) <= 1:
            return None
        
        try:
            # 살아있는 플레이어 리스트에서 현재 플레이어의 인덱스 찾기
            current_index = alivePlayers.index(player)
            # 이전 플레이어는 현재 플레이어의 바로 앞 플레이어 (순환)
            before_index = (current_index - 1) % len(alivePlayers)
            return alivePlayers[before_index]
        except ValueError:
            # 현재 플레이어가 살아있는 플레이어 리스트에 없는 경우
            print(f"Error: {player}가 살아있는 플레이어 목록에 없습니다.")
        return None

    
    def _initPlayer(self):
        # 플레이어 초기화 로직
        for player in self.players.values():
            player.hand = []
            player.alive = True
    def _shufflePlayers(self):
        # 플레이어 순서를 랜덤하게 섞는 로직
        playerNames = list(self.players.keys())
        random.shuffle(playerNames)
        self.players = {name: self.players[name] for name in playerNames}
        self.playerCycle = cycle(self.players.values())
    def _dealCards(self):
        # 플레이어에게 카드를 나누는 로직
        self.deck = CardSet().cards.copy()  # 카드 덱 초기화
        while len(self.deck) > 0:
            for player in self.players.values():
                if len(self.deck) == 0:
                    break
                card = self.deck.pop(0)
                player.hand.append(card)
        # 카드가 남지 않을때까지 배분
