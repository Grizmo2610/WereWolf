# 04 - Storage, Logging & UI

## 1. Public vs private content split

| Content | Public chat (all players see) | Admin debug page | Console / log file |
|---|---|---|---|
| `speak()` output | ✅ | ✅ | ✅ |
| `think()` reasoning/intent | ❌ | ✅ (tagged `NIGHT_CHAT_THINK` / `DAY_THINK`) | ✅ |
| Night-action target + reason | ❌ (only the final public outcome, e.g. who died) | ✅ (tagged `NIGHT_CHAT_SPEAK` for wolf pack coordination specifically, `NIGHT_ACTION` for others) | ✅ |
| Vote target + reason | Final tally only | ✅ | ✅ |
| Phase boundaries | ✅ (as highlighted system events, see §4) | ✅ | ✅ (`=== ĐÊM 1 ===`, `=== NGÀY 1 - BỎ PHIẾU ===`, etc.) |

The wolf pack's private night coordination — previously fully hidden to avoid leaking game mechanics into the public chat — is now fully visible under the `NIGHT_CHAT_THINK`/`NIGHT_CHAT_SPEAK` tags, but **only** on the Admin-only debug page (`frontend/templates/admin_debug.html`) and in the console/log file. Regular players (human seats) still never see it; this is strictly a "watch what the AIs are actually doing" tool for the Admin.

## 2. SQLite schema (`backend/db/models.py`)

- **`GameRecord`** — `room_code`, `scenario_id`, `total_players`, `started_at`, `ended_at`, `winner_faction`
- **`PlayerRecord`** — `game_id`, `player_id`, `seat_id`, `role_id`, `is_ai`, `provider_name`, `personality`, `alive_until_round`
- **`RoundLog`** — `game_id`, `round_number`, `phase`, `summary_public`
- **`SpeechLog`** — `game_id`, `round_id`, `player_id`, `think_reasoning`, `think_intent`, `will_speak`, `spoken_text`, `is_night_chat` (bool — distinguishes wolf-pack night talk from day discussion), `timestamp`
- **`ActionLog`** — `game_id`, `round_id`, `player_id`, `action_type`, `target_id`, `reason`, `was_forced_random` (bool, set by the retry-fallback path), `timestamp`
- **`ApiKeyRecord`** *(new — replaces the plain `.env` key list)*: `id`, `provider_name`, `key_value`, `alias`, `is_active`, `is_exhausted`, `last_used_at`, `added_at`. Managed through `CredentialStore` (`backend/config/credential_store.py`), which exposes `get_available(provider)`, `mark_exhausted(id)`, `add(provider, key, alias)`, `deactivate(id)` — all callable from the `/admin/keys` page without a server restart.

## 3. Log file + console output

Same structured log line format written to both `backend/logs/YYYY-MM-DD.log` **and** `stdout`, so the Admin can watch a live game in the terminal without opening the DB:

```
=== ĐÊM 1 ===
[21:03:11] [ROOM abc123] [seat_2/gemini] NIGHT_CHAT_THINK role=werewolf "cắn seat_5 vì..."
[21:03:14] [ROOM abc123] [seat_2/gemini] NIGHT_CHAT_SPEAK "seat_5 đi, ít nói quá"
[21:03:44] [ROOM abc123] [seat_7/gemini] NIGHT_ACTION role=guard target=seat_5
[21:04:02] EVENT player_dead seat=5 cause=wolf_bite
=== NGÀY 1 - THẢO LUẬN ===
[21:05:00] [ROOM abc123] [seat_1/ollama] THINK will_speak=True intent="nghi seat_3"
[21:05:31] [ROOM abc123] [seat_1/ollama] SPEAK "seat_3 hôm qua nói hơi mâu thuẫn"
[21:06:10] EVENT discussion_consensus_reached target=seat_3
=== NGÀY 1 - BỎ PHIẾU ===
[21:06:40] EVENT player_lynched seat=3
```

