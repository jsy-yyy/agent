"""RAG pipeline: chunking, indexing, retrieval, and grounded answering."""

import uuid

from app.models.records import ChapterRecord, RagChunkRecord
from app.prompts import prompts
from app.services.embedding.index_service import IndexService
from app.services.llm import LLMService
from app.services.rag_service import rag_service


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 80) -> list[str]:
    """Split text into overlapping chunks of approximately chunk_size characters."""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start >= len(text):
            break
    return chunks


class RagPipeline:
    def __init__(self, llm: LLMService, index_service: IndexService) -> None:
        self._llm = llm
        self._index = index_service

    def index_chapters(self, textbook_id: str, chapters: list[ChapterRecord]) -> list[RagChunkRecord]:
        """Chunk chapter text and build the FAISS index."""
        all_chunks: list[dict] = []
        chunk_texts: list[str] = []

        for chapter in chapters:
            texts = chunk_text(chapter.content)
            for i, text in enumerate(texts):
                chunk_id = f"chunk_{uuid.uuid4().hex[:8]}"
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "textbook_id": textbook_id,
                    "chapter_id": chapter.chapter_id,
                    "chunk_index": i,
                    "text": text,
                    "page_start": chapter.page_start,
                    "page_end": chapter.page_end,
                    "token_count": len(text),
                })
                chunk_texts.append(text)

        records = []
        for c in all_chunks:
            records.append(rag_service.create_chunk(**c))

        if chunk_texts:
            self._index.build([c["chunk_id"] for c in all_chunks], chunk_texts)

        return records

    def retrieve(self, question: str, top_k: int = 5) -> list[tuple[RagChunkRecord, float]]:
        """Retrieve top-k chunks for a question."""
        results = self._index.retrieve(question, top_k=top_k)
        out = []
        for chunk_id, score in results:
            try:
                out.append((rag_service.get_chunk(chunk_id), score))
            except KeyError:
                continue
        return out

    def answer(self, question: str, top_k: int = 5) -> dict:
        """Answer a question with grounded citations."""
        retrieved = self.retrieve(question, top_k=top_k)
        if not retrieved:
            return {"answer": "当前知识库中未找到相关信息", "citations": []}

        context_parts = []
        for i, (chunk, _) in enumerate(retrieved):
            context_parts.append(f"[Chunk {i}]\n来源: 教材{chunk.textbook_id}, 第{chunk.page_start or '?'}页\n{chunk.text}")

        context = "\n\n---\n\n".join(context_parts)
        prompt = prompts.format("rag.answer", context_chunks=context, question=question)

        answer_text = self._llm.generate_text(prompt)

        citations = []
        for chunk, score in retrieved:
            citations.append({
                "textbook_id": chunk.textbook_id,
                "chapter_id": chunk.chapter_id,
                "page": chunk.page_start,
                "relevance_score": round(score, 4),
                "chunk_id": chunk.chunk_id,
                "text": chunk.text[:200],
            })

        return {"answer": answer_text.strip(), "citations": citations}
