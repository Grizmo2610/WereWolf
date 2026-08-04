import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env ở root project (một cấp trên backend/)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ENV_PATH = os.path.join(_ROOT, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_PATH, env_file_encoding="utf-8", extra="ignore")

    gemini_api_keys: str = ""
    openai_api_keys: str = ""
    gemini_model: str = "gemini-2.0-flash"
    openai_model: str = "inclusionai/ling-3.0-flash:free"
    openai_base_url: str = "https://openrouter.ai/api/v1"
    ollama_model: str = "phi3:mini"
    ollama_enabled: bool = False

    qwen_vllm_base_url: str = "https://chatbot-vllm-qwen36-35b-a3b.seabank.com.vn/Qwen3.6-35B-A3B/v1"
    qwen_vllm_model: str = "Qwen3.6-35B-A3B"
    qwen_vllm_api_key: str = ""
    qwen_vllm_enabled: bool = False
    qwen_vllm_timeout_seconds: int = 120

    gemini_delay_seconds: int = 2
    openai_delay_seconds: int = 2
    ollama_delay_seconds: int = 1
    qwen_vllm_delay_seconds: int = 2

    max_turns_per_day: int = 40
    discussion_timeout_seconds: int = 300
    db_path: str = "./backend/logs/game.db"
    log_dir: str = "./backend/logs"

    min_turn_seconds: int = 30
    api_retry_count: int = 2

    @property
    def gemini_keys_list(self) -> list[str]:
        return [k for k in self.gemini_api_keys.split(",") if k]

    @property
    def openai_keys_list(self) -> list[str]:
        return [k for k in self.openai_api_keys.split(",") if k]

    @property
    def ollama_keys_list(self) -> list[str]:
        return ["local"] if self.ollama_enabled else []

    @property
    def qwen_vllm_keys_list(self) -> list[str]:
        if not self.qwen_vllm_enabled:
            return []
        return [self.qwen_vllm_api_key] if self.qwen_vllm_api_key else ["local"]

    @property
    def turn_delay_seconds(self) -> dict[str, int]:
        return {
            "gemini": self.gemini_delay_seconds,
            "openai": self.openai_delay_seconds,
            "ollama": self.ollama_delay_seconds,
            "qwen_vllm": self.qwen_vllm_delay_seconds,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()