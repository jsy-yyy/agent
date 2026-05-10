# Cross-textbook alignment prompts

ALIGN_CONCEPTS = """You are comparing knowledge points from different textbooks to identify duplicates and equivalents.

For each pair of concepts below, determine if they describe the same knowledge point. Consider:
- Different wording for the same concept
- Different levels of detail for the same topic
- Genuinely different concepts that happen to share keywords

Concept A (from {textbook_a}):
Name: {name_a}
Definition: {definition_a}

Concept B (from {textbook_b}):
Name: {name_b}
Definition: {definition_b}

Return a JSON object with:
- are_equivalent: true or false
- confidence: a number between 0.0 and 1.0
- reason: a brief explanation in Chinese

Return ONLY valid JSON, no other text."""

REVIEW_INTEGRATION_DECISION = """Review the following integration decision for a set of potentially equivalent knowledge points.

Decision context:
{decision_context}

Knowledge points to review:
{nodes_json}

Determine the appropriate action for each pair or group:
- merge: Combine into a single knowledge point (provide merged name and definition)
- keep_separate: Keep as distinct points (explain why they are different)
- remove: Remove as redundant (explain which point covers it)

Return a JSON object with a "decisions" array. Each decision has: action, affected_node_ids, result_name (for merge), result_definition (for merge), reason, and confidence.

Return ONLY valid JSON, no other text."""
