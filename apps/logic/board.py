import numpy as np
from .card import Card, getCardType
import networkx as nx
import random
from copy import deepcopy
class Board:
    # max: x = 22 y = 22

    def __init__(self,game):
        self.game = game
        self.tasks = game.tasks
        self.targets = [(12,13),(10,13),(8,13)]
        random.shuffle(self.targets)
        self.rock = self.targets[1:]
        self.gold = self.targets[0]
        self.home = (10,5)
        print(f"home: {self.home}, gold: {self.gold}, rock: {self.rock}")

        self.path = nx.Graph()
        self.board = self.createLayout()


    def addCard(self, card, x, y, flip=False,rockfail=False):
        # 게임 맵에 카드를 추가하는 로직
        # newCard = Card(card)
        newCard = card
        if flip:
            newCard.reversePathCard()

        if rockfail:
            self.removeNetwork(x,y,self.board[x,y])
            self.board[x,y] = newCard
            self.addNetwork(x,y,newCard)
            return True
        elif not emptyVerification(self.board,x,y): #검증
            return False ,"error emptyVerification"
        elif not nearPathVerification(self.board,x,y,newCard.path): #검증
            print("error nearPathVerification")
            return False,"error nearPathVerification"
        elif not self.totalPathVerification(x,y,newCard): #검증
            print("error totalPathVerification")
            return False,"error totalPathVerification"
        else:
            return True
        
    def rockFail(self, x, y):
        # 돌이 부서지는 로직
        # self.board[x][y] = Card(0)
        if self.board[x][y].num>0:
            for i,j in filter(lambda edge: edge[0] == (x,y) or edge[1] == (x,y), self.path.edges):
                self.path.remove_edge(i,j)
            self.path.nodes[(x,y)]['active'] = False
            self.board[(x,y)] = Card(0)
            self.addNetwork(x,y,self.board[x,y])
            return True
        else:
            return False,"error rockFail"
    def viewMap(self, x, y):
        if self.gold == (x,y):
            # 보물찾기 성공
            return True,"gold"
        elif self.rock[0] == (x,y) or self.rock[1] == (x,y):
            # 돌 찾기 성공
            return True,"rock"
        else:
            # 아무것도 없음
            return False,"잘못된 위치정보입니다."

    def checkEnd(self):
        if self.activeHasPath(self.path,self.home,self.gold):
            print("game end")
            return True, "gold", self.gold
        elif self.activeHasPath(self.path,self.home,self.rock[0]) and self.board[self.rock[0]].num in (-2,-4): 
            newCard = Card(self.board[self.rock[0]].num-1)
            # 근접 카드 위치에 따라 카드 reverse
            if self.board[(self.rock[0][0],self.rock[0][1]-1)].num != 0 and 4 in newCard.path :
                pass
            elif self.board[(self.rock[0][0]-1,self.rock[0][1])].num != 0 and 1 in newCard.path:
                pass
            elif self.board[(self.rock[0][0],self.rock[0][1]+1)].num != 0 and 2 in newCard.path:
                pass
            elif self.board[(self.rock[0][0]+1,self.rock[0][1])].num != 0 and 3 in newCard.path:
                pass
            else:
                newCard.reversePathCard()
            self.board[self.rock[0]] = newCard
            print(f"arrive rock {self.rock[0]}")
            return True, "rock", self.rock[0]
        elif self.activeHasPath(self.path,self.home,self.rock[1]) and self.board[self.rock[1]].num in (-2,-4): 
            newCard = Card(self.board[self.rock[1]].num-1)
            if self.board[(self.rock[1][0],self.rock[1][1]-1)].num != 0 and 4 in newCard.path :
                pass
            elif self.board[(self.rock[1][0]-1,self.rock[1][1])].num != 0 and 1 in newCard.path:
                pass
            elif self.board[(self.rock[1][0],self.rock[1][1]+1)].num != 0 and 2 in newCard.path:
                pass
            elif self.board[(self.rock[1][0]+1,self.rock[1][1])].num != 0 and 3 in newCard.path:
                pass
            else:
                newCard.reversePathCard()
            self.board[self.rock[1]] = newCard
            print(f"arrice rock {self.rock[1]}")
            return True, "rock", self.rock[1]
        else:
            print("game continue")
            return False, "None"

    # 보드 초기화
    def createLayout(self):
        board = np.full((22, 22), Card(0))
        for i in range(22):
            for j in range(22):
                board[i][j] = Card(0,f"({i:2d},{j:2d})")
                self.path.add_node((i,j))
        nx.set_node_attributes(self.path, False, 'active')
        board[*self.home] = Card(-1)
        board[*self.gold] = Card(-6)
        board[*self.rock[0]] = Card(-4)
        board[*self.rock[1]] = Card(-2)
        self.addNetwork(10,5,board[10,5])
        self.addNetwork(self.gold[0],self.gold[1],board[self.gold[0],self.gold[1]])
        self.addNetwork(self.rock[0][0],self.rock[0][1],board[self.rock[0][0],self.rock[0][1]])
        self.addNetwork(self.rock[1][0],self.rock[1][1],board[self.rock[1][0],self.rock[1][1]])
        return board
    

    def addNetwork(self, x,y,card):
        for path in card.path:
            # print(path)
            if 1 in path and 0 not in path:
                self.path.add_edge((x,y),(x-1,y))
            if 2 in path and 0 not in path:
                self.path.add_edge((x,y),(x,y+1))
            if 3 in path and 0 not in path:
                self.path.add_edge((x,y),(x+1,y))
            if 4 in path and 0 not in path:
                self.path.add_edge((x,y),(x,y-1))
        # print("cardpath" )
        self.path.nodes[(x,y)]['active'] = 0 not in card.path
        # print(self.path.edges)
    def removeNetwork(self, x,y,card):
        for i,j in filter(lambda x: x[0] == (10,7) or x[1] == (10,7), self.path.edges):
            self.path.remove_edge(i,j)
            self.path.nodes[(x,y)]['active'] = False
        
    

    ####Verification####
    def totalPathVerification(self,x,y,newCard):
        path = deepcopy(self.path)
        board = deepcopy(self.board)
        self.board[x][y] = newCard
        self.addNetwork(x,y,newCard)
        actvate = self.path.nodes[(x,y)]['active']
        self.path.nodes[(x,y)]['active'] = True
        if self.activeHasPath(self.path,self.home,(x,y)):
            #경로 출력
            print("path: ",nx.shortest_path(self.path,self.home,(x,y)))
            self.path.nodes[(x,y)]['active'] = actvate
            return True
        elif self.activeHasPath(self.path,self.home,(x-1,y)) and (1,0) in newCard.path:
            self.path.nodes[(x,y)]['active'] = actvate
            return True
        elif self.activeHasPath(self.path,self.home,(x,y+1)) and (2,0) in newCard.path:
            self.path.nodes[(x,y)]['active'] = actvate
            return True
        elif self.activeHasPath(self.path,self.home,(x+1,y)) and (3,0) in newCard.path:
            self.path.nodes[(x,y)]['active'] = actvate
            return True
        elif self.activeHasPath(self.path,self.home,(x,y-1)) and (4,0) in newCard.path:
            self.path.nodes[(x,y)]['active'] = actvate
            return True
        else:
            self.path = path
            self.board = board
            return False
    
    def activeHasPath(self, path, source, target):
        # 활성화된 노드들만 포함한 서브그래프 생성
        try:
            active_nodes = [n for n, attr in path.nodes(data=True) if attr.get('active', True)]
            G_active = path.subgraph(active_nodes)
            return nx.has_path(G_active, source, target)
        except:
            return False
    

    def showBoard(self):
        rows, cols = self.board.shape
        # 배열의 각 행을 순회합니다.
        for r in range(rows):
            # 각 셀의 np.array를 행 단위로 문자열로 변환합니다.

            cells_lines = [ ["".join(row) for row in cell.map] for cell in self.board[r, :] ]
            # 각 셀의 문자열은 동일한 줄 수를 가진다고 가정 (여기서는 5줄)
            num_lines = len(cells_lines[0])
            # 셀의 각 줄을 이어 붙여 한 행의 결과를 만듭니다.
            for line_idx in range(num_lines):
                line_parts = [cell_lines[line_idx] for cell_lines in cells_lines]
                print(" ".join(line_parts))  # 각 셀 사이에 공백 추가

def emptyVerification(board,x,y):
    # print(board[x][y].num)
    # print(board[x][y].path)
    if board[x][y].num == 0:
        return True
    else:
        return False

def nearPathVerification(board,x,y,path):
    # 현재 셀의 path를 card 집합으로 변환 (각 튜플 내 숫자들을 모두 모음)
    card = {d for tup in path for d in tup}
    # 현재 셀의 card에 있는 각 방향에 대해 인접 셀의 연결 상태를 검사
    # 위 카드 비교
    if not board[x-1, y].num == 0:
        if (1 in card) != (any(3 in tup for tup in board[x-1, y].path)) :
            print("error at top")
            return False
    # 아래 카드 비교
    if not  board[x+1, y].num == 0:
        if (3 in card) != (any(1 in tup for tup in board[x+1, y].path)) :
            print("error at bottom")
            return False
    # 오른쪽 카드 비교
    if not board[x, y+1].num == 0:
        if (2 in card) != (any(4 in tup for tup in board[x, y+1].path)):
            print("error at right")
            return False
    #왼쪽 카드 비교
    if not board[x, y-1].num == 0:
        if (4 in card) != (any(2 in tup for tup in board[x, y-1].path)) :
            print("error at left")
            return False
    return True