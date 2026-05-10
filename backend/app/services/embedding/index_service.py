from pathlib import Path

import numpy as np

from app.core.config import get_settings
from app.services.embedding.provider import EmbeddingProvider


class IndexService:
    def __init__(self, provider: EmbeddingProvider, dimension: int = 1536) -> None:
        self._provider = provider
        self._dimension = dimension
        self._index: object | None = None
        self._chunk_ids: list[str] = []

    @property
    def is_loaded(self) -> bool:
        return self._index is not None

    @property
    def size(self) -> int:
        return len(self._chunk_ids)

    def build(self, chunk_ids: list[str], texts: list[str]) -> None:
        """Embed texts and build a FAISS index."""
        if len(chunk_ids) != len(texts):
            raise ValueError("chunk_ids and texts must have the same length")
        if not texts:
            self._index = None
            self._chunk_ids = []
            return

        import faiss

        embeddings = self._provider.embed_texts(texts)
        matrix = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(matrix)

        index = faiss.IndexFlatIP(self._dimension)
        index.add(matrix)
        self._index = index
        self._chunk_ids = list(chunk_ids)

    def retrieve(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        """Retrieve top_k chunk IDs with similarity scores."""
        results = self.retrieve_many([query], top_k=top_k)
        return results[0] if results else []

    def retrieve_many(self, queries: list[str], top_k: int = 5) -> list[list[tuple[str, float]]]:
        """Retrieve top_k chunk IDs for multiple queries using one embedding request."""
        if not self._index or not self._chunk_ids:
            return [[] for _ in queries]
        if not queries:
            return []

        import faiss

        query_embeddings = self._provider.embed_texts(queries)
        query_vecs = np.array(query_embeddings, dtype=np.float32)
        faiss.normalize_L2(query_vecs)

        scores, indices = self._index.search(query_vecs, min(top_k, len(self._chunk_ids)))
        all_results: list[list[tuple[str, float]]] = []
        for row_scores, row_indices in zip(scores, indices):
            results: list[tuple[str, float]] = []
            for score, idx in zip(row_scores, row_indices):
                if idx >= 0 and idx < len(self._chunk_ids):
                    results.append((self._chunk_ids[idx], float(score)))
            all_results.append(results)
        return all_results

    def save(self, path: str | None = None) -> None:
        """Save the FAISS index and chunk ID mapping to disk."""
        if not self._index:
            return

        import faiss

        save_path = Path(path or get_settings().data_dir) / "indexes"
        save_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(save_path / "faiss.index"))
        with open(save_path / "chunk_ids.txt", "w") as f:
            f.write("\n".join(self._chunk_ids))

    def load(self, path: str | None = None) -> bool:
        """Load a previously saved FAISS index. Returns True if successful."""
        import faiss

        load_path = Path(path or get_settings().data_dir) / "indexes"
        index_file = load_path / "faiss.index"
        ids_file = load_path / "chunk_ids.txt"
        if not index_file.exists() or not ids_file.exists():
            return False

        self._index = faiss.read_index(str(index_file))
        with open(ids_file) as f:
            self._chunk_ids = [line.strip() for line in f if line.strip()]
        return True
