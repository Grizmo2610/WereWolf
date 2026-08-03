# AGENTS.md

Rules for any coding agent (Claude Code or otherwise) implementing this project. Read `00-overview-and-architecture.md` through `04-logging-storage-ui.md` first — this file is the compliance checklist distilled from them, not a replacement.

## 1. Language

- Code identifiers (classes, functions, variables, file names) — **English only**.
- Everything user-facing: prompts sent to LLMs, chat text, UI strings, log messages meant for a human to read — **Vietnamese**.
- Do not mix: a class named `NguoiChoi` or a UI string in English are both violations.

## 2. File & folder structure

- Follow the exact tree in `00-overview-and-architecture.md` §3. Don't invent new top-level folders. If a new module doesn't obviously fit an existing folder, ask before placing it — don't guess.
- `backend/` and `frontend/` each own their config independently (`backend/config/`, `frontend/config/`). Never put a frontend asset under `backend/` or vice versa.
- One class per concern, matching the design docs' class list. Don't merge `Agent` and `TurnScheduler` responsibilities into one file because it's "easier for now."

## 3. Comment & docstring policy

- No module-level docstrings, no "summary" comments at the top of a file.
- No section-banner comments (`# ==== SECTION ====`, `"""--- Roles ---"""`). Group related code by file/class instead of by comment block.
- Inline comments are fine when a line is genuinely non-obvious (e.g. a tie-break rule, a magic number's origin). Keep them to one short line.
- Do not restate what the code already says (`x += 1  # increment x` is not acceptable).

## 4. Core mechanical rules — these are non-negotiable, not suggestions

- **Wolves always act first at night**, structurally enforced (Tier 0 vs Tier 1), not just via priority numbers. See `03-agent-system.md` §3.
- **Every agent turn takes a minimum of 30 seconds** (think + optional speak, or think + action, or the silent vote-think), sleep for the remainder if the LLM call(s) finish faster. See `03-agent-system.md` §5.
- **Think happens before speak, as two separate LLM calls.** Never merge them into one call and parse out two sections — the spec requires genuinely separate requests, each prefixed with the correct "Đây là phần nghĩ / Đây là phần nói" framing.
- **Agents never receive another player's real role.** `private_context` is per-agent; only `public_memory` (what's actually been said) crosses between agents. If you find yourself passing `game.players` wholesale into a prompt, stop — that's a leak.
- **Day discussion is round-robin with a fixed round count**; **day exile vote and night werewolf vote are sequential voting with a rotating starting voter and no tie-break** (ties = no elimination). Do not implement any other voting shape (no simultaneous/parallel voting, no random tie resolution) unless a scenario's `custom_rules` explicitly overrides it. See `03-agent-system.md` §4b.
- **Night discussion turn count is capped lower than day discussion.** Don't default it to the same value.
- **Retry/skip/switch-credential logic follows the exact decision tree** in `03-agent-system.md` §4 — malformed output retries once then skips (think/speak) or random-falls-back (vote/action target); provider-level failures (quota, auth, timeout, connection error) switch credential before retrying. Don't collapse these into a single generic "retry 3 times then give up."

## 5. Providers

- Every provider (`gemini_provider.py`, `ollama_provider.py`, `openai_provider.py`) implements the exact same `BaseProvider.generate(prompt) -> str` interface. `Agent` code must never branch on provider type — if it needs to, the interface is wrong and needs fixing, not a workaround in `Agent`.
- API keys/credentials live in the `ApiKeyRecord` SQLite table via `CredentialStore`, never hardcoded, never re-introduced into `.env` as a plain list. `.env` only holds non-secret defaults.
- The Ollama provider must explicitly handle `requests.exceptions.Timeout` and `requests.exceptions.ConnectionError` and translate both into the same `ProviderUnavailable` exception the retry policy expects from cloud providers — don't let a raw `requests` exception escape to caller code.

## 6. Logging

- Every log line has a level (`DEBUG`/`INFO`/`WARN`/`ERROR`) per `04-logging-storage-ui.md` §5c. Don't use bare `print()` anywhere in `backend/` — route everything through `console_logger.py` so console and log-file output stay identical.
- Phase transitions and events (`=== ĐÊM N ===`, deaths, consensus reached, credential switch, forced-random fallback) are emitted from `console_logger.py` calls in `game.py`/`resolver.py`, not scattered inline throughout arbitrary modules.
- Night wolf-pack coordination (`NIGHT_CHAT_THINK`/`NIGHT_CHAT_SPEAK`) is logged at `DEBUG` and is visible only on `/admin/keys`-style Admin routes (`admin_debug.html`) — it must never be pushed to the public WebSocket channel that human players' browsers subscribe to. Treat this as a privacy boundary, not just a UI filter — don't rely on the frontend to hide it if the backend already broadcast it.

## 7. UI

- One shared stylesheet source (`frontend/config/theme.js`) generates the CSS custom properties (palette + font + background). No hardcoded hex colors or `font-family` declarations in individual templates.
- Chat and system log are **one merged panel** on the player-facing screen — don't build them as two separate components that happen to sit next to each other.
- Background image has a gradient fallback built from the same palette if the configured path/URL fails — don't ship a blank/broken background as the fallback state.
- Tailwind via CDN only. No npm build step, no bundler, for this project's scope — if a task seems to need one, flag it instead of adding tooling silently.

## 9. Definition of done — never "done" just because it compiles

- Writing code is not completion. Before marking any task/subtask done, actually **run it** — execute the script, hit the endpoint, run the relevant test — and check the output for errors.
- **Program/logic errors** (broken imports, wrong function signatures, wrong call arguments, type mismatches, unhandled exceptions in core flow, schema mismatches) **must be fixed and re-verified** before calling anything done. Don't leave a known-broken import "for later."
- **External/API errors** (provider quota hit, network timeout to Gemini/Ollama, a real external service being down) are acceptable to leave unresolved in a dev/test run **only if clearly logged as a warning** explaining what failed and why it's expected in this environment — never silently swallowed, never mistaken for a passing test.
- If a test can't be run because of missing credentials/local services (e.g. no Ollama running, no API key configured), say so explicitly rather than assuming it would have passed.
- Passing your own verification is a prerequisite, not the finish line. **A task is only "done" once the user has explicitly confirmed it** — report what was built and what was tested, then wait for their confirmation rather than marking it complete unilaterally. Don't say "hoàn thành"/"done" in a summary as if the matter is closed; state status and hand it back for review.

## 10. Environment & workspace boundaries

- Always work inside a **virtual environment** (`venv`), created if it doesn't exist yet. Every `pip install` happens inside that venv — never install into the system/global Python.
- Stay strictly inside the current project folder. **Never `cd` or read/write outside it**, regardless of what a task seems to imply.
- **Don't explore the full folder tree up front.** List only the top-level files/folders first, then decide — based on what's actually needed for the current task — which specific subfolders are worth opening. Don't recursively dump the entire tree as a first move.
- **Skip folders whose contents are already known by convention** — `__pycache__`, `.venv`/`venv`, `.git`, `node_modules`, and similar — don't list or open these; their presence is expected and their contents are never relevant to a review.

## 11. When the docs conflict or something is underspecified

- If two design files disagree (e.g. an older scheduler description vs a newer §4b refinement), the most recently dated/most specific section wins — but flag the conflict rather than silently picking one, since the docs may not have been fully reconciled yet.
- If a requirement is genuinely missing (no doc covers it), implement the smallest reasonable default consistent with everything else here, and note the assumption in the PR/commit description rather than blocking on it — but don't invent new mechanical rules (voting shape, turn timing, ordering) that contradict §4 above under any circumstances.