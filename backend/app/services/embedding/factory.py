from app.core.config import get_settings
from app.services.embedding.openai_embedding import OpenAIEmbeddingProvider
from app.services.embedding.provider import EmbeddingProvider, NotConfiguredEmbeddingProvider


def create_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if not settings.openai_api_key or not settings.embedding_model:
        return NotConfiguredEmbeddingProvider()
    return OpenAIEmbeddingProvider(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.embedding_model,
    )
