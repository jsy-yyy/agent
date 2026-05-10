from typing import Any

from app.prompts import alignment, extraction, feedback, rag


class PromptRegistry:
    def __init__(self) -> None:
        self._prompts: dict[str, str] = {
            "extraction.nodes": extraction.EXTRACT_KNOWLEDGE_NODES,
            "extraction.relations": extraction.EXTRACT_KNOWLEDGE_RELATIONS,
            "alignment.concepts": alignment.ALIGN_CONCEPTS,
            "alignment.review": alignment.REVIEW_INTEGRATION_DECISION,
            "rag.answer": rag.RAG_ANSWER,
            "rag.benchmark_generation": rag.RAG_BENCHMARK_GENERATION,
            "feedback.explain": feedback.EXPLAIN_DECISION,
            "feedback.parse_intent": feedback.PARSE_FEEDBACK_INTENT,
            "feedback.respond": feedback.FEEDBACK_RESPONSE,
        }

    def get(self, name: str) -> str:
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found. Available: {list(self._prompts.keys())}")
        return self._prompts[name]

    def format(self, name: str, **kwargs: Any) -> str:
        template = self.get(name)
        return template.format(**kwargs)

    def list_prompts(self) -> list[str]:
        return sorted(self._prompts.keys())
