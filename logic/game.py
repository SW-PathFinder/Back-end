from logic.board import Board
from logic.player import Player
from itertools import cycle
from logic.card import Card , card_image_mapping
from typing import Dict, List, Tuple , Any
import random
class Game:
    def __init__(self):
        ### 공통
        self.players: Dict[str, Player] = {}      # 플레이어 객체들을 저장
        self.tasks : List[Dict] = []           # [{type:"path"|"action", "data":{}}]
        ### SABOTEAUR
        self.board = Board(self)
        self.cards: List[Card] = []
        self.goldCard = []
        self.currentPlayer = ""  # 현재 플레이어의 인덱스
        self.currentRound = 0   # 현재 라운드
        self.status = "ready" # 게임 상태: "ready", "playing", "ended"
        pass
    def init(self):
        self.players = {player: Player(player) for player in self.players}  # 플레이어 이름을 키로 하는 딕셔너리로 변환
        # self.tasks = []  # 작업 리스트 초기화
        self.currentPlayer = ""
        self.currentRound = 0
        self.status = "ready"
        self.board = Board(self)  # 보드 객체 초기화
        self.cards = []
        self.goldCard = []
        self.cardIndexes = []
        self.roles = []  # 플레이어 역할 리스트
        self.current_index = 0  # 현재 플레이어 인덱스

##### 대기실 #######
    def addPlayer(self, player:str):
        self.players[player] = (Player(player))
        pass
    def exitPlayer(self, player:str):
        self.players.pop(player)
        pass
    def startGame(self):
        self._shuffleGoldCard()
        # self.players의 순서를 랜덤으로
        playersKeys = list(self.players.keys())
        random.shuffle(playersKeys)
        self.players = {key: self.players[key] for key in playersKeys}
        self.currentPlayer = playersKeys[0]
        # res = self.roundStart()
        return True
    

