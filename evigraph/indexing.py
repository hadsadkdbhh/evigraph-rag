from __future__ import annotations

from pathlib import Path

from evigraph.document_loader import DocumentLoader, dump_chunks


class LocalIndexBuilder:
    def __init__(self, chunk_size: int = 900, chunk_overlap: int = 120) -> None:
        self.loader = DocumentLoader(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def build(self, corpus_path: str | Path, output_path: str | Path) -> dict[str, int | str]:
        chunks = self.loader.load(corpus_path)
        dump_chunks(chunks, output_path)
        return {
            "corpus_path": str(corpus_path),
            "output_path": str(output_path),
            "chunks": len(chunks),
        }
