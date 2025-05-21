# WebSocket 메시지 명세 (GameConsumer 기준)

## game.py action case별 WebSocket JSON 메시지 포맷

### path: 경로 카드 놓기
{
  "type": "action",
  "player": "dami",
  "action": {
    "type": "path",
    "data": {
      "x": 10,
      "y": 11,
      "card": {
        "num": 3
      }
    }
  }
}

### rockFail: 돌 제거 카드 사용
{
  "type": "action",
  "player": "dami",
  "action": {
    "type": "rockFail",
    "data": {
      "x": 10,
      "y": 13
    }
  }
}

### saboteur: 장비 망가뜨리기
{
  "type": "action",
  "player": "dami",
  "action": {
    "type": "saboteur",
    "data": {
      "target": "player2",
      "cardType": "Lamp"
      # cardType은 "Lamp", "pickaxe", "trolley"
    }
  }
}

### repair: 장비 수리
{
  "type": "action",
  "player": "dami",
  "action": {
    "type": "repair",
    "data": {
      "target": "player2",
      "cardType": ["pickaxe"]
      # cardType은 리스트 형태로 보내야 함
    }
  }
}

### viewMap: 목적지 카드 보기
{
  "type": "action",
  "player": "dami",
  "action": {
    "type": "viewMap",
    "data": {
      "x": 12,
      "y": 13
    }
  }
}
