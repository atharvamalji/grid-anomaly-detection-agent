import argparse
from pathlib import Path

from .index import DEFAULT_CORPUS_DIR, DEFAULT_INDEX_DIR, RagIndex

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chunk, embed, and index the RAG corpus")
    parser.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS_DIR)
    parser.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    args = parser.parse_args()

    index = RagIndex()
    index.build(args.corpus_dir)
    index.save(args.index_dir)
    print(f"Indexed {len(index.chunks)} chunks from {args.corpus_dir} -> {args.index_dir}")
