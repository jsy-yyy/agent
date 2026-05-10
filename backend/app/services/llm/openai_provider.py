import time
from typing import Any

from openai import OpenAI

from app.services.llm.json_repair import parse_and_repair
from app.services.llm.provider import CallMetadata, LLMProviderError


class OpenAICompatibleProvider:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        enable_thinking: bool | None = None,
    ) -> None:
        if not api_key:
            raise LLMProviderError("OPENAI_API_KEY is not set")
        if not model:
            raise LLMProviderError("LLM_MODEL is not set")
        self._model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url or None)
        self._call_history: list[CallMetadata] = []
        self._extra_body = {"enable_thinking": enable_thinking} if enable_thinking is not None else None

    @property
    def call_history(self) -> list[CallMetadata]:
        return list(self._call_history)

    @property
    def last_call(self) -> CallMetadata | None:
        return self._call_history[-1] if self._call_history else None

    def generate_text(self, prompt: str) -> str:
        start = time.monotonic()
        try:
            request_kwargs: dict[str, Any] = dict(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
            )
            if self._extra_body is not None:
                request_kwargs["extra_body"] = self._extra_body
            response = self._client.chat.completions.create(**request_kwargs)
            content = response.choices[0].message.content
            result = content if content is not None else ""
            self._record_call("text", None, start, response)
            return result
        except Exception as exc:
            self._call_history.append(
                CallMetadata(call_type="text", schema_name=None, latency_ms=(time.monotonic() - start) * 1000)
            )
            raise LLMProviderError(str(exc)) from exc

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        start = time.monotonic()
        try:
            request_kwargs: dict[str, Any] = dict(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            if self._extra_body is not None:
                request_kwargs["extra_body"] = self._extra_body
            response = self._client.chat.completions.create(**request_kwargs)
            content = response.choices[0].message.content
            if content is None:
                raise LLMProviderError("LLM returned empty response")
            result = parse_and_repair(content, schema_name)
            self._record_call("json", schema_name, start, response)
            return result
        except ValueError as exc:
            self._call_history.append(
                CallMetadata(call_type="json", schema_name=schema_name, latency_ms=(time.monotonic() - start) * 1000)
            )
            raise LLMProviderError(str(exc)) from exc
        except LLMProviderError:
            raise
        except Exception as exc:
            self._call_history.append(
                CallMetadata(call_type="json", schema_name=schema_name, latency_ms=(time.monotonic() - start) * 1000)
            )
            raise LLMProviderError(str(exc)) from exc

    def _record_call(self, call_type: str, schema_name: str | None, start: float, response: Any) -> None:
        latency_ms = (time.monotonic() - start) * 1000
        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", None) if usage else None
        completion_tokens = getattr(usage, "completion_tokens", None) if usage else None
        total_tokens = getattr(usage, "total_tokens", None) if usage else None
        self._call_history.append(
            CallMetadata(
                call_type=call_type,
                schema_name=schema_name,
                latency_ms=latency_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )
        )
