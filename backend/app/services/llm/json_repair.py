import json
import re


def extract_json_candidate(text: str) -> str:
    """Extract a JSON object from text that may contain surrounding content.

    Handles markdown code fences, leading/trailing prose, and whitespace.
    """
    stripped = text.strip()

    # Try markdown code fences first: ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", stripped, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # Find the outermost { } pair
    start = stripped.find("{")
    if start == -1:
        return stripped
    end = stripped.rfind("}")
    if end == -1:
        return stripped
    return stripped[start : end + 1]


def _try_common_fixes(json_str: str) -> str:
    """Apply common fixes for LLM-generated JSON issues."""
    fixed = json_str

    # Remove trailing commas before closing brackets/braces
    fixed = re.sub(r",(\s*[}\]])", r"\1", fixed)

    # Replace single-quoted keys: 'key':
    fixed = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', fixed)

    # Replace single-quoted values: : 'value'
    fixed = re.sub(r"(:\s*)'([^']*)'", r'\1"\2"', fixed)

    return fixed


def parse_and_repair(text: str, schema_name: str) -> dict:
    """Parse JSON from LLM output with one repair attempt.

    Returns the parsed dict on success.
    Raises ValueError with a descriptive message on failure.
    """
    candidate = extract_json_candidate(text)

    # First attempt: parse directly
    first_error: str = "unknown"
    try:
        result = json.loads(candidate)
        if isinstance(result, dict):
            return result
        raise ValueError(f"LLM returned a JSON {type(result).__name__} instead of an object")
    except (json.JSONDecodeError, ValueError) as exc:
        first_error = str(exc)

    # Second attempt: apply common fixes and retry
    repaired = _try_common_fixes(candidate)
    try:
        result = json.loads(repaired)
        if isinstance(result, dict):
            return result
        raise ValueError(f"Repaired JSON produced a {type(result).__name__} instead of an object")
    except (json.JSONDecodeError, ValueError) as second_error:
        raise ValueError(
            f"Failed to parse JSON for schema '{schema_name}' after repair. "
            f"First error: {first_error}. "
            f"After repair: {second_error}. "
            f"Raw output (first 500 chars): {text[:500]}"
        ) from second_error
