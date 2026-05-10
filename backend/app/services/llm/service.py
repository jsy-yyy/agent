from typing import Any

from app.services.llm.provider import LLMProvider


class LLMService:
    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def generate_text(self, prompt: str) -> str:
        return self._provider.generate_text(prompt)

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        return self._provider.generate_json(prompt, schema_name)
