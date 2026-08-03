import logging
from dataclasses import dataclass, field

from agents.providers.base_provider import BaseProvider
from agents.providers.gemini_provider import GeminiProvider
from agents.providers.ollama_provider import OllamaProvider
from agents.providers.openai_provider import OpenAIProvider
from agents.providers.qwen_vllm_provider import QwenVllmProvider
from config.providers import default_model_for

logger = logging.getLogger("werewolf")

PROVIDER_CLASSES = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
    "qwen_vllm": QwenVllmProvider,
}


@dataclass
class KeySlot:
    provider_name: str
    api_key: str
    exhausted: bool = field(default=False, compare=False)


class KeyPool:
    def __init__(self, providers: dict[str, list[str]]):
        self.providers = providers
        self._flat_keys: list[KeySlot] = [
            KeySlot(provider_name=name, api_key=key)
            for name, keys in providers.items()
            for key in keys
        ]
        self._assignments: dict[str, KeySlot] = {}

    def probe_and_prune(self) -> None:
        """Kiểm tra nhanh từng key/provider ngay lúc tạo phòng (không tính vào
        lượt chơi nào). Key/provider nào không sẵn sàng (endpoint self-hosted
        đang tắt, key sai...) bị đánh dấu exhausted ngay từ đầu thay vì để
        agent phát hiện ra giữa ván rồi mới fallback. Không throw — nếu tất cả
        đều fail, assign() vẫn có cơ chế fallback riêng của nó."""
        for slot in self._flat_keys:
            try:
                provider_cls = PROVIDER_CLASSES[slot.provider_name]
                model_name = default_model_for(slot.provider_name)
                probe = provider_cls(api_key=slot.api_key, model_name=model_name)
                ok = probe.health_check()
            except Exception as exc:
                logger.warning(
                    "Health check lỗi cho provider %s (...%s): %s",
                    slot.provider_name, slot.api_key[-4:] if slot.api_key else "", exc,
                )
                ok = False
            if not ok:
                slot.exhausted = True
                logger.warning(
                    "Provider %s (key ...%s) KHÔNG sẵn sàng lúc khởi động — loại khỏi vòng xoay ban đầu.",
                    slot.provider_name, slot.api_key[-4:] if slot.api_key else "",
                )
            else:
                logger.info("Provider %s (key ...%s) sẵn sàng.", slot.provider_name, slot.api_key[-4:] if slot.api_key else "")

        if all(s.exhausted for s in self._flat_keys):
            logger.error("Không có provider/key nào sẵn sàng sau health check — sẽ dùng lại toàn bộ danh sách gốc làm fallback cuối.")
            for slot in self._flat_keys:
                slot.exhausted = False

    def assign(self, agent_player_ids: list[str]) -> dict[str, KeySlot]:
        if not self._flat_keys:
            raise ValueError("Không có API key nào được cấu hình")
        active = [s for s in self._flat_keys if not s.exhausted]
        pool = active if active else self._flat_keys
        for i, player_id in enumerate(agent_player_ids):
            self._assignments[player_id] = pool[i % len(pool)]
        return self._assignments

    def get_client(self, player_id: str) -> BaseProvider:
        slot = self._assignments[player_id]
        provider_cls = PROVIDER_CLASSES[slot.provider_name]
        model_name = default_model_for(slot.provider_name)
        return provider_cls(api_key=slot.api_key, model_name=model_name)

    def get_provider_name(self, player_id: str) -> str:
        return self._assignments[player_id].provider_name

    def mark_key_exhausted(self, player_id: str) -> bool:
        """Đánh dấu key hiện tại của agent là hết credit. Thử gán key khác còn dùng được.
        Trả True nếu đã gán được key mới, False nếu không còn key nào."""
        current_slot = self._assignments[player_id]
        current_slot.exhausted = True
        logger.warning(
            "Key %s...%s của provider %s bị đánh dấu hết credit.",
            current_slot.api_key[:4], current_slot.api_key[-4:], current_slot.provider_name
        )
        active = [s for s in self._flat_keys if not s.exhausted]
        if active:
            # Gán key mới round-robin trong số key còn active
            idx = list(self._assignments.keys()).index(player_id)
            self._assignments[player_id] = active[idx % len(active)]
            logger.info("Agent %s chuyển sang key mới: %s", player_id, active[idx % len(active)].provider_name)
            return True
        logger.error("Không còn key nào active cho agent %s.", player_id)
        return False

    def key_groups(self) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {}
        for player_id, slot in self._assignments.items():
            key_id = f"{slot.provider_name}:{slot.api_key[-6:]}"
            groups.setdefault(key_id, []).append(player_id)
        return groups
