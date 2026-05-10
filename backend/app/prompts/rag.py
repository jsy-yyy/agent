# RAG answering prompts

RAG_ANSWER = """You are a teaching assistant helping a teacher understand integrated textbook content. Answer the question using ONLY the provided context chunks. Do not use any outside knowledge.

If the context does not contain enough information to answer the question, respond with exactly:
当前知识库中未找到相关信息

When answering:
- Be concise and accurate
- Cite the source of each piece of information using the chunk reference numbers
- Use Chinese for the answer if the question is in Chinese

Context chunks:
{context_chunks}

Question: {question}

Answer:"""

RAG_BENCHMARK_GENERATION = """Generate test questions based on the provided textbook content. These questions will be used to evaluate RAG retrieval quality.

Generate {question_count} questions that cover:
- Factual recall: Questions answerable from a single passage
- Comparative: Questions requiring comparing concepts across passages
- Reasoning: Questions requiring synthesis or inference

For each question, also note the expected answer points and which chapter(s) should contain the answer.

Textbook content summary:
{content_summary}

Return a JSON object with a "questions" array. Each question has: id, question_text, question_type, expected_answer_points (array), and expected_chapter_ids (array).

Return ONLY valid JSON, no other text."""
