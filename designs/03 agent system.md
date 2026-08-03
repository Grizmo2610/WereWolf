# 03 - Agent System

## 1. Language rule

In-game text (prompts sent to the LLM, chat content, UI strings) is Vietnamese. Code identifiers (classes, variables, functions) are English. This file is written in English per this round's request, but every prompt template quoted below is the actual Vietnamese text sent to the model — don't translate it at implementation time.

## 2. `Agent` (`backend/agents/agent.py`)

One AI-controlled player. 1:1 with a `Player`.

**Attributes:** `player_id`, `provider_name`, `credential_id` (see `04-logging-storage-ui.md` §2 for the credential store), `model_name`, `personality`, `public_memory: list[str]`, `private_context: str`, `spoken_today: bool`.

**Methods:** `think(game)`, `speak(think_result)`, `decide_night_action(game)`, `decide_vote(game)` — same responsibilities as before, now wrapped by `retry_policy.py` (§4) and `turn_scheduler.py`'s minimum-duration enforcement (§5).

`private_context` never includes another player's real role. Agents only ever get what other players have actually said (`public_memory`) plus whatever their own role's ability legitimately reveals.

## 3. Night action ordering — wolves always first

`night_order.py` defines the night sequence as two tiers, not one flat priority list:

```
Tier 0 (always first): every Wolf-faction role that acts at night
                        (Werewolf, Alpha Wolf, Wolf Cub, Wolf Seer, Medium, ...)
Tier 1 (after Tier 0): everything else, ordered by ActionPriority as before
                        (Guard, Cupid, Seer-type info roles, Witch save,
                        Witch poison, Vampire, Gambler, Sorcerer, ...)
```

This is enforced structurally: the scheduler iterates Tier 0 to completion before even building Tier 1's queue. A future role added with a numerically low `ActionPriority` still can't jump ahead of the wolves.

## 4. Failure handling — retry, skip, or switch credential

Applies to every LLM call an `Agent` makes (think, speak, night action, vote). Handled by `retry_policy.py`, wrapping each provider call:

1. **Malformed output** (response doesn't match the expected JSON/command format): retry once — same model, same prompt, fresh call.
   - Still malformed after the retry:
     - If it was a **think** or **speak** call → skip entirely (both the reasoning and the utterance are dropped; treated as `SKIP_TURN`, logged as such).
     - If it was a **vote** or a **night-action target selection** → fall back to a **random valid target** so the game can still progress; log that this was a forced-random fallback.
2. **Provider-level failure** (quota/credit exhausted, auth error, rate limit, or — for the local provider — `ConnectionError`/`Timeout`): do **not** just retry the same credential. Instead:
   - Mark the current credential as temporarily unusable (`CredentialStore.mark_exhausted(...)`).
   - Re-assign the agent to the next available credential in the pool (same provider first, then fall through to another configured provider if none are left).
   - Retry the *same* call once on the new credential before falling back to the skip/random behavior in step 1.
3. All of this is logged (console + DB) so a human reviewing the match can tell "agent skipped because output was garbage twice" apart from "agent skipped because we ran out of keys entirely."

## 4b. Day discussion & voting mechanics (concrete rules)

Refines the earlier key-based guarantee/random scheduler: the actual turn order algorithm is simpler and rule-driven, matching what gets announced in the Day-1 info block (`04-logging-storage-ui.md` §4b).

**Day Discussion — round-robin, fixed round count:**
- Players speak in seat order for `rounds_per_day` rounds (configurable, default low — e.g. 2 — deliberately smaller than an unbounded loop to keep games moving).
- The starting speaker for round 1 of a given day rotates to the next player each subsequent day (day 1 starts at seat 0, day 2 starts at seat 1, etc.), but stays fixed across all rounds *within* that same day.
- `consensus.py`'s early-stop (see §8 below) can still end discussion before `rounds_per_day` completes if the transcript converges — this is a ceiling, not a guarantee every round happens.
- Each turn is still a full `think()` → maybe `speak()` pair, same as before, still subject to the API-key round-robin distribution described for the pool, and still bound by the 30s floor in §5.

**Day Exile Vote & Night Werewolf Vote — sequential voting, same shape for both:**
- Players vote one at a time, in order, starting from a rotating starting voter (rotates to the next player each time this vote type occurs — day exile voting order and night wolf-vote order rotate independently of each other).
- Whoever has the most votes once everyone eligible has voted is eliminated (day) or attacked (night, wolves only).
- **Ties result in no elimination** — no tie-break, no revote, the phase simply resolves to nobody being removed.
- Each voter still does a short silent `decide_vote()` think beforehand (per the original design), just sequenced strictly one-by-one rather than any parallel/random ordering.

## 5. Minimum turn duration — 30 seconds

Every agent turn (think + optional speak combined, or think + night-action, or the silent vote-think) must occupy **at least 30 seconds of wall-clock time** before the scheduler advances to the next agent. If the actual LLM round-trip(s) finish faster than 30s, the scheduler sleeps for the remainder before releasing the next turn. This applies uniformly — day discussion turns, night action turns, and vote turns all respect the same floor. Implemented as a wrapper in `turn_scheduler.py`: record `turn_start`, run the agent's calls, then `sleep(max(0, 30 - elapsed))`.

## 6. Day-1 / early-game context injection

Every prompt sent to an agent includes a context block built from actual game state, not just static rules text. On night 1 / day 1 specifically, this block explicitly states there is nothing to react to yet, instead of leaving the model to guess or hallucinate prior events:

```
Đây là đêm đầu tiên / ngày đầu tiên. Chưa có ai nói gì, chưa có ai chết,
chưa có sự kiện gì xảy ra. Đừng nhắc tới chuyện gì đã xảy ra trước đó vì
chưa có.
```

From night/day 2 onward, the block is instead populated with the real `public_memory` transcript and the real list of who has died and how (only what's public — see `04-logging-storage-ui.md` §1 for the public/private split).

## 7. "Reading", not "seeing"

The base system prompt is explicit that the agent has no visual channel — it only receives text transcripts, never images, cards, or board state as pictures. Added as a fixed clause in the base prompt (`prompts.py`):

```
Bạn không "nhìn thấy" bàn chơi hay lá bài của ai — bạn chỉ ĐỌC được nội
dung chữ mà người khác đã nói ra hoặc thông tin văn bản do luật vai trò
của bạn cung cấp. Đừng mô tả như thể bạn đang nhìn thấy gì.
```

This exists to prevent the model from generating "I see that..." framing that doesn't match its actual input modality.

## 8. Early stop on discussion consensus

`consensus.py` watches the running day-discussion transcript for convergence and can end the discussion phase early, before every scheduled turn is used up. Trigger condition: once two or more consecutive (or a majority of already-spoken) agents have stated the **same vote target** in their `speak()` output — e.g. "Tôi vote 3" followed by "Tôi cũng vote 3" — the discussion phase is marked resolved and the scheduler moves straight to the vote phase; remaining unspoken agents are not forced to speak (they still get a chance to think/vote silently, just not a forced public turn). This only short-circuits **discussion** — it never skips the actual `think()`/`speak()`/`decide_night_action()`/`decide_vote()` calls themselves, since those are still required per player, per the original design (每 lượt vẫn phải think, chỉ discussion phase kết thúc sớm).

## 9. Console (terminal) visibility

Everything logged to the DB/log-file (per `04-logging-storage-ui.md`) is **also** printed to the running server's terminal/stdout in real time — this isn't just a file-based audit trail, it's meant to be watchable live while the game runs locally. This includes phase boundary markers and full night-chat contents (see `04-logging-storage-ui.md` §1 and §3), not just the public chat.