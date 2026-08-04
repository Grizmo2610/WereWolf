import json
import logging
import random
import time
from dataclasses import dataclass, field

from agents.key_pool import KeyPool
from agents.prompts import (
    PERSONALITY_TRAITS,
    night_action_prompt,
    speak_prompt,
    system_prompt,
    think_prompt,
    vote_think_prompt,
)
from config.settings import get_settings

logger = logging.getLogger("werewolf")

PUBLIC_MEMORY_TAIL_SIZE = 30


@dataclass
class ThinkResult:
    will_speak: bool
    reasoning: str
    intent: str


@dataclass
class ActionDecision:
    target_id: str | None
    reason: str


class Agent:
    def __init__(self, player_id: str, key_pool: KeyPool, character_name: str,
                 role_id: str, personality: str | None = None):
        self.player_id = player_id
        self.key_pool = key_pool
        self.character_name = character_name
        self.role_id = role_id
        self.personality = personality or random.choice(PERSONALITY_TRAITS)
        self.public_memory: list[str] = []
        self.private_context: str = ""
        self.spoken_today: bool = False
        self.total_words_today: int = 0

    def _client(self):
        return self.key_pool.get_client(self.player_id)

    def _call(self, user_prompt: str) -> str:
        settings = get_settings()
        retries = settings.api_retry_count
        last_exc: Exception | None = None

        for attempt in range(retries + 1):
            try:
                client = self._client()
                full_prompt = (
                    system_prompt(self.character_name, self.role_id, self.personality)
                    + "\n\n" + user_prompt
                )
                return client.generate(full_prompt)
            except Exception as exc:
                last_exc = exc
                client_for_check = self._client()
                if client_for_check.is_out_of_credit_error(exc):
                    rotated = self.key_pool.mark_key_exhausted(self.player_id)
                    if rotated:
                        logger.info("Agent %s: đã chuyển key, thử lại lần %d", self.player_id, attempt + 1)
                        continue
                    # Không còn key nào
                    raise RuntimeError("Hết tất cả API key/credit.") from exc
                if attempt < retries:
                    logger.warning(
                        "Agent %s: lỗi API lần %d/%d: %s — thử lại",
                        self.player_id, attempt + 1, retries + 1, exc
                    )
                    time.sleep(1)
                else:
                    raise

        raise last_exc  # type: ignore[misc]

    @staticmethod
    def _parse_json(raw: str) -> dict:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())

    @staticmethod
    def _roster_text(game) -> str:
        lines = [f"Ghế {p.seat_id}: {p.display_name}" for p in game.alive_players()]
        return "\n".join(lines) if lines else "(không còn ai sống)"

    def _resolve_seat_target(self, game, data: dict) -> str | None:
        seat = data.get("target_seat")
        if seat is None:
            return None
        try:
            seat = int(seat)
        except (TypeError, ValueError):
            return None
        target = game.get_by_seat(seat)
        if target and target.alive:
            return target.player_id
        return None

    @staticmethod
    def _death_summary(game) -> str:
        """Trả về chuỗi tóm tắt ai đã chết và lý do (thông tin công khai).
        Dùng để inject vào prompt, tránh model phải đoán mò hay hallucinate.
        """
        CAUSE_LABEL = {
            "wolf_bite": "bị sói cắn chết đêm",
            "voted_out": "bị làng treo cổ ngày",
            "hunter_shot": "bị Thợ Săn bắn",
            "witch_poison": "bị đầu độc đêm",
            "lover_death": "chết vì người yêu bị giết",
            "terrorist_explosion": "chết vì Khủng Bố",
        }
        dead = [p for p in game.players if not p.alive]
        if not dead:
            return ""
        lines = []
        for p in dead:
            cause = getattr(p, "death_cause", None) or "unknown"
            round_died = getattr(p, "died_round", None)
            label = CAUSE_LABEL.get(cause, cause)
            round_str = f" (vòng {round_died})" if round_died else ""
            lines.append(f"- {p.display_name} (ghế {p.seat_id}): {label}{round_str}")
        return "\n".join(lines)

    def _random_vote_target(self, game) -> str | None:
        alive = [p for p in game.alive_players() if p.player_id != self.player_id]
        if not alive:
            alive = game.alive_players()
        if not alive:
            return None
        return random.choice(alive).player_id

    def _random_night_target(self, game) -> str | None:
        alive = [p for p in game.alive_players() if p.player_id != self.player_id]
        if not alive:
            return None
        return random.choice(alive).player_id

    def think(self, game) -> ThinkResult:
        tail = "\n".join(self.public_memory[-PUBLIC_MEMORY_TAIL_SIZE:])
        round_number = getattr(game, "round_number", 0)
        death_summary = self._death_summary(game)
        settings = get_settings()
        retries = settings.api_retry_count

        for attempt in range(retries + 1):
            try:
                raw = self._call(think_prompt(self.private_context, tail, round_number, death_summary))
                data = self._parse_json(raw)
                return ThinkResult(
                    will_speak=bool(data.get("will_speak", False)),
                    reasoning=str(data.get("reasoning", "")),
                    intent=str(data.get("intent", "")),
                )
            except json.JSONDecodeError:
                logger.warning("Agent %s think: parse JSON thất bại lần %d", self.player_id, attempt + 1)
                if attempt >= retries:
                    return ThinkResult(will_speak=False, reasoning="parse_error", intent="")
            except Exception as exc:
                logger.error("Agent %s think: lỗi %s", self.player_id, exc)
                return ThinkResult(will_speak=False, reasoning="api_error", intent="")

        return ThinkResult(will_speak=False, reasoning="parse_error", intent="")

    def speak(self, think_result: ThinkResult) -> str:
        settings = get_settings()
        retries = settings.api_retry_count
        for attempt in range(retries + 1):
            try:
                raw = self._call(speak_prompt(think_result.intent, self.personality))
                return raw.strip()
            except Exception as exc:
                logger.warning("Agent %s speak: lỗi lần %d: %s", self.player_id, attempt + 1, exc)
                if attempt >= retries:
                    return ""
        return ""

    def decide_night_action(self, game) -> ActionDecision:
        tail = "\n".join(self.public_memory[-PUBLIC_MEMORY_TAIL_SIZE:])
        roster = self._roster_text(game)
        round_number = getattr(game, "round_number", 0)
        settings = get_settings()
        retries = settings.api_retry_count

        for attempt in range(retries + 1):
            try:
                raw = self._call(night_action_prompt(self.role_id, self.private_context, tail, roster, round_number))
                data = self._parse_json(raw)
                target_id = self._resolve_seat_target(game, data)
                return ActionDecision(target_id=target_id, reason=str(data.get("reason", "")))
            except json.JSONDecodeError:
                logger.warning("Agent %s night_action: parse JSON thất bại lần %d", self.player_id, attempt + 1)
                if attempt >= retries:
                    return ActionDecision(target_id=self._random_night_target(game), reason="parse_error_random")
            except Exception as exc:
                logger.error("Agent %s night_action: lỗi %s", self.player_id, exc)
                return ActionDecision(target_id=self._random_night_target(game), reason="api_error_random")

        return ActionDecision(target_id=self._random_night_target(game), reason="parse_error_random")

    def decide_vote(self, game) -> ActionDecision:
        tail = "\n".join(self.public_memory[-PUBLIC_MEMORY_TAIL_SIZE:])
        roster = self._roster_text(game)
        round_number = getattr(game, "round_number", 0)
        death_summary = self._death_summary(game)
        settings = get_settings()
        retries = settings.api_retry_count

        for attempt in range(retries + 1):
            try:
                raw = self._call(vote_think_prompt(self.private_context, tail, roster, round_number, death_summary))
                data = self._parse_json(raw)
                target_id = self._resolve_seat_target(game, data)
                return ActionDecision(target_id=target_id, reason=str(data.get("reason", "")))
            except json.JSONDecodeError:
                logger.warning("Agent %s vote: parse JSON thất bại lần %d", self.player_id, attempt + 1)
                if attempt >= retries:
                    return ActionDecision(target_id=self._random_vote_target(game), reason="parse_error_random")
            except Exception as exc:
                logger.error("Agent %s vote: lỗi %s", self.player_id, exc)
                return ActionDecision(target_id=self._random_vote_target(game), reason="api_error_random")

        return ActionDecision(target_id=self._random_vote_target(game), reason="parse_error_random")

    def observe_public_line(self, line: str) -> None:
        self.public_memory.append(line)