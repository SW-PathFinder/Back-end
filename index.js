// index.js
import { Server } from "socket.io";
import http from "http";
import Game from "./logic/Game.js";             // 필요 시 TS/JS 포팅

const server = http.createServer();
const io = new Server(server, { cors: { origin: "*" } });

const gameSessions = {};        // room → Game
const userSid = {};             // username → socket.id

io.on("connection", (socket) => {
  socket.on("join_game", ({ room, player }) => {
    socket.join(room);
    userSid[player] = socket.id;

    if (!gameSessions[room]) gameSessions[room] = new Game();
    gameSessions[room].addPlayer(player);

    io.to(room).emit("player_joined", {
      target: "all",
      type: "player_joined",
      data: { player },
    });
  });

  socket.on("game_action", ({ room, player, action }) => {
    const resList = gameSessions[room].action(player, action) || [];
    resList.forEach((r) =>
      r.target === "all"
        ? io.to(room).emit("game_update", r)
        : io.to(userSid[r.target]).emit("private_game_update", r)
    );
  });
});

server.listen(3000);
