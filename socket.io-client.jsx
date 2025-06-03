import { useEffect, useState, useRef } from "react";
import { io } from "socket.io-client";

export default function GameSocket({ room, username }) {
  const [log, setLog] = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    const s = io("http://localhost:8000", { query: { user: username } });
    socketRef.current = s;

    s.emit("join_game", { room, player: username });

    s.on("game_update", (msg) => setLog((l) => [...l, msg]));
    s.on("private_game_update", (msg) => setLog((l) => [...l, msg]));
    s.on("chat", (msg) => setLog((l) => [...l, msg]));

    return () => s.disconnect();
  }, [room, username]);

  const playCard = () =>
    socketRef.current.emit("game_action", {
      room,
      player: username,
      action: { type: "path", data: { handNum: 0, x: 8, y: 12 } },
    });

  return (
    <>
      <button onClick={playCard}>카드 내려보기</button>
      <pre>{JSON.stringify(log, null, 2)}</pre>
    </>
  );
}
