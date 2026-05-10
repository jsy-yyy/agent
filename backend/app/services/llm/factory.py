from app.core.config import get_settings
from app.services.llm.openai_provider import OpenAICompatibleProvider
from app.services.llm.provider import LLMProvider, NotConfiguredLLMProvider


def create_llm_provider() -> LLMProvider:
    settings = get_settings()
    if not settings.openai_api_key or not settings.llm_model:
        return NotConfiguredLLMProvider()
    return OpenAICompatibleProvider(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.llm_model,
        enable_thinking=settings.llm_enable_thinking,
    )
