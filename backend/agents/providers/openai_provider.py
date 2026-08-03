from agents.providers.base_provider import BaseProvider
from config.settings import get_settings


class OpenAIProvider(BaseProvider):
    def generate(self, prompt: str) -> str:
        from openai import OpenAI

        settings = get_settings()
        client = OpenAI(api_key=self.api_key, base_url=settings.openai_base_url)
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
