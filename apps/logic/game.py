from board import Board
from player import Player
from itertools import cycle
from card import Card
import random
class Game:
    def __init__(self):
        self.players = {}      # 플레이어 객체들을 저장
        self.gameState = "init"  # 게임 상태: "init", "playing", "ended"
        self.tasks = []           # [{type:"path"|"action", "data":{}}]
        self.board = Board(self)
        self.cards = {}
        self.currentPlayer = 0  # 현재 플레이어의 인덱스
        self.currentRound = 0   # 현재 라운드
        self.status = "ready" # 게임 상태: "ready", "playing", "ended"
        

        pass


##### 대기실 #######
    def addPlayer(self, player:str):
        self.players[player] = Player(player)
        pass
    def exitPlayer(self, player:str):
        self.players.pop(player)
        pass
    def startGame(self):
        self.gameState = "playing"
        # self.players의 순서를 랜덤으로
        playersKeys = list(self.players.keys())
        random.shuffle(playersKeys)
        self.players = {key: self.players[key] for key in playersKeys}
        self.currentPlayer = cycle(self.players.keys())

        pass
    

##### 인게임 #######
    def roundStart(self,first_player = 0):
        self._shuffulePlayerRoles()
        self._shuffuleCards()
        for player in self.players.values():
            print(f"{player.name} : {player.role} | {player.hand}")
        # print([(player.role, player.name, player.hand) for player in self.players.values()])
        self.currentRound +=1
        self.currentPlayer = first_player
        return {"type":"status","data":self}
        
    def action(self, player, action):
        # 플레이어가 행동을 수행
        if player == self.currentPlayer:
            # 행동 수행
            print("action : ",action)
            match action["type"]:
                case "path": # action = {"type":"path","data":{"x":x,"y":y,"card":card}}
                    # 경로 추가
                    result = self.board.addCard( action["data"]["card"],action["data"]["x"], action["data"]["y"])
                    print("Result : ",result)
                    if result == True:
                        # 경로 추가 성공
                        self.tasks.append({"type":"path","data":{"x":action["data"]["x"],"y":action["data"]["y"],"card":action["data"]["card"]}})
                        self._nextTrun()
                    else:
                        self.tasks.append({"type":"error","data":result[1]})

                case "rockFail": # action = {"type":"rockFail","data":{"x":x,"y":y}}
                    result = self.board.rockFail(action["data"]["x"],action["data"]["y"])
                    if result == True:
                        # 경로 추가 성공
                        self.tasks.append({"type":"rockFail","data":{"x":action["data"]["x"],"y":action["data"]["y"]}})
                        self._nextTrun()
                    else:
                        self.tasks.append({"type":"error","data":result[1]})
                case "saboteur": # action = {"type":"saboteur","data":{"target":str,"cardType":str}}
                    # 사보타주 행동
                    result = self.players[action["target"]].setLimit(action["data"]["cardType"])
                    if result == True:
                        # 사보타주 성공
                        self.tasks.append({"type":"saboteur","data":{"target":action["target"],"cardType":result[1]}})
                        self._nextTrun()
                    else:
                        self.tasks.append({"type":"error","data":result[1]})
                case "repair": # action = {"type":"repair","data":{"target":str,"cardType":str}}
                    result = self.players[action["target"]].repairLimit(action["data"]["cardType"])
                    if result == True:
                        # 수리 성공
                        self.tasks.append({"type":"repair","data":{"target":action["target"],"cardType":result[1]}})
                        self._nextTrun()
                    else:
                        self.tasks.append({"type":"error","data":result[1]})
                case "viewMap": # action = {"type":"viewMap","data":{"x":x,"y":y}}
                    # 맵 보기
                    result = self.board.viewMap(action["data"]["x"],action["data"]["y"])
                    if result[0] == True:
                        # 맵 보기 성공
                        self.tasks.append({"type":"viewMap","data":{"data":result[1]}})
                        self._nextTrun()
                    else:
                        self.tasks.append({"type":"error","data":result[1]})
        else:
            # 현재 플레이어가 아님
            self.tasks.append({"type":"error","data":"not your turn"})
        response = self.tasks.copy()
        self.tasks.clear()
        return response

                



    def _nextTrun(self):
        # 다음 턴으로 넘어감
        self.currentPlayer +=1
        self.currentPlayer %= len(self.players)
        self.tasks.append({"type":"turn_change","data":self.currentPlayer})

    def _shuffuleCards(self):
        # 카드 섞기
        self.cardIndexes = [1]*4 + [2]*4 + [3]*4 + [4]*4 + [5]*4 + [6]*4 + [7]*4 + [8]*4 + [9]*4 + [10]*3 + [11]*3 + [12]*3 + [13]*3 + [14]*3 + [15]*3 + [16]*3 + [17]*3 + [18]*3 + [19]*3 + [20]*2 + [21]*2 + [22]*2 + [23] + [24] + [25] + [26]*6 + [27]*3
        self.cards = [Card(i) for i in self.cardIndexes]
        
        random.shuffle(self.cards)
        
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


