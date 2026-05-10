from unittest.mock import MagicMock, patch

import pytest

from app.core.config import clear_settings_cache, get_settings
from app.services.llm import (
    LLMProviderError,
    LLMService,
    NotConfiguredLLMProvider,
    OpenAICompatibleProvider,
    create_llm_provider,
)


class TestOpenAICompatibleProviderConstruction:
    def test_missing_api_key_raises_clear_error(self) -> None:
        with pytest.raises(LLMProviderError, match="OPENAI_API_KEY"):
            OpenAICompatibleProvider(api_key="", base_url="https://api.example.com", model="gpt-4")

    def test_missing_model_raises_clear_error(self) -> None:
        with pytest.raises(LLMProviderError, match="LLM_MODEL"):
            OpenAICompatibleProvider(api_key="sk-test", base_url="https://api.example.com", model="")


class TestCreateLLMProviderFromConfig:
    def test_returns_not_configured_when_settings_are_empty(self) -> None:
        clear_settings_cache()
        with patch.dict("os.environ", {}, clear=True), patch("app.core.config._default_env_files", return_value=[]):
            provider = create_llm_provider()
            assert isinstance(provider, NotConfiguredLLMProvider)

    def test_returns_openai_provider_when_settings_are_populated(self) -> None:
        clear_settings_cache()
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "sk-test-key",
                "OPENAI_BASE_URL": "https://api.deepseek.com/v1",
                "LLM_MODEL": "deepseek-chat",
                "LLM_ENABLE_THINKING": "false",
            },
            clear=True,
        ):
            provider = create_llm_provider()
            assert isinstance(provider, OpenAICompatibleProvider)
            assert provider._model == "deepseek-chat"
            assert provider._extra_body == {"enable_thinking": False}


class TestOpenAICompatibleProviderDelegation:
    def test_generate_text_delegates_to_openai_client(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "test response"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAICompatibleProvider(
            api_key="sk-test", base_url="https://api.example.com", model="test-model"
        )
        provider._client = mock_client

        result = provider.generate_text("hello")

        assert result == "test response"
        mock_client.chat.completions.create.assert_called_once_with(
            model="test-model",
            messages=[{"role": "user", "content": "hello"}],
        )

    def test_generate_text_handles_none_content(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAICompatibleProvider(
            api_key="sk-test", base_url="https://api.example.com", model="test-model"
        )
        provider._client = mock_client

        result = provider.generate_text("prompt")
        assert result == ""

    def test_generate_text_wraps_api_error(self) -> None:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API timeout")

        provider = OpenAICompatibleProvider(
            api_key="sk-test", base_url="https://api.example.com", model="test-model"
        )
        provider._client = mock_client

        with pytest.raises(LLMProviderError, match="API timeout"):
            provider.generate_text("prompt")

    def test_generate_json_handles_invalid_json(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not json {broken"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAICompatibleProvider(
            api_key="sk-test", base_url="https://api.example.com", model="test-model"
        )
        provider._client = mock_client

        with pytest.raises(LLMProviderError, match="Failed to parse JSON"):
            provider.generate_json("prompt", "graph")

    def test_generate_json_delegates_to_openai_client(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"key": "value"}'
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAICompatibleProvider(
            api_key="sk-test", base_url="https://api.example.com", model="test-model"
        )
        provider._client = mock_client

        result = provider.generate_json("extract", "graph")

        assert result == {"key": "value"}
        mock_client.chat.completions.create.assert_called_once_with(
            model="test-model",
            messages=[{"role": "user", "content": "extract"}],
            response_format={"type": "json_object"},
        )

    def test_generate_json_handles_none_content(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAICompatibleProvider(
            api_key="sk-test", base_url="https://api.example.com", model="test-model"
        )
        provider._client = mock_client

        with pytest.raises(LLMProviderError, match="empty response"):
            provider.generate_json("prompt", "graph")

    def test_generate_text_passes_extra_body_when_configured(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAICompatibleProvider(
            api_key="sk-test",
            base_url="https://api.example.com",
            model="qwen-model",
            enable_thinking=False,
        )
        provider._client = mock_client

        provider.generate_text("hello")

        mock_client.chat.completions.create.assert_called_once_with(
            model="qwen-model",
            messages=[{"role": "user", "content": "hello"}],
            extra_body={"enable_thinking": False},
        )
