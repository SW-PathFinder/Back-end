class Player:
    def __init__(self, name):
        self.id = ""
        self.name = name
        self.role = "worker"  # 기본 역할: worker / saboteur
        self.hand = []
        self.gold = 0
        self.limit = {"Lamp":False,"pickaxe":False,"trolley":False} #[a,b,c]

        self.alive = True



    def setRole(self, role):
        self.role = role # worker / saboteur

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