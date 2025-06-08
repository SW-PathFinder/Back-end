import numpy as np

class Card:
    def __init__(self,num,hint=""):
        self.num = num
        self.Info = getCardType(num,hint)
        # print(self.Info)
        self.type = self.Info.get("type",None)
        self.path = self.Info['info'][:-1]
        self.flip = self.Info['info'][-1] if type(self.Info['info'][-1])==bool else self.Info['info']
        self.info = self.Info.get('info')
        self.map = self.Info.get('map')
    
    def to_dict(self):
        """Card 객체를 JSON 직렬화 가능한 딕셔너리로 변환"""
        return {
            "num": self.num,
            "type": self.type,
            "path": self.path,
            "flip": self.flip,
            "info": self.info if not isinstance(self.info, np.ndarray) else self.info.tolist(),
            "map": self.map.tolist() if isinstance(self.map, np.ndarray) else self.map
        }
    
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
                "┏": "┚", "┚": "┏", 
                "┓": "┕", "┕": "┓",
                "┫": "┣", "┣": "┫",
                "┳": "┻", "┻": "┳",
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
        self.path = [tuple((x+1) % 4 +1 if x != 0 else x for x in tup) for tup in self.path]


            

def getCardType(cardTtype, hint=""):
    match cardTtype:
        case -8: #비밀카드
            return {
                "type": "path",
                "info": [(1,2,3,4), False],
                "map": np.array([
                    list("┏-----┓"),
                    list("|*****|"),
                    list("|*****|"),
                    list("|*****|"),
                    list("┕-----┚")
                ])
            }
        case -7:  # 금!!!!
            return {
                "type": "path",
                "info": [(1,2,3,4), False],
                "map": np.array([
                    list("┏-----┓"),
                    list("|#####|"),
                    list("|#####|"),
                    list("|#####|"),
                    list("┕-----┚")
                ])
            }
        case -6:  # 금!!!!
            return {
                "type": "path",
                "info": [(1,2,3,4), False],
                "map": np.array([
                    list("┏-----┓"),
                    list("|#####|"),
                    list("|#####|"),
                    list("|hiden|"),
                    list("┕-----┚")
                ])
            }
        case -5:  # 돌~!~!
            return {
                "type": "path",
                "info": [(2,3), False],
                "map": np.array([
                    list("┏-----┓"),
                    list("|     |"),
                    list("|  ┏--┫"),
                    list("|  |##|"),
                    list("┕--┻--┚")
                ])
            }
        case -4:  # 돌~!~!
            return {
                "type": "path",
                "info": [(1,2,3,4), False],
                "map": np.array([
                    list("┏-----┓"),
                    list("|hiden|"),
                    list("|  ┏--┫"),
                    list("|  |##|"),
                    list("┕--┻--┚")
                ])
            }
        case -3:  # 돌~!~!
            return {
                "type": "path",
                "info": [(1,2), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |##|"),
                    list("|  ┕--┫"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }
        case -2:  # 돌 히든
            return {
                "type": "path",
                "info": [(1,2,3,4), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |##|"),
                    list("|  ┕--┫"),
                    list("|hiden|"),
                    list("┕-----┚")
                ])
            }
        case -1: # 시작점
            return {
                "type": "path",
                "info": [(1,2,3,4), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|##|##|"),
                    list("┣--╋--┫"),
                    list("|##|##|"),
                    list("┕--┻--┚")
                ])
            }
        case 0:
            if hint == "":
                return {
                    "type": "path",
                    "info": [(0,0), False],
                    "map": np.array([
                        list("       "),
                        list("       "),
                        list("       "),
                        list("       "),
                        list("       ")
                    ])}
            else:
                return {
                    "type": "path",
                    "info": [(0,0), False],
                    "map": np.array([
                    list("       "),
                    list("       "),
                    list(f"{hint}"),
                    list("       "),
                    list("       ")
                ])
            }
        case 1:
            return {
                "type": "path",
                "info": [(1,3), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("|  |  |"),
                    list("|  |  |"),
                    list("┕--┻--┚")
                ])
            }
        case 2:
            return {
                "type": "path",
                "info": [(1,2,3), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("|  ┣--┫"),
                    list("|  |  |"),
                    list("┕--┻--┚")
                ])
            }
        case 3:
            return {
                "type": "path",
                "info": [(1,2,3,4), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("┣--╋--┫"),
                    list("|  |  |"),
                    list("┕--┻--┚")
                ])
            }
        case 4:
            return {
                "type": "path",
                "info": [(1,2,4), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("┣--┻--┫"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }
        case 5:
            return {
                "type": "path",
                "info": [(2,4), False],
                "map": np.array([
                    list("┏-----┓"),
                    list("|     |"),
                    list("┣-----┫"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }
        case 6:
            return {
                "type": "path",
                "info": [(1,4), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("┣--┚  |"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }
        case 7:
            return {
                "type": "path",
                "info": [(1,2), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("|  ┕--┫"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }
        case 8:
            return {
                "type": "path",
                "info": [(1,0), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("|     |"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }
        case 9:
            return {
                "type": "path",
                "info": [(1,0), (3,0), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("|     |"),
                    list("|  |  |"),
                    list("┕--┻--┚")
                ])
            }
        case 10:
            return {
                "type": "path",
                "info": [(1,0), (2,0), (3,0), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("|   --┫"),
                    list("|  |  |"),
                    list("┕--┻--┚")
                ])
            }
        case 11:
            return {
                "type": "path",
                "info": [(1,0), (2,0), (3,0), (4,0), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("┣-- --┫"),
                    list("|  |  |"),
                    list("┕--┻--┚")
                ])
            }
        case 12:
            return {
                "type": "path",
                "info": [(1,0), (2,0), (4,0), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("┣-- --┫"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }
        case 13:
            return {
                "type": "path",
                "info": [(2,0), (4,0), False],
                "map": np.array([
                    list("┏-----┓"),
                    list("|     |"),
                    list("┣-- --┫"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }
        case 14:
            return {
                "type": "path",
                "info": [(1,0), (4,0), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("┣--   |"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }
        case 15:
            return {
                "type": "path",
                "info": [(1,0), (2,0), False],
                "map": np.array([
                    list("┏--┳--┓"),
                    list("|  |  |"),
                    list("|   --┫"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }
        case 16:
            return {
                "type": "path",
                "info": [(2,0), False],
                "map": np.array([
                    list("┏-----┓"),
                    list("|     |"),
                    list("|   --┫"),
                    list("|     |"),
                    list("┕-----┚")
                ])
            }

        
        case 17: # 3
            return {"type":"sabotage","info":"mineCart",
                    "map": np.array([
                        list("┏-----┓"),
                        list("|sabot|"),
                        list("|minec|"),
                        list("|     |"),
                        list("┕-----┚")
                    ])}
        case 18: # 3
            return {"type":"sabotage","info":"lantern",
                    "map": np.array([
                        list("┏-----┓"),
                        list("|sabot|"),
                        list("|lante|"),
                        list("|     |"),
                        list("┕-----┚")
                    ])}
        case 19: # 3
            return {"type":"sabotage","info":"pickaxe",
                    "map": np.array([
                        list("┏-----┓"),
                        list("|sabot|"),
                        list("|picka|"),
                        list("|     |"),
                        list("┕-----┚")
                    ])}
        case 20: # 2
            return {"type":"repair","info":["mineCart"],
                    "map": np.array([
                        list("┏-----┓"),
                        list("|repai|"),
                        list("|minec|"),
                        list("|     |"),  # 수정: 공백 문자 길이 맞춤
                        list("┕-----┚")
                    ])}
        case 21: # 2
            return {"type":"repair","info":["lantern"],
                    "map": np.array([
                        list("┏-----┓"),
                        list("|repai|"),
                        list("|lante|"),
                        list("|     |"),  # 수정: 공백 문자 길이 맞춤
                        list("┕-----┚")
                    ])}
        case 22: # 2
            return {"type":"repair","info":["pickaxe"],
                    "map": np.array([
                        list("┏-----┓"),
                        list("|repai|"),
                        list("|picka|"),
                        list("|     |"),  # 수정: 공백 문자 길이 맞춤
                        list("┕-----┚")
                    ])}
        case 23: # 1
            return {"type":"repair","info":["mineCart","lantern"],
                    "map": np.array([
                        list("┏-----┓"),
                        list("|repai|"),
                        list("|minec|"),
                        list("|lante|"),
                        list("┕-----┚")
                    ])}
        case 24: # 1
            return {"type":"repair","info":["mineCart","pickaxe"],
                    "map": np.array([
                        list("┏-----┓"),
                        list("|repai|"),
                        list("|minec|"),
                        list("|picka|"),
                        list("┕-----┚")
                    ])}
        case 25: # 1
            return {"type":"repair","info":["lantern","pickaxe"],
                    "map": np.array([
                        list("┏-----┓"),
                        list("|repai|"),
                        list("|lante|"),
                        list("|picka|"),
                        list("┕-----┚")
                    ])}
        case 26: # 6
            return {"type":"viewMap","info":"viewMap",
                    "map": np.array([
                        list("┏-----┓"),
                        list("|view |"),
                        list("|  Map|"),
                        list("|     |"),
                        list("┕-----┚")
                    ])}
        case 27: # 3
            return {"type":"rockFail","info":"rockFail",
                    "map": np.array([
                        list("┏-----┓"),
                        list("|rockF|"),
                        list("|ail  |"),
                        list("|     |"),
                        list("┕-----┚")
                    ])}

card_image_mapping = {
    # 특수 카드 (목적지/시작점)
    -8: "bg_playable",              # 비밀카드 (DestHidden)
    -7: "path/14",                  # 금 목적지 (DestGold)
    -6: "path/14",                  # 금 목적지 (숨겨진 상태)
    -5: "path/8",                   # 돌 목적지 A (DestRockA)
    -4: "path/8",                   # 돌 목적지 A (숨겨진 상태)
    -3: "path/6",                   # 돌 목적지 B (DestRockB)
    -2: "path/6",                   # 돌 목적지 B (숨겨진 상태)
    -1: "path/27",                  # 시작점 (Origin)
    
    # 길 카드
    1: "path/11",                   # Way2D (세로 길)
    2: "path/13",                   # Way3B (3방향 - 서쪽 제외)
    3: "path/16",                   # Way4 (4방향 모두)
    4: "path/1",                    # Way3A (3방향 - 북쪽 제외)
    5: "path/9",                    # Way2C (가로 길)
    6: "path/0",                    # Way2A (남동쪽)
    7: "path/4",                    # Way2B (북동쪽)
    8: "path/7",                    # 막힌 길 (남쪽만)
    
    # 막힌 길 카드
    9: "path/32",                   # Block2D (남북)
    10: "path/29",                  # Block3B (동남북)
    11: "path/15",                  # Block4 (4방향 막힘)
    12: "path/38",                  # Block3A (동서남)
    13: "path/42",                  # Block2C (동서)
    14: "path/5",                   # Block2A (동남)
    15: "path/2",                   # Block2B (동북)
    16: "path/31",                  # Block1A (동쪽만)
    
    # 액션 카드
    17: "action/sabotage_minecart",      # 수레 파괴
    18: "action/sabotage_lantern",       # 램프 파괴
    19: "action/sabotage_pickaxe",       # 곡괭이 파괴
    20: "action/repair_minecart",        # 수레 수리
    21: "action/repair_lantern",         # 램프 수리
    22: "action/repair_pickaxe",         # 곡괭이 수리
    23: "action/repair_minecart_lantern", # 수레+램프 수리
    24: "action/repair_minecart_pickaxe", # 수레+곡괭이 수리
    25: "action/repair_lantern_pickaxe",  # 램프+곡괭이 수리
    26: "action/map",                     # 지도 보기
    27: "action/destroy",                 # 파괴
}