##### 인게임 #######
    def roundStart(self):
        del self.board
        print("Board reset")
        self.board = Board(self)
        self.cards = []
        for player in self.players.values():
            player.hand = []
            player.role = "worker"
            player.limit = {"mineCart":False,"pickaxe":False,"lantern":False}

        self._shuffulePlayerRoles()
        self._shuffuleCards()
        self.currentPlayer= list(self.players.keys())[0]#임시
        self.currentRound += 1
        # for player in self.players.values():
            # print(f"{player.name} : {player.role} | {player.hand}")
        # print([(player.role, player.name, player.hand) for player in self.players.values()])
        # self.currentRound +=1
        if self.currentRound == 1:
            print("라운드 1이 시작됩니다.")
            response = self.tasks.copy()
            self.tasks.clear()
            return response
        else:
            print("게임이 시작되었습니다.")
            return None
    

    def action(self, player, action):
        # 플레이어가 행동을 수행
        # print(f"action : {action} by {player}")
        if action["type"] == "roundStart":
            print("게임 시작")
            # 게임 시작
            self.roundStart()
            for name,player in self.players.items():
                hand = [(card.num,card.flip==True) for card in player.hand]
                self.tasks.append({"player":"server","target":name,"type":"roundStart","data":{"hand":hand,"role":player.role,"currentRound":self.currentRound}})
            self.tasks.append({"player":"server","target":"all","type":"turn_change","data":self.currentPlayer})
            print(f"라운드 {self.currentRound}이 시작됩니다.")
            response = self.tasks.copy()
            self.tasks.clear()
            return response
        # debug
        # if action["type"] == "hand":
        #     data = {"hand":['\n'.join(''.join(r) for r in self.players[player].hand[0].map)]}
        #     data = {"hand":[{"num":card.num, "flip":card.flip} for card in self.players[player].hand]}
        #     # print(data)
        #     return {"player":"server","target":player,"type":"hand","data":data}

        elif action["type"] == "playerState":
            data = self.getPlayerState(player)
            ###디버깅용
            # board = self.board.showBoard()
            board =  [{"x": x, "y": y, "cardId": self.board.board[x, y].num,"reverse":self.board.board[x, y].flip} for x in range(22) for y in range(22) if self.board.board[x, y].num != 0]
            players = {name: {"name":p.name,"role": p.role if player == self.currentPlayer else "?", "limit":p.limit,"gold": p.gold if player == self.currentPlayer else "?", "hand": [{"cardId": card.num,"cardType":card.type, "reverse": card.flip, "tool":card.tool} if name == player else {"cardId": -8,"cardType":"path", "reverse": False} for card in p.hand]} for name, p in self.players.items()}
            currentPlayer = self.currentPlayer
            for card in board:
                if card["cardId"] in (-2,-4,-6):
                    card["cardId"] = -8
            # hand = self.players[player].hand
            # strHand = [" ".join(["".join(hand[cardindex].map[i]) for cardindex in range(len(hand))]) for i in range(5)]
            # hands = [f"현재플레이어 : {self.currentPlayer}   |   내 역할 : {self.players[player].role}   |   잔여덱 : {len(self.cards)}   |   현재 라운드: {self.currentRound}"]+[" ".join([f"   {cardindex}   " for cardindex in range(len(hand))])]+strHand
            return {"player":"server","target":player,"type":"playerState","data":data,"board":board,"players":players,"currentPlayer":currentPlayer}
            #####
            return {"player":"server","target":player,"type":"playerState","data":data}
        elif action["type"] == "gameState":
            # 게임 상태 반환
            data = {
                "round": self.currentRound,
                "players": {name: {"name":player.name,"role": player.role, "limit":player.limit,"gold": player.gold, "hand": [{"cardId": card.num,"cardType":card.type, "reverse": card.flip} for card in player.hand]} for name, player in self.players.items()},
                "currentPlayer": self.currentPlayer,
                # "boardmap": self.board.showBoard(True),
                "board": [{"x": x, "y": y, "cardId": self.board.board[x, y].num,"reverse":self.board.board[x, y].flip if self.board.board[x,y].num not in  (-2,-4,-6) else -8 , "reverse": self.board.board[x, y].flip == True} for x in range(22) for y in range(22) if self.board.board[x, y].num != 0],
                "deck": [card.num for card in self.cards],
                "goldDeck": self.goldCard
            }
            return {"player":"server","target":"server","type":"gameState","data":data}

            
        elif action["type"] == "endTime":
            print("EndTime이 실행되었습니다. ")
            self.tasks.append({"player":self.currentPlayer,"target":"all","type":"endTime","data":{}})
            result = self.players[self.currentPlayer].discard(handNum=0)
            if result:
                # 카드 버리기 성공
                self.tasks.append({"player":self.currentPlayer,"target":"all","type":"discard","data":{"handNum":0}})
                result = self._drawCard()

                if result[0]:

                    self.tasks.append({"player":self.currentPlayer,"target":self.currentPlayer,"type":"drawCard","data":{"card":result[1].num}})
                else:
                    print(7)
                    self.tasks.append({"player":"server","target":player,"type":"error","data":result[1]})

                self._nextTrun()
            else:
                self.tasks.append({"player":"server","target":player,"type":"error","data":result[1]})
            # 응답 반환
            print("EndTime이 완료되었습니다.")
        elif action["type"] == "reversePath":
            # 경로 뒤집기
            handNum : int = int(action["data"].get("handNum",action["data"]))
            if len(self.players[player].hand)<handNum+1:
                self.tasks.append({"player":"server","target":player,"type":"error","data":"손패 번호가 잘못되었습니다."})
                response = self.tasks.copy()
                self.tasks.clear()
                return response
            card : Card = self.players[player].hand[handNum]
            if card.type == "path":
                card.reversePathCard()
                self.tasks.append({"player":self.currentPlayer,"target":player,"type":"reversePath","data":{"card":card.num}})
            else:
                self.tasks.append({"player":"server","target":player,"type":"error","data":"행동카드는 회전이 불가능합니다."})
           
            response = self.tasks.copy()
            self.tasks.clear()
            return response



        # player action
        elif player == self.currentPlayer:
            # 행동 수행
            # print("action : ",action)

            ############ 손패 검증
            handNum : int = int(action["data"].get("handNum",action["data"]))
            if len(self.players[player].hand)<handNum+1:
                self.tasks.append({"player":"server","target":player,"type":"error","data":"손패 번호가 잘못되었습니다."})
                response = self.tasks.copy()
                self.tasks.clear()
                return response
            card : Card = self.players[player].hand[handNum]
            ############## 데이터 처리
            x = action["data"].get("x",None)
            y = action["data"].get("y",None)
            target = action["data"].get("target",None)
            actionType = card.Info["info"]

            if self.players[player].getLimitStatus() == True and action["type"] == "path":
                # 장비가 제한된 상태에서 경로 카드를 사용하려고 할 때
                self.tasks.append({"player":"server","target":player,"type":"error","data":"장비가 제한된 상태입니다."})
                response = self.tasks.copy()
                self.tasks.clear()
                return response

            match action["type"]:
                case "path": # action = {"type":"path","data":{"x":x,"y":y,"handNum":num0-5}}
                    # 경로 추가
                    if card.type != "path":
                        self.tasks.append({"player":"server","target":player,"type":"error","data":"경로 카드는 경로 추가에만 사용할 수 있습니다."})
                        response = self.tasks.copy()
                        self.tasks.clear()
                        return response
                    
                    result = self.board.addCard(card,x, y)
                    # print("Result : ",result)
                    if result == True:
                        # 경로 추가 성공
                        self.tasks.append({"player":self.currentPlayer,"target":"all","type":"path","data":{"x":x,"y":y,"card":card.num,"reverse":card.flip}})
                        self._useCard(handNum)
                        self._nextTrun()
                    else:
                        self.tasks.append({"player":"server","target":player,"type":"error","data":result[1]})

                case "rockFail": # action = {"type":"rockFail","data":{"x":x,"y":y}}
                    if card.type != "rockFail":
                        self.tasks.append({"player":"server","target":player,"type":"error","data":"돌 찾기 카드는 돌 찾기에만 사용할 수 있습니다."})
                        response = self.tasks.copy()
                        self.tasks.clear()
                        return response
                    result = self.board.rockFail(x,y)
                    if result == True:
                        # 경로 추가 성공
                        self.tasks.append({"player":self.currentPlayer,"target":"all","type":"rockFail","data":{"x":x,"y":y}})
                        self._useCard(handNum)
                        self._nextTrun()
                    else:
                        self.tasks.append({"player":"server","target":player,"type":"error","data":result[1]})
                case "sabotage": # action = {"type":"saboteur","data":{"player":self.currentPlayer,"target":str,"handNum":int}}
                    # 사보타주 행동
                    if card.type != "sabotage":
                        self.tasks.append({"player":"server","target":player,"type":"error","data":"사보타주 카드는 사보타주에만 사용할 수 있습니다."})
                        response = self.tasks.copy()
                        self.tasks.clear()
                        return response
                    result = self.players[target].setLimit(actionType)
                    if result == True:
                        # 사보타주 성공
                        self.tasks.append({"player":self.currentPlayer,"target":"all","type":"sabotage","data":{"player":self.currentPlayer,"target":target,"cardType":actionType}})
                        self._useCard(handNum)
                        self._nextTrun()
                    else:
                        self.tasks.append({"player":"server","target":player,"type":"error","data":result[1]})
                case "repair": # action = {"type":"repair","data":{"player":self.currentPlayer,"target":str,"handNum":int}}
                    if card.type != "repair":
                        self.tasks.append({"player":"server","target":player,"type":"error","data":"수리 카드는 수리에만 사용할 수 있습니다."})
                        response = self.tasks.copy()
                        self.tasks.clear()
                        return response
                    tool = action["data"].get("tool",actionType[0])
                    result = self.players[target].repairLimit(actionType,tool)
                    if result[0] == True:
                        # 수리 성공
                        self.tasks.append({"player":self.currentPlayer,"target":"all","type":"repair","data":{"player":self.currentPlayer,"target":target,"cardType":result[1]}})
                        self._useCard(handNum)
                        self._nextTrun()
                    else:
                        self.tasks.append({"player":"server","target":player,"type":"error","data":result[1]})
                case "viewMap": # action = {"type":"viewMap","data":{"x":x,"y":y}}
                    if card.type != "viewMap":
                        self.tasks.append({"player":"server","target":player,"type":"error","data":"맵 보기 카드는 맵 보기 행동에만 사용할 수 있습니다."})
                        response = self.tasks.copy()
                        self.tasks.clear()
                        return response
                    # 맵 보기
                    result = self.board.viewMap(x,y)
                    if result[0] == True:
                        # 맵 보기 성공
                        self.tasks.append({"player":self.currentPlayer,"target":"all","type":"viewMap","data":{"player":self.currentPlayer,"target":(x,y)}})
                        self.tasks.append({"player":self.currentPlayer,"target":player,"type":"revealDest","data":{"x":x,"y":y,"cardType":result[1]}})
                        self._useCard(handNum)
                        self._nextTrun()
                    else:
                        self.tasks.append({"player":"server","target":player,"type":"error","data":result[1]})
                case "discard": # action = {"type":"drawCard","data":{handNum:0-5}}
                    result = self.players[player].discard(handNum)
                    if result:
                        # 카드 버리기 성공
                        self.tasks.append({"player":self.currentPlayer,"target":"all","type":"discard","data":{"handNum":handNum}})
                        result = self._drawCard()
                        if result[0]:
                            self.tasks.append({"player":self.currentPlayer,"target":player,"type":"drawCard","data":{"card":result[1].num}})
                        else:
                            self.tasks.append({"player":"server","target":player,"type":"error","data":result[1]})
                        self._nextTrun()
                    else:
                        self.tasks.append({"player":"server","target":player,"type":"error","data":result[1]})
                case "reversePath": # action = {"type":"reversePath","data":{handNum:0-5}}
                    if card.type == "path":
                        # 경로 뒤집기
                        card.reversePathCard()
                        self.tasks.append({"player":self.currentPlayer,"target":player,"type":"reversePath","data":{"card":card.num}})
                    else:
                        self.tasks.append({"player":"server","target":player,"type":"error","data":"행동카드는 회전이 불가능합니다."})
        else:
            # 현재 플레이어가 아님
            self.tasks.append({"player":"server","target":player,"type":"error","data":"not your turn"})
        
        checkEnd = self.board.checkEnd()
        checkNoneCard = len(self.cards) == 0 and [player.hand for player in self.players.values()] == [[]]*len(self.players)
        # print(checkEnd)
        end = checkEnd[0]
        endType = checkEnd[1]
        print(f"end : {end}, endType : {endType}, checkNoneCard : {checkNoneCard}")
        print("len(self.cards) : ",len(self.cards))
        # print("[player.hand for player in self.players.values()] : ",[player.hand for player in self.players.values()])
        if end or checkNoneCard:
            if endType == "rock":
                endPosition =checkEnd[2]
                # 돌 찾기 성공
                self.tasks.append({"player":self.currentPlayer,"target":"all","type":"rock_found","data":endPosition})
                end = self.board.checkEnd()
                if end[0] == True:
                    endType = end[1]
                    endPosition = end[2]
                    self.tasks.append({"player":self.currentPlayer,"target":"all","type":"round_end","data":{"winner":"saboteur","roles":{player:self.players[player].role for player in self.players}}})
            elif endType == "gold" or checkNoneCard:
                winner = "worker" if endType == "gold" else "saboteur"
                # self.tasks.append({"player":self.currentPlayer,"target":"all","type":"gold_found","data":endPosition})
                self.tasks.append({"player":self.currentPlayer,"target":"all","type":"round_end","data":{"winner":winner,'roles':{player:self.players[player].role for player in self.players}}})
                # self.tasks에서 type이 drawCard,turn_change는 삭제
                self.tasks = [task for task in self.tasks if task["type"] not in ["drawCard", "turn_change"]]
                # 금 배분
                for player in self.players:
                    if self.players[player].role == "worker" and winner == "worker":
                        # N장 중 가장 큰 숫자부터 순서 역방향으로 배분해주기
                        gold = self.goldCard.pop(0) if len(self.goldCard) > 0 else 0
                        self.players[player].addGold(gold)
                        print(f"{player}에게 {gold} 금이 배분되었습니다.")

                        self.tasks.append({"player":self.currentPlayer,"target":player,"type":"getGold","data":{"gold":gold}})
                    elif self.players[player].role == "saboteur" and winner == "saboteur":
                        lenPlayer = len(self.players)
                        # lenplayer의 수가 4이하는 4개, 5이상9명이하는 3개, 10명이상은 2개
                        goldMaximum = 4 if lenPlayer < 5 else 3 if lenPlayer < 10 else 2
                        currnetGold = 0
                        # print("goldCard : ",self.goldCard)
                        for i in range(len(self.goldCard)):
                            if currnetGold+self.goldCard[i] <= goldMaximum:
                                gold = self.goldCard.pop(i)
                                currnetGold += gold
                                if currnetGold == goldMaximum:
                                    break
                        print(f"{player}에게 {currnetGold} 금이 배분되었습니다.")
                        self.players[player].addGold(currnetGold)
                        self.tasks.append({"player":self.currentPlayer,"target":player,"type":"getGold","data":{"gold":currnetGold}})
                        # 인원에 따라 고
                if self.currentRound == 3:
                    # 금 개수로 순위 매기기
                    golds = {player: self.players[player].gold for player in self.players}
                    sorted_golds = sorted(golds.items(), key=lambda x: x[1], reverse=True)
                    print("금 순위:", sorted_golds)
                    self.tasks.append({"player":self.currentPlayer,"target":"all","type":"game_end","data":{"rank":golds}})
                    self.init()
                else:
                    print("라운드가 종료되었습니다.")
                    self.tasks += self.action("all",{"type":"roundStart"})
                    print("다음 라운드로 넘어갑니다.")
        response = self.tasks.copy()
        self.tasks.clear()
        return response
    
                
    def _drawCard(self):
        # 카드 뽑기
        if len(self.cards) > 0:
            card = self.cards.pop()
            self.players[self.currentPlayer].drawCard(card)
            return True, card
        else:
            return False, "모든 패가 소진되었습니다."
    def _useCard(self, handNum:int):
        if self.players[self.currentPlayer].discard(handNum):
            result = self._drawCard()
            if result[0]:
                # 카드 뽑기 성공            
                self.tasks.append({"player":self.currentPlayer,"target":self.currentPlayer,"type":"drawCard","data":{"card":result[1].num}})
        else:
            return False, "잘못된 카드 번호입니다."


    def _nextTrun(self):
        # 다음 턴으로 넘어감
        self.current_index = list(self.players.keys()).index(self.currentPlayer)
        self.current_index += 1
        self.current_index %= len(self.players)
        self.currentPlayer = list(self.players.keys())[self.current_index]
        self.tasks.append({"player":self.currentPlayer,"target":"all","type":"turn_change","data":self.currentPlayer})

    def _shuffuleCards(self):
        # 카드 섞기
        self.cardIndexes = [1]*4 + [2]*4 + [3]*4 + [4]*4 + [5]*4 + [6]*4 + [7]*4 + [8]*4 + [9]*4 + [10]*3 + [11]*3 + [12]*3 + [13]*3 + [14]*3 + [15]*3 + [16]*3 + [17]*3 + [18]*3 + [19]*3 + [20]*2 + [21]*2 + [22]*2 + [23] + [24] + [25] + [26]*6 + [27]*3
        self.cards = [Card(i) for i in self.cardIndexes]
        # players hand []
        for player in self.players.values():
            player.hand = []
        
        random.shuffle(self.cards)
        for card in self.cards:
            if card.type == "path":
                if random.choice([True, False]):
                    card.reversePathCard()
        
        # 플레이어 수에 따라 카드 분배
        match len(self.players):
            case 3 | 4 | 5:
                # 3, 4, 5명 플레이어: 6장씩
                for player in self.players.values():
                    for i in range(6):
                        player.hand.append(self.cards.pop())
            case 6 | 7:
                # 6, 7명 플레이어: 5장씩
                for player in self.players.values():
                    for i in range(5):
                        player.hand.append(self.cards.pop())
            case 8 | 9 | 10:
                # 8, 9, 10명 플레이어: 4장씩
                for player in self.players.values():
                    for i in range(4):
                        player.hand.append(self.cards.pop())
        # for player in self.players.values():
        #     print(player.name," : ",player.hand)
        # print(self.cards)


    def _shuffulePlayerRoles(self):
        match len(self.players):
            case 3:
                self.roles = ["saboteur", "worker", "worker", "worker"]
            case 4:
                self.roles = ["saboteur", "worker", "worker", "worker", "worker"]
            case 5:
                self.roles = ["saboteur", "saboteur", "worker", "worker", "worker", "worker"]
            case 6:
                self.roles = ["saboteur", "saboteur", "worker", "worker", "worker", "worker", "worker"]
            case 7:
                self.roles = ["saboteur", "saboteur", "saboteur", "worker", "worker", "worker", "worker", "worker"]
            case 8:
                self.roles = ["saboteur", "saboteur", "saboteur", "worker", "worker", "worker", "worker", "worker", "worker"]
            case 9:
                self.roles = ["saboteur", "saboteur", "saboteur", "worker", "worker", "worker", "worker", "worker", "worker", "worker"]
            case 10:
                self.roles = ["saboteur", "saboteur", "saboteur", "saboteur", "worker", "worker", "worker", "worker", "worker", "worker", "worker"]
            case _:
                self.roles = ["worker"]*len(self.players)
        # print(self.roles)
        random.shuffle(self.roles)
        # print(self.roles)
        for i,player in enumerate(self.players):
            self.players[player].setRole(self.roles[i])

        pass


    def _shuffleGoldCard(self):
        # 
        # 금 카드 섞기
        # self.goldCard = 
        self.goldCard = [1]*16+[2]*8+[3]*4
        random.shuffle(self.goldCard)
        # print(self.goldCard)
        for player in self.players.values():
            player.gold = 0
        pass


    def getPlayerState(self, player):
        return {
                "round": self.currentRound,
                "gold": self.players[player].gold,
                "role": self.players[player].role,
                "hands": [{"cardId": card.num, "reverse": card.flip==True,"type":card.type} for card in self.players[player].hand],
                "currentPlayerId": self.currentPlayer,
                "board": [{"x": x, "y": y, "cardId": self.board.board[x, y].num if self.board.board[x,y].num not in  (-2,-4,-6) else -8 , "reverse": self.board.board[x, y].flip == True} for x in range(22) for y in range(22) if self.board.board[x, y].num != 0],
                "deckCount": len(self.cards),
                "players": [{"playerId": p.name, "tool": p.limit, "handCount": len(p.hand)} for p in self.players.values()]
            }