Phase-boundary markers (`=== ĐÊM N ===`, `=== NGÀY N - THẢO LUẬN ===`, `=== NGÀY N - BỎ PHIẾU ===`) and `EVENT` lines (deaths, consensus reached, forced-random fallback, credential switch) are emitted by `console_logger.py`, called from `game.py`/`resolver.py` at each transition — not scattered ad hoc across the codebase.

## 4. Public chat event highlights

The in-game chat panel (human + AI visible) renders two kinds of entries, visually distinct:

- **Speech entries** — normal chat bubble, character name + avatar, `spoken_text` only.
- **System event entries** — highlighted/centered banner style (not a chat bubble), for: night started, night ended, a player died (and how, if that cause is publicly known — e.g. lynch is always public, wolf-bite cause may or may not be per scenario rules), a vote result, game start/end. These use the palette's accent colors (see §5) rather than the neutral chat background, so they visually separate "narration" from "player talk."

## 4b. Game-start info block (posted to public chat/log at Day 1)

Right after roles are dealt, before Night 1 begins, the system posts one fixed-format public block (both to the chat panel as a highlighted system entry and to the log at `INFO` level) so every player — human or AI — starts from the same shared facts:

```
- **Alive Players:** {count}
- **Role Counts:** {Villager: n, Werewolf: n, Doctor: n, Seer: n, ...}
- **Alive Team Member:** {Villagers: n, Werewolves: n, Neutral: n}
- **Day Discussion:** Round-robin. Players speak in round-robin order for
  {rounds_per_day} round(s). The starting speaker rotates to the next
  player for each subsequent day, but stays fixed across all rounds
  within that day.
- **Day Exile Vote:** Sequential voting. Players vote one by one. The
  player with the most votes after everyone has voted is eliminated.
  The starting voter rotates to the next player for each subsequent
  voting phase. Ties result in no elimination.
- **Night Werewolf Vote:** Sequential voting. Same mechanics as the day
  exile vote, scoped to the werewolf pack.
- Role function list: one line per role in play, format
  "Role name {role} - team {faction} - {one-line ability description}."
```

Example role-function lines (style reference, generated dynamically from the actual `Scenario`, not hardcoded):

```
* Role name Werewolf - team Werewolves - Each night, collaborates with
  fellow werewolves to vote on eliminating one player.
* Role name Villager - team Villagers - No special abilities.
  Participates in the daily vote to eliminate a suspected werewolf.
* Role name Doctor - team Villagers - Each night, may protect one player
  from a werewolf attack. Doctor is NOT allowed to save themselves during
  night time. Doctor is NOT allowed to save the same player on
  consecutive nights.
* Role name Seer - team Villagers - Each night, may inspect one player
  to learn their true role.
```

`Doctor` above is this block's display label for `Guard`/`Bảo Vệ`; use whatever the role's actual configured display name is, but keep documenting real hard constraints (can't self-save, can't repeat target, etc.) in the description line.

## 5. UI — color palette & background

Single palette, applied globally via CSS custom properties (`frontend/config/theme.js` generates these into a `<style>` block included on every template — no per-page hardcoded hex values):

```css
--color-1: #11516f;  /* deep teal - headers, borders */
--color-2: #267e96;  /* mid teal - primary buttons */
--color-3: #369daf;  /* teal accent - links, active state */
--color-4: #64b5bf;  /* light teal - secondary elements */
--color-5: #a6bbbb;  /* muted gray-teal - dividers, disabled state */
--color-6: #e68d81;  /* coral - danger/death events */
--color-7: #f2b8a0;  /* peach - warning/vote events */
--color-8: #f5cb9c;  /* light peach - highlight banners */
--color-9: #fbd384;  /* gold - night-phase accent */
--color-10: #f3d8bb; /* cream - card backgrounds, chat bubbles */
```

Suggested mapping (not mandatory, adjustable in `theme.js`): dead/eliminated players desaturate toward `--color-5`; death/lynch system events use `--color-6`/`--color-7`; night-phase UI leans on `--color-1`/`--color-9` for a dusk feel; chat bubbles sit on `--color-10`.

