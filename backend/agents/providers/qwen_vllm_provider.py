import requests

from agents.providers.base_provider import BaseProvider
from config.settings import get_settings


class QwenVllmProvider(BaseProvider):
    """Endpoint self-hosted qua vLLM, tương thích OpenAI /v1/chat/completions.
    Không phải lúc nào endpoint này cũng sẵn sàng (đang bảo trì, quá tải,
    mạng nội bộ chập chờn...) nên mọi lỗi kết nối/timeout đều được raise
    dưới dạng RuntimeError có message rõ ràng để BaseProvider.is_out_of_credit_error
    nhận diện và kích hoạt fallback sang key/provider khác."""

    def __init__(self, api_key: str, model_name: str):
        super().__init__(api_key, model_name)
        settings = get_settings()
        self.base_url = settings.qwen_vllm_base_url.rstrip("/")
        self.timeout_seconds = settings.qwen_vllm_timeout_seconds

    def _headers(self) -> dict:
        if self.api_key and self.api_key != "local":
            return {"Authorization": f"Bearer {self.api_key}"}
        return {}

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout as exc:
            raise RuntimeError(f"Qwen vLLM timeout: {exc}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(f"Qwen vLLM connection error (endpoint không sẵn sàng?): {exc}") from exc
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            raise RuntimeError(f"Qwen vLLM HTTP {status}: {exc}") from exc
        except (KeyError, IndexError, ValueError) as exc:
            raise RuntimeError(f"Qwen vLLM response không đúng định dạng: {exc}") from exc

    def health_check(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self._headers(),
                timeout=5,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
