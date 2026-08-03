from config.settings import get_settings

ENABLED_PROVIDERS = ["gemini", "openai", "ollama", "qwen_vllm"]


def default_model_for(provider_name: str) -> str:
    settings = get_settings()
    if provider_name == "gemini":
        return settings.gemini_model
    if provider_name == "openai":
        return settings.openai_model
    if provider_name == "ollama":
        return settings.ollama_model
    if provider_name == "qwen_vllm":
        return settings.qwen_vllm_model
    raise ValueError(f"Unknown provider: {provider_name}")
