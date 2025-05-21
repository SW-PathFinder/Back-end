import numpy as np


class Card:
    def __init__(self, num, hint=""):
        self.num = num
        self.Info = getCardType(num, hint)
        print(self.Info)
        self.type = self.Info["type"]
        self.path = self.Info["info"][:-1]
        self.flip = self.Info["info"][-1]
        self.map = self.Info.get("map")

    def reversePathCard(self):
        def flip_map(map_array):
            """
            np.array 형태의 map을 상하좌우(180도 회전) 반전한 후,
            특정 문자들을 대응 문자로 변환합니다.
            """
            # 먼저 np.flip을 사용해 행과 열을 모두 뒤집어 180도 회전 효과를 줍니다.
            flipped = np.flip(map_array)

            # 문자별 대응 매핑 (양방향 변환)
            mapping = {
                "┏": "┚",
                "┚": "┏",
                "┓": "┕",
                "┕": "┓",
                "┫": "┣",
                "┣": "┫",
                "┳": "┻",
                "┻": "┳",
            }
            # flipped 배열의 각 문자를 매핑에 따라 변환
            new_array = np.empty_like(flipped)
            for i in range(flipped.shape[0]):
                new_row = []
                for j in range(flipped.shape[1]):
                    ch = flipped[i, j]
                    new_row.append(mapping.get(ch, ch))  # 매핑이 없으면 그대로 사용
                new_array[i] = new_row
            return new_array

        self.flip = not self.flip
        self.map = flip_map(self.map)
        self.path = [
            tuple((x + 1) % 4 + 1 if x != 0 else x for x in tup) for tup in self.path
        ]


def getCardType(cardTtype, hint=""):
    match cardTtype:
        case -5:  # 금!!!!
            return {
                "type": "path",
                "info": [(1, 2, 3, 4), False],
                "map": np.array(
                    [
                        list("┏-----┓"),
                        list("|#####|"),
                        list("|#####|"),
                        list("|#####|"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case -4:  # 금!!!!
            return {
                "type": "path",
                "info": [(1, 2, 3, 4), False],
                "map": np.array(
                    [
                        list("┏-----┓"),
                        list("|#####|"),
                        list("|#####|"),
                        list("|hiden|"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case -3:  # 돌~!~!
            return {
                "type": "path",
                "info": [(1, 2), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |##|"),
                        list("|  ┕--┫"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case -2:  # 돌 히든
            return {
                "type": "path",
                "info": [(1, 2, 3, 4), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |##|"),
                        list("|  ┕--┫"),
                        list("|hiden|"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case -1:  # 시작점
            return {
                "type": "path",
                "info": [(1, 2, 3, 4), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|##|##|"),
                        list("┣--╋--┫"),
                        list("|##|##|"),
                        list("┕--┻--┚"),
                    ]
                ),
            }
        case 0:
            if hint == "":
                return {
                    "type": "path",
                    "info": [(0, 0), False],
                    "map": np.array(
                        [
                            list("       "),
                            list("       "),
                            list("       "),
                            list("       "),
                            list("       "),
                        ]
                    ),
                }
            else:
                return {
                    "type": "path",
                    "info": [(0, 0), False],
                    "map": np.array(
                        [
                            list("       "),
                            list("       "),
                            list(f"{hint}"),
                            list("       "),
                            list("       "),
                        ]
                    ),
                }
        case 1:
            return {
                "type": "path",
                "info": [(1, 3), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("|  |  |"),
                        list("|  |  |"),
                        list("┕--┻--┚"),
                    ]
                ),
            }
        case 2:
            return {
                "type": "path",
                "info": [(1, 2, 3), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("|  ┣--┫"),
                        list("|  |  |"),
                        list("┕--┻--┚"),
                    ]
                ),
            }
        case 3:
            return {
                "type": "path",
                "info": [(1, 2, 3, 4), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("┣--╋--┫"),
                        list("|  |  |"),
                        list("┕--┻--┚"),
                    ]
                ),
            }
        case 4:
            return {
                "type": "path",
                "info": [(1, 2, 4), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("┣--┻--┫"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case 5:
            return {
                "type": "path",
                "info": [(2, 4), False],
                "map": np.array(
                    [
                        list("┏-----┓"),
                        list("|     |"),
                        list("┣-----┫"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case 6:
            return {
                "type": "path",
                "info": [(1, 4), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("┣--┚  |"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case 7:
            return {
                "type": "path",
                "info": [(1, 2), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("|  ┕--┫"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case 8:
            return {
                "type": "path",
                "info": [(1, 0), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("|     |"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case 9:
            return {
                "type": "path",
                "info": [(1, 0), (3, 0), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("|     |"),
                        list("|  |  |"),
                        list("┕--┻--┚"),
                    ]
                ),
            }
        case 10:
            return {
                "type": "path",
                "info": [(1, 0), (2, 0), (3, 0), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("|   --┫"),
                        list("|  |  |"),
                        list("┕--┻--┚"),
                    ]
                ),
            }
        case 11:
            return {
                "type": "path",
                "info": [(1, 0), (2, 0), (3, 0), (4, 0), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("┣-- --┫"),
                        list("|  |  |"),
                        list("┕--┻--┚"),
                    ]
                ),
            }
        case 12:
            return {
                "type": "path",
                "info": [(1, 0), (2, 0), (4, 0), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("┣-- --┫"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case 13:
            return {
                "type": "path",
                "info": [(2, 0), (4, 0), False],
                "map": np.array(
                    [
                        list("┏-----┓"),
                        list("|     |"),
                        list("┣-- --┫"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case 14:
            return {
                "type": "path",
                "info": [(1, 0), (4, 0), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("┣--   |"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case 15:
            return {
                "type": "path",
                "info": [(1, 0), (2, 0), False],
                "map": np.array(
                    [
                        list("┏--┳--┓"),
                        list("|  |  |"),
                        list("|   --┫"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }
        case 16:
            return {
                "type": "path",
                "info": [(2, 0), False],
                "map": np.array(
                    [
                        list("┏-----┓"),
                        list("|     |"),
                        list("|   --┫"),
                        list("|     |"),
                        list("┕-----┚"),
                    ]
                ),
            }

        case 17:  # 3
            return {"type": "action", "info": ("sabotage", "mineCart")}
        case 18:  # 3
            return {"type": "action", "info": ("sabotage", "lentern")}
        case 19:  # 3
            return {"type": "action", "info": ("sabotage", "pickax")}
        case 20:  # 2
            return {"type": "action", "info": ("repair", ["mineCart"])}
        case 21:  # 2
            return {"type": "action", "info": ("repair", ["lentern"])}
        case 22:  # 2
            return {"type": "action", "info": ("repair", ["pickax"])}
        case 23:  # 1
            return {"type": "action", "info": ("repair", ["mineCart", "lentern"])}
        case 24:  # 1
            return {"type": "action", "info": ("repair", ["mineCart", "pickax"])}
        case 25:  # 1
            return {"type": "action", "info": ("repair", ["lentern", "pickax"])}
        case 26:  # 6
            return {"type": "action", "info": ("viewMap",)}
        case 27:  # 3
            return {"type": "action", "info": ("rockFail",)}
