/* chat-panel.js — hiển thị chat + sự kiện trong 1 feed */

const EVENT_STYLES = {
  night_start:      { cls: "event-night",     icon: "🌙" },
  night_end:        { cls: "event-night-end",  icon: "🌅" },
  player_died:      { cls: "event-death",      icon: "💀" },
  player_executed:  { cls: "event-execute",    icon: "⚖️" },
  vote_start:       { cls: "event-vote",       icon: "🗳️" },
  vote_end:         { cls: "event-vote",       icon: "🗳️" },
  game_end:         { cls: "event-gameover",   icon: "🏆" },
};

function appendChatLine(text, playerName) {
  const panel = _panel();
  if (!panel) return;
  const div = document.createElement("div");
  div.className = "chat-line";
  const name = document.createElement("div");
  name.className = "name";
  name.textContent = playerName || "?";
  const body = document.createElement("div");
  body.className = "text";
  body.textContent = text;
  div.appendChild(name);
  div.appendChild(body);
  panel.appendChild(div);
  _scroll(panel);
}

function appendSystemLine(text, event) {
  const panel = _panel();
  if (!panel) return;
  const div = document.createElement("div");
  const style = event && EVENT_STYLES[event];
  if (style) {
    div.className = `event-line ${style.cls}`;
    const icon = document.createElement("span");
    icon.className = "event-icon";
    icon.textContent = style.icon;
    const body = document.createElement("span");
    body.className = "event-text";
    body.textContent = text.replace(/^[\p{Emoji_Presentation}\p{Extended_Pictographic}]\s*/u, "");
    div.appendChild(icon);
    div.appendChild(body);
  } else {
    div.className = "system-line";
    div.textContent = text;
  }
  panel.appendChild(div);
  _scroll(panel);
}

function updatePhaseBadge(phase, round) {
  const badge = document.getElementById("phase-badge");
  if (!badge) return;
  const labels = {
    lobby:          "Chờ bắt đầu",
    night:          `🌙 Đêm ${round}`,
    day_discussion: `☀️ Ngày ${round} · Thảo luận`,
    day_vote:       `⚖️ Ngày ${round} · Bỏ phiếu`,
    ended:          "🏆 Kết thúc",
  };
  const label = labels[phase] || phase;
  badge.textContent = label;

  // style badge by phase
  badge.className = "phase-badge";
  if (phase === "night") badge.classList.add("phase-badge--night", "phase-night");
  else if (phase === "day_discussion" || phase === "day_vote") badge.classList.add("phase-badge--day");
  else if (phase === "ended") badge.classList.add("phase-badge--ended");
}

function _panel() { return document.getElementById("chat-panel"); }
function _scroll(el) {
  requestAnimationFrame(() => { el.scrollTop = el.scrollHeight; });
}
