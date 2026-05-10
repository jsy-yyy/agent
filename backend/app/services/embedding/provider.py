from typing import Protocol


class EmbeddingProviderError(RuntimeError):
    """Raised when the configured embedding provider cannot satisfy a request."""


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""


class NotConfiguredEmbeddingProvider:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise EmbeddingProviderError("Embedding provider is not configured.")
