import pytest

from app.services.llm.json_repair import extract_json_candidate, parse_and_repair
from app.services.llm.provider import LLMProviderError


class TestExtractJsonCandidate:
    def test_returns_clean_json_as_is(self) -> None:
        result = extract_json_candidate('{"key": "value"}')
        assert result == '{"key": "value"}'

    def test_strips_markdown_json_fence(self) -> None:
        result = extract_json_candidate('```json\n{"key": "value"}\n```')
        assert result == '{"key": "value"}'

    def test_strips_markdown_fence_without_language(self) -> None:
        result = extract_json_candidate('```\n{"key": "value"}\n```')
        assert result == '{"key": "value"}'

    def test_strips_text_before_json(self) -> None:
        result = extract_json_candidate('Here is the result: {"key": "value"}')
        assert result == '{"key": "value"}'

    def test_strips_text_after_json(self) -> None:
        result = extract_json_candidate('{"key": "value"} End of output.')
        assert result == '{"key": "value"}'

    def test_returns_original_when_no_braces(self) -> None:
        result = extract_json_candidate("plain text")
        assert result == "plain text"


class TestParseAndRepair:
    def test_clean_json_parses_directly(self) -> None:
        result = parse_and_repair('{"name": "test", "count": 42}', "test_schema")
        assert result == {"name": "test", "count": 42}

    def test_repairs_trailing_comma_in_object(self) -> None:
        result = parse_and_repair('{"name": "test",}', "test_schema")
        assert result == {"name": "test"}

    def test_repairs_trailing_comma_in_array(self) -> None:
        result = parse_and_repair('{"items": [1, 2,]}', "test_schema")
        assert result == {"items": [1, 2]}

    def test_repairs_single_quoted_keys(self) -> None:
        result = parse_and_repair("{'name': 'test'}", "test_schema")
        assert result == {"name": "test"}

    def test_markdown_fence_with_trailing_comma(self) -> None:
        result = parse_and_repair('```json\n{"key": "val",}\n```', "test_schema")
        assert result == {"key": "val"}

    def test_nested_objects_with_repair(self) -> None:
        result = parse_and_repair(
            '```json\n{"nodes": [{"id": 1, "name": "a",}],}\n```',
            "test_schema",
        )
        assert result == {"nodes": [{"id": 1, "name": "a"}]}

    def test_raises_on_array_instead_of_object(self) -> None:
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            parse_and_repair("[1, 2, 3]", "test_schema")

    def test_raises_on_string_instead_of_object(self) -> None:
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            parse_and_repair('"just a string"', "test_schema")

    def test_raises_on_completely_broken_json(self) -> None:
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            parse_and_repair("not json at all {broken", "test_schema")

    def test_includes_schema_name_in_error(self) -> None:
        with pytest.raises(ValueError, match="knowledge_graph"):
            parse_and_repair("{broken", "knowledge_graph")

    def test_preserves_chinese_characters(self) -> None:
        result = parse_and_repair('{"名称": "测试", "描述": "中文内容"}', "test_schema")
        assert result == {"名称": "测试", "描述": "中文内容"}


class TestJsonRepairIntegrationWithProvider:
    def test_provider_uses_repair_for_markdown_wrapped_json(self) -> None:
        from unittest.mock import MagicMock

        from app.services.llm.openai_provider import OpenAICompatibleProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '```json\n{"key": "val",}\n```'
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAICompatibleProvider(
            api_key="sk-test", base_url="https://api.example.com", model="test-model"
        )
        provider._client = mock_client

        result = provider.generate_json("prompt", "graph")
        assert result == {"key": "val"}

    def test_provider_raises_on_unrepairable_json(self) -> None:
        from unittest.mock import MagicMock

        from app.services.llm.openai_provider import OpenAICompatibleProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not json {broken stuff"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAICompatibleProvider(
            api_key="sk-test", base_url="https://api.example.com", model="test-model"
        )
        provider._client = mock_client

        with pytest.raises(LLMProviderError, match="Failed to parse JSON"):
            provider.generate_json("prompt", "graph")
