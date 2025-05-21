import json
from channels.generic.websocket import AsyncWebsocketConsumer
from logic.game import Game  # game.py에서 Game 클래스 import

game_instances = {}  # room_code 별 게임 인스턴스 저장용


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"game_{self.room_code}"

        # 없으면 새 게임 만들기
        if self.room_code not in game_instances:
            game_instances[self.room_code] = Game()

        self.game = game_instances[self.room_code]

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        print(f"[CONNECTED] {self.channel_name} joined room {self.room_code}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"[DISCONNECTED] {self.channel_name} left room {self.room_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data["type"] == "join":
            nickname = data["nickname"]
            self.game.addPlayer(nickname)
            print(f"player {nickname} joined")

        elif data["type"] == "start":
            self.game.startGame()
            result = self.game.roundStart()
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "broadcast", "message": result}
            )

        elif data["type"] == "action":
            nickname = data["player"]
            action = data["action"]
            # Convert card num to Card instance if it's a path card
            if action["type"] == "path":
                card_data = action["data"]["card"]
                card_num = card_data.get("num")
                from logic.card import Card  # Fixed import path

                action["data"]["card"] = Card(card_num)
            results = self.game.action(nickname, action)

            for r in results:
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "broadcast", "message": r}
                )

    async def broadcast(self, event):
        await self.send(text_data=json.dumps(event["message"]))
