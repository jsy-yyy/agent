from unittest.mock import MagicMock

import numpy as np
import pytest

from app.core.config import clear_settings_cache
from app.services.embedding import (
    EmbeddingProviderError,
    IndexService,
    NotConfiguredEmbeddingProvider,
    OpenAIEmbeddingProvider,
    create_embedding_provider,
)


class FakeEmbeddingProvider:
    def __init__(self, dim: int = 128) -> None:
        self.dim = dim
        self.calls: list[list[str]] = []

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [np.random.randn(self.dim).astype(np.float32).tolist() for _ in texts]


class TestOpenAIEmbeddingProviderConstruction:
    def test_missing_api_key_raises(self) -> None:
        with pytest.raises(EmbeddingProviderError, match="OPENAI_API_KEY"):
            OpenAIEmbeddingProvider(api_key="", base_url="https://api.example.com", model="text-embedding")

    def test_missing_model_raises(self) -> None:
        with pytest.raises(EmbeddingProviderError, match="EMBEDDING_MODEL"):
            OpenAIEmbeddingProvider(api_key="sk-test", base_url="https://api.example.com", model="")


class TestCreateEmbeddingProvider:
    def test_returns_not_configured_when_empty(self) -> None:
        clear_settings_cache()
        with pytest.MonkeyPatch().context() as mp:
            mp.delenv("OPENAI_API_KEY", raising=False)
            mp.delenv("EMBEDDING_MODEL", raising=False)
            mp.setattr("app.core.config._default_env_files", lambda: [])
            provider = create_embedding_provider()
            assert isinstance(provider, NotConfiguredEmbeddingProvider)

    def test_returns_openai_provider_when_configured(self) -> None:
        clear_settings_cache()
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("OPENAI_API_KEY", "sk-test")
            mp.setenv("EMBEDDING_MODEL", "text-embedding-3-small")
            provider = create_embedding_provider()
            assert isinstance(provider, OpenAIEmbeddingProvider)


class TestOpenAIEmbeddingProvider:
    def test_embed_texts_delegates_to_client(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2]), MagicMock(embedding=[0.3, 0.4])]
        mock_client.embeddings.create.return_value = mock_response

        provider = OpenAIEmbeddingProvider(api_key="sk-test", base_url="https://api.example.com", model="text-embedding")
        provider._client = mock_client

        result = provider.embed_texts(["hello", "world"])
        assert len(result) == 2
        assert result[0] == [0.1, 0.2]
        mock_client.embeddings.create.assert_called_once_with(model="text-embedding", input=["hello", "world"])

    def test_wraps_api_errors(self) -> None:
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API error")

        provider = OpenAIEmbeddingProvider(api_key="sk-test", base_url="https://api.example.com", model="text-embedding")
        provider._client = mock_client

        with pytest.raises(EmbeddingProviderError, match="API error"):
            provider.embed_texts(["text"])


class TestIndexService:
    def test_build_and_retrieve(self) -> None:
        fake = FakeEmbeddingProvider(dim=128)
        svc = IndexService(fake, dimension=128)

        svc.build(["c1", "c2", "c3"], ["text one", "text two", "text three"])
        assert svc.size == 3
        assert svc.is_loaded

        results = svc.retrieve("text one", top_k=2)
        assert len(results) == 2
        # The most similar should be the query itself
        assert results[0][0] in ("c1", "c2", "c3")

    def test_retrieve_on_empty_index_returns_empty(self) -> None:
        fake = FakeEmbeddingProvider()
        svc = IndexService(fake)
        assert svc.retrieve("query") == []

    def test_build_with_empty_texts(self) -> None:
        fake = FakeEmbeddingProvider()
        svc = IndexService(fake)
        svc.build([], [])
        assert not svc.is_loaded
        assert svc.size == 0

    def test_build_mismatched_lengths_raises(self) -> None:
        svc = IndexService(FakeEmbeddingProvider())
        with pytest.raises(ValueError, match="same length"):
            svc.build(["c1"], ["text one", "text two"])

    def test_save_and_load_roundtrip(self, tmp_path) -> None:
        fake = FakeEmbeddingProvider(dim=128)
        svc = IndexService(fake, dimension=128)
        svc.build(["a", "b"], ["alpha", "beta"])

        svc.save(str(tmp_path))

        svc2 = IndexService(fake, dimension=128)
        assert svc2.load(str(tmp_path))
        assert svc2.size == 2

        results = svc2.retrieve("alpha", top_k=1)
        assert len(results) == 1

    def test_load_returns_false_when_no_files(self, tmp_path) -> None:
        svc = IndexService(FakeEmbeddingProvider())
        assert not svc.load(str(tmp_path))

    def test_save_empty_index_does_nothing(self, tmp_path) -> None:
        fake = FakeEmbeddingProvider()
        svc = IndexService(fake)
        svc.save(str(tmp_path))
        assert not (tmp_path / "indexes" / "faiss.index").exists()
