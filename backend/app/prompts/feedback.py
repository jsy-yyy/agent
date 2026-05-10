# Teacher feedback prompts

EXPLAIN_DECISION = """You are explaining an integration decision to a teacher. The teacher wants to understand why certain knowledge points were handled in a particular way.

Integration decision:
- Action: {action}
- Affected concepts: {affected_concepts}
- Result: {result_summary}
- Reason: {reason}
- Confidence: {confidence}

Explain this decision in clear, educational terms. Include:
1. What happened and why
2. The evidence supporting this decision
3. The impact on the knowledge graph and learning pathways

Respond in Chinese with a conversational tone."""

PARSE_FEEDBACK_INTENT = """Analyze the teacher's feedback message to determine what action they want to take.

Teacher message: {feedback_message}

Available integration decisions:
{available_decisions}

Determine the teacher's intent from these categories:
- keep_removed: Teacher wants to keep a node that was removed
- split_merge: Teacher believes a merge is incorrect and wants to split
- force_merge: Teacher wants to merge nodes that were kept separate
- explain: Teacher is asking for more explanation (no action needed)
- other: The message does not match any integration action

Return a JSON object with:
- intent: the category name
- target_decision_ids: array of decision IDs affected
- target_node_ids: array of node IDs affected
- explanation: brief paraphrase of what the teacher wants

Return ONLY valid JSON, no other text."""

FEEDBACK_RESPONSE = """You are responding to a teacher's feedback about an integration decision in a knowledge graph.

The teacher said: {feedback_message}

Your previous decision: {decision_summary}

After considering the teacher's feedback, provide a response that:
1. Acknowledges the teacher's concern
2. Explains what change will be made (or why no change is needed)
3. Describes the impact on the knowledge graph

Respond in Chinese with a helpful, collaborative tone."""
