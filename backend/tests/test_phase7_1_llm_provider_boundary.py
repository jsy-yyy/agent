import pytest

from app.services.llm import LLMProviderError, LLMService, NotConfiguredLLMProvider


class FakeLLMProvider:
    def __init__(self) -> None:
        self.text_prompts: list[str] = []
        self.json_requests: list[tuple[str, str]] = []

    def generate_text(self, prompt: str) -> str:
        self.text_prompts.append(prompt)
        return "generated text"

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, str]:
        self.json_requests.append((prompt, schema_name))
        return {"schema": schema_name, "result": "generated json"}


def test_llm_service_delegates_text_generation_to_provider() -> None:
    provider = FakeLLMProvider()
    service = LLMService(provider)

    result = service.generate_text("summarize this chapter")

    assert result == "generated text"
    assert provider.text_prompts == ["summarize this chapter"]


def test_llm_service_delegates_json_generation_to_provider() -> None:
    provider = FakeLLMProvider()
    service = LLMService(provider)

    result = service.generate_json("extract entities", "knowledge_graph")

    assert result == {"schema": "knowledge_graph", "result": "generated json"}
    assert provider.json_requests == [("extract entities", "knowledge_graph")]


def test_not_configured_provider_fails_with_clear_boundary_error() -> None:
    service = LLMService(NotConfiguredLLMProvider())

    with pytest.raises(LLMProviderError, match="not configured"):
        service.generate_text("hello")
