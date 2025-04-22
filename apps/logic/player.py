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
    # def repairLimit(self, card):
    #     if card in self.limit:
    #         self.limit[card] = True
    #     else:
    #         print("error : not a limit card")