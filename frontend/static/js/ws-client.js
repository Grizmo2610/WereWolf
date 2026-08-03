/* ws-client.js — WebSocket connection & dispatcher */
(function () {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  let socket;
  let reconnectDelay = 2000;

  function connect() {
    socket = new WebSocket(`${protocol}://${location.host}/ws/${window.ROOM_CODE}`);

    socket.onopen = () => {
      reconnectDelay = 2000;
      appendSystemLine("Đã kết nối tới máy chủ.");
    };

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "state") {
          updatePhaseBadge(msg.phase, msg.round);
          renderSeatCircle(msg.players);
        } else if (msg.type === "chat") {
          appendChatLine(msg.text, msg.player_name);
        } else if (msg.type === "system") {
          appendSystemLine(msg.text, msg.event);
        }
      } catch (e) {
        console.error("WS parse error", e);
      }
    };

    socket.onclose = () => {
      appendSystemLine("Mất kết nối — thử kết nối lại sau " + (reconnectDelay / 1000) + "s…");
      setTimeout(connect, reconnectDelay);
      reconnectDelay = Math.min(reconnectDelay * 1.5, 15000);
    };

    socket.onerror = () => {
      socket.close();
    };
  }

  connect();
})();
