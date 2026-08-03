# 00 - Overview & Architecture

## 1. What this project is

A web-based, local-hosted version of the Werewolf/Mafia party game ("Ma Sói"), playable with a mix of human players (same LAN, no login/auth) and AI-controlled players (LLM agents). Exactly one human is the Admin — creates the room, picks the scenario, decides which seats are human vs AI. No accounts, no persistence of identity across games beyond a single match's record.

Core loop: **Night** (role holders act secretly, wolves always resolve first) → **Day** (public discussion, ends early once players converge) → **Vote** (lynch one player) → repeat until a faction's win condition is met.

Design inspiration for UI/UX conventions (layout, card-based role display, WebSocket-driven live updates) is drawn from [davidchilin/werewolves_game](https://github.com/davidchilin/werewolves_game) — direct asset scraping wasn't accessible (robots-blocked), so treat it as a reference to browse manually for specific art/sound assets, not a dependency.

Detailed content lives in separate files:
- `01-characters.md` — full role list
- `02-scenarios.md` — full scenario list
- `03-agent-system.md` — AI agent behavior, prompts, error handling, turn timing
- `04-logging-storage-ui.md` — persistence, logging, terminal output, UI spec

## 2. Tech stack

- Backend: FastAPI (Python), single process, WebSocket for realtime.
- Frontend: Jinja2 templates + TailwindCSS (CDN) + vanilla JS. No build step.
- Storage: SQLite (game records, logs, credentials).
- AI providers: Google Gemini API (primary), local Ollama (`phi3:mini` or similar), OpenAI-compatible providers (future, same interface).

## 3. Folder structure

```
werewolf/
├── backend/
│   ├── .env                      # non-secret runtime config only (see 4.2)
│   ├── .env.example
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py            # Settings — loads .env
│   │   └── credential_store.py     # CredentialStore — DB-backed key management (see 4.2)
│   ├── main.py                      # FastAPI entrypoint, mounts routes/static/templates
│   ├── db/
│   │   ├── database.py              # SQLite engine/session
│   │   └── models.py                 # ORM models (game, round, speech, action, api_key)
│   ├── enums.py
│   ├── seat.py
│   ├── player.py
│   ├── game.py
│   ├── resolver.py
│   ├── scenarios.py
│   ├── room_manager.py
│   ├── roles/
│   │   ├── base.py
│   │   ├── villagers.py
│   │   ├── wolves.py
│   │   └── neutral.py
│   ├── agents/
│   │   ├── agent.py
│   │   ├── turn_scheduler.py
│   │   ├── prompts.py
│   │   ├── night_order.py             # explicit wolves-first ordering (see 03)
│   │   ├── consensus.py                # early-stop detection for day discussion
│   │   ├── retry_policy.py              # retry/skip/switch-key logic on failure
│   │   ├── console_logger.py             # terminal-facing structured logs
│   │   └── providers/
│   │       ├── base_provider.py
│   │       ├── gemini_provider.py
│   │       ├── ollama_provider.py       # local model, http://localhost:11434
│   │       └── openai_provider.py       # scaffold, disabled by default
│   └── logs/
│
└── frontend/
    ├── config/
    │   └── theme.js                    # color palette + background url, single source of truth
    ├── templates/
    │   ├── lobby.html
    │   ├── game.html
    │   └── admin_debug.html              # night-chat visibility for Admin only (see 04)
    └── static/
        ├── js/
        │   ├── ws-client.js
        │   ├── seat-circle.js
        │   ├── chat-panel.js
        │   └── lobby.js
        └── css/
            └── custom.css
```

## 4. Key architectural decisions from this round of requirements

### 4.1 Wolves always act first at night

`night_order.py` hard-codes wolf-faction actions (all `Werewolf`/`AlphaWolf`/`WolfCub`/etc.) as the first block resolved every night, before any other role's `ActionPriority`. This is enforced at the scheduler level, not just by numeric priority value, so it can't accidentally be reordered by adding a new role with a lower priority number.

### 4.2 API keys are no longer stored only in `.env`

Plain `.env` lists were flagged as painful to edit/rotate. New approach: a `CredentialStore` backed by a SQLite table (`api_keys`), managed through a small Admin-only page (`/admin/keys`) — add, disable, or delete a key without restarting the server. `.env` still holds non-secret defaults (default model per provider, timeouts, feature flags) but never the actual key list. See `04-logging-storage-ui.md` §2 for the table schema.

### 4.3 Local model support (Ollama)

A new provider, `ollama_provider.py`, wraps calls to a local Ollama instance (default `http://localhost:11434/api/chat`, model configurable, default `phi3:mini`). It implements the same `BaseProvider.generate(prompt) -> str` interface as `gemini_provider.py`, so `Agent` code doesn't need to know whether it's talking to a cloud or local model. Timeout defaults to 120s (matches typical local inference latency), with the two failure modes handled explicitly: `requests.exceptions.Timeout` and `requests.exceptions.ConnectionError` (Ollama not running) — both map to a provider-level `ProviderUnavailable` exception so `retry_policy.py` can react the same way it does for a cloud 429/quota error (see `03-agent-system.md` §4).

### 4.4 UI theme

Single shared color palette (hex, warm-to-cool dusk gradient) applied across all templates via `frontend/config/theme.js` as CSS custom properties — no per-page hardcoded colors:

```
--color-1: #11516f;
--color-2: #267e96;
--color-3: #369daf;
--color-4: #64b5bf;
--color-5: #a6bbbb;
--color-6: #e68d81;
--color-7: #f2b8a0;
--color-8: #f5cb9c;
--color-9: #fbd384;
--color-10: #f3d8bb;
```

One single background image (a fixed URL, not per-page) applied at the `<body>` level across lobby and game screens for visual continuity. URL is a config value, not hardcoded inline, so it's swappable later.

Full layout spec is in `04-logging-storage-ui.md` §4.