**Background:** one single image, applied at `<body>` level via `background-image: url(var(--bg-url))`, `background-attachment: fixed`, `background-size: cover`, consistent across lobby and game screens. The URL itself is a single config value in `theme.js`, not duplicated per template. **Fallback:** if the configured image URL/path fails to load (checked client-side via the `<img>` `onerror`/`Image()` preload trick, or server-side path-exists check before rendering), fall back to a CSS `linear-gradient` built from the same palette (`--color-1` → `--color-9`, dusk-style diagonal gradient) instead of leaving a blank body.

**Font:** Times New Roman across the entire UI (`font-family: "Times New Roman", Times, serif;` set once on `body` in `theme.js`'s generated stylesheet, not per-component).

## 5b. Chat panel & system log are merged

There is **one** panel, not two — the earlier "chat panel" + "separate system log" split is dropped for the player-facing screen. Public system events (phase boundaries, deaths, vote tallies) and public speech both render in the same scrolling feed, distinguished only by the bubble-vs-banner styling from §4. Specifically:

- **Day speech** (`spoken_text` from day-phase `speak()` calls) appears as normal chat bubbles in this shared feed.
- **Live vote count** — while a Day Exile Vote or Night Werewolf Vote is in progress, the feed shows a running counter entry (e.g. "Đã bỏ phiếu: 4/8") that updates in place (not a new line per vote) as each sequential voter casts theirs, then converts into the final tally banner once voting closes.
- **Night wolf-pack discussion is intentionally reduced**, not hidden entirely from this merged public feed the way `NIGHT_CHAT_THINK`/`SPEAK` is (those stay Admin-only per §1) — rather, the *number of night discussion turns itself* is capped lower than day discussion (e.g. wolves get a short, fixed exchange before their sequential vote, not open-ended back-and-forth) to keep pacing tight. Still subject to the same 30s minimum-turn floor.
- The Admin debug page (`admin_debug.html`) remains the only place `NIGHT_CHAT_THINK`/`NIGHT_CHAT_SPEAK` are visible, per §1 — that split is unchanged.

## 5c. Log levels

Every log line (console + file, per §3) is tagged with a standard level, not just a bare message:

```
[21:03:11] [INFO ] === ĐÊM 1 ===
[21:03:14] [DEBUG] [seat_2/gemini] NIGHT_CHAT_THINK role=werewolf "..."
[21:03:44] [INFO ] [seat_7/gemini] NIGHT_ACTION role=guard target=seat_5
[21:04:02] [WARN ] retry_forced_random player=seat_9 reason=malformed_output_twice
[21:04:10] [ERROR] credential_exhausted provider=gemini key_alias=k2, switching
```

Standard levels: `DEBUG` (think/reasoning content, raw provider payloads), `INFO` (phase boundaries, actions, events, speech), `WARN` (forced-random fallback, silent skip), `ERROR` (credential exhausted/switch, provider unreachable, malformed output after retry exhausted). Console defaults to `INFO` and above; the log file captures everything including `DEBUG` (this is also where the night-chat content backing the Admin debug page is sourced from).

## 6. Layout (grid, Tailwind, no build step)

```
┌─────────────────────────────┬───────────────────┐
│                               │                    │
│      Seat circle (SVG/CSS)    │    Chat panel       │
│      seat-circle.js            │  (chat bubbles +     │
│                                 │  highlighted event    │
│                                 │  banners, auto-scroll)│
│                                 │                        │
├─────────────────────────────┤    ─────────────────    │
│  Current phase indicator        │                        │
│  (Đêm 2 / Ngày 2 - Bỏ phiếu)      │                        │
└─────────────────────────────┴───────────────────┘
```

Dead players render at `opacity-40 grayscale` on the seat circle. All updates pushed via WebSocket (`ws-client.js`), no polling. The Admin debug page (`admin_debug.html`) is a separate route, not part of this shared layout — it's a plain scrollable log view, not styled for player-facing use.