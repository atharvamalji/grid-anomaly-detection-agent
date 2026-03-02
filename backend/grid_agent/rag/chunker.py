from dataclasses import dataclass
from pathlib import Path

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 150


@dataclass
class Chunk:
    text: str
    source: str
    chunk_index: int


def _extract_pdf_text(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def load_documents(corpus_dir: Path) -> list[tuple[str, str]]:
    """Load all .txt/.md/.pdf files in corpus_dir. Returns (filename, text) pairs."""
    docs = []
    for path in sorted(corpus_dir.glob("*")):
        if path.suffix.lower() in (".txt", ".md"):
            docs.append((path.name, path.read_text(encoding="utf-8")))
        elif path.suffix.lower() == ".pdf":
            text = _extract_pdf_text(path)
            if text.strip():
                docs.append((path.name, text))
    return docs


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Chunk]:
    """Split text into overlapping character-based chunks."""
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    index = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk_str = text[start:end].strip()
        if chunk_str:
            chunks.append(Chunk(text=chunk_str, source=source, chunk_index=index))
            index += 1
        if end == text_len:
            break
        start = end - chunk_overlap
    return chunks


def chunk_corpus(corpus_dir: Path) -> list[Chunk]:
    """Load and chunk every document in corpus_dir."""
    all_chunks = []
    for filename, text in load_documents(corpus_dir):
        all_chunks.extend(chunk_text(text, source=filename))
    return all_chunks
