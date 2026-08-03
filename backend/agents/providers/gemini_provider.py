from agents.providers.base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    def generate(self, prompt: str) -> str:
        from google import genai

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(model=self.model_name, contents=prompt)
        return response.text
