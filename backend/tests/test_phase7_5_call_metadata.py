from unittest.mock import MagicMock

import pytest

from app.services.llm import CallMetadata, LLMProviderError
from app.services.llm.openai_provider import OpenAICompatibleProvider


def _make_mock_response(content: str, usage_tokens: tuple[int, int, int] | None = None) -> MagicMock:
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = content
    if usage_tokens is not None:
        prompt, completion, total = usage_tokens
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = prompt
        mock_response.usage.completion_tokens = completion
        mock_response.usage.total_tokens = total
    else:
        mock_response.usage = None
    return mock_response


def _make_provider() -> OpenAICompatibleProvider:
    provider = OpenAICompatibleProvider(
        api_key="sk-test", base_url="https://api.example.com", model="test-model"
    )
    provider._client = MagicMock()
    return provider


class TestCallMetadata:
    def test_metadata_dataclass_defaults(self) -> None:
        meta = CallMetadata(call_type="text", schema_name=None, latency_ms=123.4)
        assert meta.call_type == "text"
        assert meta.schema_name is None
        assert meta.latency_ms == 123.4
        assert meta.prompt_tokens is None
        assert meta.completion_tokens is None
        assert meta.total_tokens is None

    def test_metadata_dataclass_with_tokens(self) -> None:
        meta = CallMetadata(
            call_type="json", schema_name="graph", latency_ms=500.0,
            prompt_tokens=100, completion_tokens=50, total_tokens=150,
        )
        assert meta.call_type == "json"
        assert meta.schema_name == "graph"
        assert meta.prompt_tokens == 100
        assert meta.completion_tokens == 50
        assert meta.total_tokens == 150


class TestCallHistoryTracking:
    def test_successful_text_call_records_metadata(self) -> None:
        provider = _make_provider()
        provider._client.chat.completions.create.return_value = _make_mock_response(
            "hello", (10, 5, 15)
        )

        result = provider.generate_text("prompt")
        assert result == "hello"
        assert len(provider.call_history) == 1

        meta = provider.last_call
        assert meta is not None
        assert meta.call_type == "text"
        assert meta.schema_name is None
        assert meta.latency_ms > 0
        assert meta.prompt_tokens == 10
        assert meta.completion_tokens == 5
        assert meta.total_tokens == 15

    def test_successful_json_call_records_metadata(self) -> None:
        provider = _make_provider()
        provider._client.chat.completions.create.return_value = _make_mock_response(
            '{"key": "val"}', (20, 10, 30)
        )

        result = provider.generate_json("prompt", "graph")
        assert result == {"key": "val"}
        assert len(provider.call_history) == 1

        meta = provider.last_call
        assert meta is not None
        assert meta.call_type == "json"
        assert meta.schema_name == "graph"
        assert meta.latency_ms > 0
        assert meta.prompt_tokens == 20
        assert meta.completion_tokens == 10
        assert meta.total_tokens == 30

    def test_failed_text_call_still_records_latency(self) -> None:
        provider = _make_provider()
        provider._client.chat.completions.create.side_effect = Exception("timeout")

        with pytest.raises(LLMProviderError, match="timeout"):
            provider.generate_text("prompt")

        assert len(provider.call_history) == 1
        meta = provider.last_call
        assert meta is not None
        assert meta.call_type == "text"
        assert meta.latency_ms > 0
        assert meta.prompt_tokens is None

    def test_failed_json_call_still_records_latency(self) -> None:
        provider = _make_provider()
        provider._client.chat.completions.create.return_value = _make_mock_response(
            "not json", None
        )

        with pytest.raises(LLMProviderError, match="Failed to parse JSON"):
            provider.generate_json("prompt", "graph")

        assert len(provider.call_history) == 1
        meta = provider.last_call
        assert meta is not None
        assert meta.call_type == "json"
        assert meta.schema_name == "graph"
        assert meta.latency_ms > 0

    def test_multiple_calls_accumulate_in_history(self) -> None:
        provider = _make_provider()

        def _response(content: str) -> MagicMock:
            return _make_mock_response(content, (1, 1, 2))

        provider._client.chat.completions.create.side_effect = [
            _response("a"),
            _response("b"),
            _response('{"k": "v"}'),
        ]

        provider.generate_text("p1")
        provider.generate_text("p2")
        provider.generate_json("p3", "s")

        assert len(provider.call_history) == 3
        assert provider.call_history[0].call_type == "text"
        assert provider.call_history[1].call_type == "text"
        assert provider.call_history[2].call_type == "json"

    def test_call_history_returns_copy(self) -> None:
        provider = _make_provider()
        provider._client.chat.completions.create.return_value = _make_mock_response("a", (1, 1, 2))
        provider.generate_text("p1")

        history = provider.call_history
        history.append(CallMetadata(call_type="text", schema_name=None, latency_ms=0))
        assert len(provider.call_history) == 1

    def test_last_call_returns_none_when_no_calls(self) -> None:
        provider = _make_provider()
        assert provider.last_call is None

    def test_metadata_without_usage_info(self) -> None:
        provider = _make_provider()
        provider._client.chat.completions.create.return_value = _make_mock_response("ok", None)

        provider.generate_text("prompt")
        meta = provider.last_call
        assert meta is not None
        assert meta.prompt_tokens is None
        assert meta.completion_tokens is None
        assert meta.total_tokens is None
        assert meta.latency_ms > 0
