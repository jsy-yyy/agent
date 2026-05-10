import pytest

from app.prompts import PromptRegistry, prompts


class TestPromptRegistry:
    def test_all_expected_prompts_are_registered(self) -> None:
        names = prompts.list_prompts()
        assert "extraction.nodes" in names
        assert "extraction.relations" in names
        assert "alignment.concepts" in names
        assert "alignment.review" in names
        assert "rag.answer" in names
        assert "rag.benchmark_generation" in names
        assert "feedback.explain" in names
        assert "feedback.parse_intent" in names
        assert "feedback.respond" in names

    def test_get_returns_non_empty_template(self) -> None:
        template = prompts.get("extraction.nodes")
        assert "{chapter_content}" in template
        assert len(template) > 100

    def test_get_raises_key_error_for_unknown_prompt(self) -> None:
        with pytest.raises(KeyError, match="nonexistent.prompt"):
            prompts.get("nonexistent.prompt")

    def test_format_substitutes_variables(self) -> None:
        result = prompts.format("rag.answer", context_chunks="chunk 1\n\nchunk 2", question="什么是细胞?")
        assert "chunk 1" in result
        assert "chunk 2" in result
        assert "什么是细胞?" in result
        assert "{" not in result

    def test_format_raises_key_error_on_missing_variable(self) -> None:
        with pytest.raises(KeyError):
            prompts.format("rag.answer", context_chunks="test")

    def test_registry_is_isolated_per_instance(self) -> None:
        registry = PromptRegistry()
        assert "extraction.nodes" in registry.list_prompts()

    def test_list_prompts_returns_sorted_names(self) -> None:
        names = prompts.list_prompts()
        assert names == sorted(names)


class TestPromptsNotScattered:
    """All prompt content must be importable from the prompts package, not from route handlers."""

    def test_extraction_prompts_are_importable(self) -> None:
        from app.prompts.extraction import EXTRACT_KNOWLEDGE_NODES, EXTRACT_KNOWLEDGE_RELATIONS
        assert len(EXTRACT_KNOWLEDGE_NODES) > 50
        assert len(EXTRACT_KNOWLEDGE_RELATIONS) > 50

    def test_alignment_prompts_are_importable(self) -> None:
        from app.prompts.alignment import ALIGN_CONCEPTS, REVIEW_INTEGRATION_DECISION
        assert len(ALIGN_CONCEPTS) > 50
        assert len(REVIEW_INTEGRATION_DECISION) > 50

    def test_rag_prompts_are_importable(self) -> None:
        from app.prompts.rag import RAG_ANSWER, RAG_BENCHMARK_GENERATION
        assert len(RAG_ANSWER) > 50
        assert len(RAG_BENCHMARK_GENERATION) > 50

    def test_feedback_prompts_are_importable(self) -> None:
        from app.prompts.feedback import EXPLAIN_DECISION, PARSE_FEEDBACK_INTENT, FEEDBACK_RESPONSE
        assert len(EXPLAIN_DECISION) > 50
        assert len(PARSE_FEEDBACK_INTENT) > 50
        assert len(FEEDBACK_RESPONSE) > 50
