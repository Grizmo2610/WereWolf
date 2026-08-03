/* seat-circle.js — vòng tròn ghế ngồi SVG */

function renderSeatCircle(players) {
  const svg = document.getElementById("seat-circle");
  if (!svg) return;
  svg.innerHTML = "";

  const W = 400, H = 400;
  const cx = W / 2, cy = H / 2;
  const tableR = 44;
  const seatR  = 26;
  const orbitR = 148;
  const n = players.length || 1;

  // Ambient glow filter
  const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
  defs.innerHTML = `
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <radialGradient id="tableFill" cx="50%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#1a3a50"/>
      <stop offset="100%" stop-color="#081218"/>
    </radialGradient>
    <radialGradient id="seatAlive" cx="50%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#1a3a50"/>
      <stop offset="100%" stop-color="#0c1c26"/>
    </radialGradient>
  `;
  svg.appendChild(defs);

  // Outer ambient ring
  const outerRing = _el("circle");
  _attrs(outerRing, { cx, cy, r: orbitR + seatR + 10,
    fill: "none", stroke: "rgba(17,81,111,0.18)", "stroke-width": "1" });
  svg.appendChild(outerRing);

  // Centre table
  const tableShadow = _el("circle");
  _attrs(tableShadow, { cx, cy: cy + 2, r: tableR + 4,
    fill: "rgba(0,0,0,0.4)" });
  svg.appendChild(tableShadow);

  const table = _el("circle");
  _attrs(table, { cx, cy, r: tableR, fill: "url(#tableFill)",
    stroke: "#11516f", "stroke-width": "1.5" });
  svg.appendChild(table);

  const tableText = _el("text");
  _attrs(tableText, { x: cx, y: cy - 4, "text-anchor": "middle",
    "font-size": "9", fill: "#267e96", "letter-spacing": "3",
    "font-family": "Times New Roman, serif" });
  tableText.textContent = "BÀN TRÒN";
  svg.appendChild(tableText);

  const tableSubText = _el("text");
  _attrs(tableSubText, { x: cx, y: cy + 9, "text-anchor": "middle",
    "font-size": "8", fill: "#11516f", "letter-spacing": "1.5",
    "font-family": "Times New Roman, serif" });
  tableSubText.textContent = "MA SÓI";
  svg.appendChild(tableSubText);

  // Seat nodes
  players.forEach((p, i) => {
    const angle = (i / n) * 2 * Math.PI - Math.PI / 2;
    const x = cx + orbitR * Math.cos(angle);
    const y = cy + orbitR * Math.sin(angle);

    // Connector line from table to seat
    const line = _el("line");
    const innerX = cx + (tableR + 4) * Math.cos(angle);
    const innerY = cy + (tableR + 4) * Math.sin(angle);
    const outerX = cx + (orbitR - seatR - 2) * Math.cos(angle);
    const outerY = cy + (orbitR - seatR - 2) * Math.sin(angle);
    _attrs(line, { x1: innerX, y1: innerY, x2: outerX, y2: outerY,
      stroke: "rgba(17,81,111,0.35)", "stroke-width": "1" });
    svg.appendChild(line);

    const g = _el("g");
    g.setAttribute("class", "seat-group" + (p.alive ? "" : " seat-dead"));
    g.setAttribute("data-seat", p.seat_id);

    // Shadow
    const shadow = _el("circle");
    _attrs(shadow, { cx: x, cy: y + 2, r: seatR + 2, fill: "rgba(0,0,0,0.35)" });
    g.appendChild(shadow);

    // Seat circle
    const circle = _el("circle");
    _attrs(circle, {
      cx: x, cy: y, r: seatR,
      fill: p.alive ? "url(#seatAlive)" : "#0a1520",
      stroke: p.alive ? "#369daf" : "#e68d81",
      "stroke-width": "2",
      filter: p.alive ? "url(#glow)" : "none",
    });
    g.appendChild(circle);

    // Seat number
    const seatNum = _el("text");
    _attrs(seatNum, { x, y: y + 4, "text-anchor": "middle",
      "font-size": "14", fill: p.alive ? "#f3d8bb" : "#e68d81",
      "font-weight": "700", "font-family": "Times New Roman, serif" });
    seatNum.textContent = "S" + (p.seat_id + 1);
    g.appendChild(seatNum);

    // Name label (below seat)
    const labelY = y + seatR + 13;
    const label = _el("text");
    _attrs(label, { x, y: labelY, "text-anchor": "middle",
      "font-size": "9.5", fill: "#64b5bf",
      "font-family": "Times New Roman, serif",
      "letter-spacing": "0.3" });
    label.textContent = _truncate(p.display_name, 12);
    g.appendChild(label);

    // Dead cross marker
    if (!p.alive) {
      const cross1 = _el("line");
      _attrs(cross1, { x1: x - 8, y1: y - 8, x2: x + 8, y2: y + 8,
        stroke: "#e68d81", "stroke-width": "1.5", opacity: "0.7" });
      g.appendChild(cross1);
      const cross2 = _el("line");
      _attrs(cross2, { x1: x + 8, y1: y - 8, x2: x - 8, y2: y + 8,
        stroke: "#e68d81", "stroke-width": "1.5", opacity: "0.7" });
      g.appendChild(cross2);
    }

    svg.appendChild(g);
  });
}

// ── helpers ─────────────────────────────────────────────
function _el(tag) {
  return document.createElementNS("http://www.w3.org/2000/svg", tag);
}
function _attrs(el, attrs) {
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
}
function _truncate(str, max) {
  return str.length > max ? str.slice(0, max - 1) + "…" : str;
}
