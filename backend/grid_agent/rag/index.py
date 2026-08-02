import json
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np

from .chunker import Chunk, chunk_corpus
from .embedder import Embedder

DEFAULT_INDEX_DIR = Path(__file__).resolve().parents[2] / "data" / "rag_index"
DEFAULT_CORPUS_DIR = Path(__file__).resolve().parents[2] / "data" / "rag_corpus"


@dataclass
class RetrievedChunk:
    text: str
    source: str
    chunk_index: int
    score: float


class RagIndex:
    """FAISS flat index (inner product over normalized vectors = cosine similarity)
    with a parallel JSON metadata store mapping vector position -> chunk info.
    """

    def __init__(self, embedder: Embedder | None = None):
        self.embedder = embedder or Embedder()
        self.index: faiss.Index | None = None
        self.chunks: list[Chunk] = []

    def build(self, corpus_dir: Path = DEFAULT_CORPUS_DIR) -> None:
        chunks = chunk_corpus(corpus_dir)
        if not chunks:
            raise ValueError(
                f"No documents found in {corpus_dir}. Add .txt/.md files to the RAG corpus."
            )

        vectors = self.embedder.embed([c.text for c in chunks])
        matrix = np.array(vectors, dtype="float32")
        faiss.normalize_L2(matrix)

        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)

        self.index = index
        self.chunks = chunks

    def save(self, index_dir: Path = DEFAULT_INDEX_DIR) -> None:
        if self.index is None:
            raise RuntimeError("Cannot save an unbuilt index — call build() first")

        index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_dir / "index.faiss"))

        metadata = [
            {"text": c.text, "source": c.source, "chunk_index": c.chunk_index} for c in self.chunks
        ]
        (index_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    def load(self, index_dir: Path = DEFAULT_INDEX_DIR) -> None:
        self.index = faiss.read_index(str(index_dir / "index.faiss"))
        metadata = json.loads((index_dir / "metadata.json").read_text(encoding="utf-8"))
        self.chunks = [Chunk(**m) for m in metadata]

    def query(self, text: str, top_k: int = 5) -> list[RetrievedChunk]:
        if self.index is None:
            raise RuntimeError("Index not built or loaded — call build() or load() first")

        vector = np.array(self.embedder.embed([text]), dtype="float32")
        faiss.normalize_L2(vector)

        scores, indices = self.index.search(vector, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            chunk = self.chunks[idx]
            results.append(
                RetrievedChunk(
                    text=chunk.text,
                    source=chunk.source,
                    chunk_index=chunk.chunk_index,
                    score=float(score),
                )
            )
        return results
