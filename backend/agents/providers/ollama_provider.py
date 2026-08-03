import requests

from agents.providers.base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    BASE_URL = "http://localhost:11434"

    def __init__(self, api_key: str, model_name: str):
        super().__init__(api_key, model_name)

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.Timeout as exc:
            raise RuntimeError(f"Ollama timeout: {exc}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(f"Ollama connection error (chưa chạy?): {exc}") from exc

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.BASE_URL}/api/tags", timeout=3)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
