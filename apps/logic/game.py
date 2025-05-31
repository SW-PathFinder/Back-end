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
        self.cards = []
        self.goldCard = []
        self.currentPlayer = ""  # 현재 플레이어의 인덱스
        self.currentRound = 0   # 현재 라운드
        self.status = "ready" # 게임 상태: "ready", "playing", "ended"
        pass


##### 대기실 #######
    def addPlayer(self, player:str):
        self.players[player] = (Player(player))
        pass
    def exitPlayer(self, player:str):
        self.players.pop(player)
        pass
    def startGame(self):
        self.gameState = "playing"
        self._shuffleGoldCard()
        # self.players의 순서를 랜덤으로
        playersKeys = list(self.players.keys())
        random.shuffle(playersKeys)
        self.players = {key: self.players[key] for key in playersKeys}
        self.currentPlayer = playersKeys[0]
        pass
    

##### 인게임 #######
    def roundStart(self):
        del self.board
        self.board = Board(self)
        self.cards = []

        self._shuffulePlayerRoles()
        self._shuffuleCards()
        self.currentPlayer= list(self.players.keys())[0]#임시
        self.currentRound += 1
        # for player in self.players.values():
            # print(f"{player.name} : {player.role} | {player.hand}")
        # print([(player.role, player.name, player.hand) for player in self.players.values()])
        # self.currentRound +=1

        return {"type":"status","data":self}
    

    def action(self, player, action):
        # 플레이어가 행동을 수행
        if action == "roundStart":
            # 게임 시작
            self.roundStart()
            for name,player in self.players.items():
                hand = [(card.num,card.flip) for card in player.hand]
                self.tasks.append({"target":name,"type":"roundStart","data":{"hand":hand,"role":player.role,"currnetRound":self.currentRound}})
            self.tasks.append({"target":"all","type":"turn_change","data":self.currentPlayer})
            if self.currentRound == 1:
                print("라운드 1이 시작됩니다.")
                response = self.tasks.copy()
                self.tasks.clear()
                return response
            else:
                print("게임이 시작되었습니다.")
                return None
                

        if player == self.currentPlayer:
            # 행동 수행
            print("action : ",action)
            handNum = action["data"]["handNum"]
            # print(self.players[player].hand)
            card = Card
            card = self.players[player].hand[handNum]
            
            x = action["data"].get("x",None)
            y = action["data"].get("y",None)
            target = action["data"].get("target",None)
            actionType = card.Info["info"]

            if self.players[player].getLimitStatus() == True and action["type"] == "path":
                # 장비가 제한된 상태에서 경로 카드를 사용하려고 할 때
                self.tasks.append({"target":player,"type":"error","data":"장비가 제한된 상태입니다."})
                response = self.tasks.copy()
                self.tasks.clear()
                return response

            match action["type"]:
                case "path": # action = {"type":"path","data":{"x":x,"y":y,"handNum":num0-5}}
                    # 경로 추가
                    result = self.board.addCard(card,x, y)
                    print("Result : ",result)
                    if result == True:
                        # 경로 추가 성공
                        self.tasks.append({"target":"all","type":"path","data":{"x":x,"y":y,"card":card.num}})
                        self._useCard(handNum)
                        self._nextTrun()
                    else:
                        self.tasks.append({"target":player,"type":"error","data":result[1]})

                case "rockFail": # action = {"type":"rockFail","data":{"x":x,"y":y}}
                    result = self.board.rockFail(x,y)
                    if result == True:
                        # 경로 추가 성공
                        self.tasks.append({"target":"all","type":"rockFail","data":{"x":x,"y":y}})
                        self._useCard(handNum)
                        self._nextTrun()
                    else:
                        self.tasks.append({"target":player,"type":"error","data":result[1]})
                case "sabotage": # action = {"type":"saboteur","data":{"target":str,"cardType":str}}
                    # 사보타주 행동
                    result = self.players[target].setLimit(actionType)
                    if result == True:
                        # 사보타주 성공
                        self.tasks.append({"target":"all","type":"saboteur","data":{"target":target,"cardType":actionType}})
                        self._useCard(handNum)
                        self._nextTrun()
                    else:
                        self.tasks.append({"target":player,"type":"error","data":result[1]})
                case "repair": # action = {"type":"repair","data":{"target":str,"cardType":str}}
                    result = self.players[target].repairLimit(actionType)
                    if result[0] == True:
                        # 수리 성공
                        self.tasks.append({"target":"all","type":"repair","data":{"target":target,"cardType":result[1]}})
                        self._useCard(handNum)
                        self._nextTrun()
                    else:
                        self.tasks.append({"target":player,"type":"error","data":result[1]})
                case "viewMap": # action = {"type":"viewMap","data":{"x":x,"y":y}}
                    # 맵 보기
                    result = self.board.viewMap(x,y)
                    if result[0] == True:
                        # 맵 보기 성공
                        self.tasks.append({"target":"all","type":"viewMap","data":{"target":(x,y)}})
                        self.tasks.append({"target":player,"type":"viewMap","data":{"cardType":result[1]}})
                        self._useCard(handNum)
                        self._nextTrun()
                    else:
                        self.tasks.append({"target":player,"type":"error","data":result[1]})
                case "discard": # action = {"type":"drawCard","data":{handNum:0-5}}
                    result = self.players[player].discard(handNum)
                    if result:
                        # 카드 버리기 성공
                        self.tasks.append({"target":player,"type":"discard","data":{"handNum":handNum}})
                        result = self._drawCard()
                        if result[0]:
                            self.tasks.append({"target":player,"type":"drawCard","data":{"card":result[1]}})
                        else:
                            self.tasks.append({"target":player,"type":"error","data":result[1]})
                        self._nextTrun()
                    else:
                        self.tasks.append({"target":player,"type":"error","data":result[1]})
                case "reversePath": # action = {"type":"reversePath","data":{handNum:0-5}}
                    if card.type == "path":
                        # 경로 뒤집기
                        card.reversePathCard()
                        self.tasks.append({"target":player,"type":"reversePath","data":{"card":card.num}})
                    else:
                        self.tasks.append({"target":player,"type":"error","data":"행동카드는 회전이 불가능합니다."})
        else:
            # 현재 플레이어가 아님
            self.tasks.append({"target":player,"type":"error","data":"not your turn"})
        
        # todo : 게임 종료 조건 체크
        # 1. 보물찾기 성공 체크
        # 2. 이번 라운드 승자 체크
        # 3. 게임 종료 체크
        # 4. 다음 라운드 시작 체크
        # 5. 다음 턴 시작 체크
        checkEnd = self.board.checkEnd()
        print(checkEnd)
        end = checkEnd[0]
        endType = checkEnd[1]
        if end:
            print()
            endPosition =checkEnd[2]

            if endType == "rock":
                # 돌 찾기 성공
                self.tasks.append({"target":"all","type":"rock_found","data":endPosition})
            elif endType == "gold":
                winner = self.players[self.currentPlayer]
                self.tasks.append({"target":"all","type":"gold_found","data":endPosition})
                self.tasks.append({"target":"all","type":"round_end","data":{"winner":winner.role}})
                # self.tasks에서 type이 drawCard,turn_change는 삭제
                self.tasks = [task for task in self.tasks if task["type"] not in ["drawCard", "turn_change"]]
                # 금 배분
                match winner.role:
                    case "worker":
                        "worker"
                    case "saboteur":
                        "saboteur"
                        # 인원에 따라 고
                if self.currentRound == 3:
                    # 금 개수로 순위 매기기
                    golds = {player: self.players[player].gold for player in self.players}
                    sorted_golds = sorted(golds.items(), key=lambda x: x[1], reverse=True)
                    print("금 순위:", sorted_golds)
                    self.tasks.append({"target":"all","type":"game_end","data":{"rank":sorted_golds}})
                else:
                    print("라운드가 종료되었습니다.")


                    self.action("all","roundStart")
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
            return True, "모든 패가 소진되었습니다."
    def _useCard(self, handNum:int):
        if self.players[self.currentPlayer].discard(handNum):
            result = self._drawCard()
            self.tasks.append({"target":self.currentPlayer,"type":"drawCard","data":{"card":result[1].num}})
        else:
            return False, "잘못된 카드 번호입니다."


    def _nextTrun(self):
        # 다음 턴으로 넘어감
        self.current_index = list(self.players.keys()).index(self.currentPlayer)
        self.current_index += 1
        self.current_index %= len(self.players)
        self.currentPlayer = list(self.players.keys())[self.current_index]
        self.tasks.append({"target":"all","type":"turn_change","data":self.currentPlayer})

    def _shuffuleCards(self):
        # 카드 섞기
        self.cardIndexes = [1]*4 + [2]*4 + [3]*4 + [4]*4 + [5]*4 + [6]*4 + [7]*4 + [8]*4 + [9]*4 + [10]*3 + [11]*3 + [12]*3 + [13]*3 + [14]*3 + [15]*3 + [16]*3 + [17]*3 + [18]*3 + [19]*3 + [20]*2 + [21]*2 + [22]*2 + [23] + [24] + [25] + [26]*6 + [27]*3
        self.cards = [Card(i) for i in self.cardIndexes]
        # players hand []
        for player in self.players.values():
            player.hand = []
        
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


    def _shuffleGoldCard(self):
        # 
        # 금 카드 섞기
        # self.goldCard = 
        random.shuffle(self.goldCard)
        # print(self.goldCard)
        for player in self.players.values():
            player.gold = 0
        pass