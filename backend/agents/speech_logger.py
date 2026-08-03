import datetime
import logging
import os

from config.settings import get_settings
from db.models import ActionLog, SpeechLog

settings = get_settings()
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_dir = settings.log_dir
if not os.path.isabs(log_dir):
    log_dir = os.path.join(PROJECT_ROOT, log_dir)
os.makedirs(log_dir, exist_ok=True)

_logger = logging.getLogger("werewolf")
_logger.setLevel(logging.INFO)
if not _logger.handlers:
    fmt = logging.Formatter("%(message)s")
    log_path = os.path.join(log_dir, f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}.log")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(fmt)
    _logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    _logger.addHandler(console_handler)


class SpeechLogger:
    def __init__(self, session, game_id: int, room_code: str):
        self.session = session
        self.game_id = game_id
        self.room_code = room_code

    def _ts(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log_think(self, player_id: str, player_name: str, provider_name: str, will_speak: bool,
                   reasoning: str, intent: str, channel: str = "day") -> None:
        tag = "THINK" if channel == "day" else "NIGHT_CHAT_THINK"
        _logger.info(
            f"[INFO][{self._ts()}] [ROOM {self.room_code}] [Player {player_name}/{provider_name}] "
            f'{tag} will_speak={will_speak} reasoning="{reasoning}" intent="{intent}"'
        )
        row = SpeechLog(
            game_id=self.game_id,
            player_id=player_id,
            think_reasoning=reasoning,
            think_intent=intent,
            will_speak=will_speak,
            spoken_text=None,
        )
        self.session.add(row)
        self.session.commit()

    def log_speak(self, player_id: str, player_name: str, provider_name: str, spoken_text: str,
                   channel: str = "day") -> None:
        tag = "SPEAK" if channel == "day" else "NIGHT_CHAT_SPEAK"
        _logger.info(
            f"[INFO][{self._ts()}] [ROOM {self.room_code}] [Player {player_name}/{provider_name}] "
            f'{tag} "{spoken_text}"'
        )
        row = SpeechLog(
            game_id=self.game_id,
            player_id=player_id,
            will_speak=True,
            spoken_text=spoken_text,
        )
        self.session.add(row)
        self.session.commit()

    def log_action(self, player_id: str, player_name: str, provider_name: str, action_type: str,
                     target_id: str | None, target_name: str | None, reason: str) -> None:
        role_hint = action_type.replace("_", " ")
        target_display = target_name or "không ai"
        _logger.info(
            f"[INFO][{self._ts()}] [ROOM {self.room_code}] [Player {player_name}/{provider_name}] "
            f'{role_hint.upper()} chọn "{target_display}" vì "{reason}"'
        )
        row = ActionLog(
            game_id=self.game_id,
            player_id=player_id,
            action_type=action_type,
            target_id=target_id,
            reason=reason,
        )
        self.session.add(row)
        self.session.commit()
