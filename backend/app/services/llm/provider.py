from dataclasses import dataclass, field
from typing import Any, Protocol


class LLMProviderError(RuntimeError):
    """Raised when the configured LLM provider cannot satisfy a request."""


@dataclass
class CallMetadata:
    call_type: str  # "text" or "json"
    schema_name: str | None
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class LLMProvider(Protocol):
    def generate_text(self, prompt: str) -> str:
        """Generate plain text from a prompt."""

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        """Generate JSON-compatible data for a named response schema."""


class NotConfiguredLLMProvider:
    def generate_text(self, prompt: str) -> str:
        raise LLMProviderError("LLM provider is not configured.")

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        raise LLMProviderError("LLM provider is not configured.")
