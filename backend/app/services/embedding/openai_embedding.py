from openai import OpenAI

from app.services.embedding.provider import EmbeddingProviderError


class OpenAIEmbeddingProvider:
    def __init__(self, *, api_key: str, base_url: str, model: str) -> None:
        if not api_key:
            raise EmbeddingProviderError("OPENAI_API_KEY is not set")
        if not model:
            raise EmbeddingProviderError("EMBEDDING_MODEL is not set")
        self._model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url or None)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self._client.embeddings.create(model=self._model, input=texts)
            return [d.embedding for d in response.data]
        except Exception as exc:
            raise EmbeddingProviderError(str(exc)) from exc
