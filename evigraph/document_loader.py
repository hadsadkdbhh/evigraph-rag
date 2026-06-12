from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    source_doc: str
    page_number: int | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "source_doc": self.source_doc,
            "page_number": self.page_number,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DocumentChunk":
        return cls(
            chunk_id=str(payload["chunk_id"]),
            text=str(payload["text"]),
            source_doc=str(payload["source_doc"]),
            page_number=payload.get("page_number"),
            metadata=dict(payload.get("metadata", {})),
        )


class DocumentLoader:
    def __init__(self, chunk_size: int = 900, chunk_overlap: int = 120) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load(self, corpus_path: str | Path) -> list[DocumentChunk]:
        path = Path(corpus_path)
        if not path.exists():
            raise FileNotFoundError(f"Corpus path does not exist: {path}")

        files = [path] if path.is_file() else sorted(file for file in path.rglob("*") if file.is_file())
        chunks: list[DocumentChunk] = []
        for file_path in files:
            if self._skip_file(file_path):
                continue
            chunks.extend(self._load_file(file_path))
        return chunks

    def _load_file(self, path: Path) -> list[DocumentChunk]:
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md"}:
            return self._chunk_text(path.read_text(encoding="utf-8", errors="ignore"), path)
        if suffix == ".jsonl":
            return self._load_jsonl(path)
        if suffix == ".json":
            return self._load_json(path)
        if suffix == ".csv":
            return self._load_csv(path)
        if suffix == ".pdf":
            return self._load_pdf(path)
        return []

    def _chunk_text(self, text: str, path: Path, page_number: int | None = None) -> list[DocumentChunk]:
        normalized = self._normalize_text(text, path)
        if not normalized:
            return []
        chunks = []
        start = 0
        index = 0
        step = max(1, self.chunk_size - self.chunk_overlap)
        while start < len(normalized):
            chunk_text = normalized[start : start + self.chunk_size].strip()
            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{path.stem}_{page_number or 0}_{index}",
                        text=chunk_text,
                        source_doc=str(path),
                        page_number=page_number,
                        metadata={"loader": "text", "char_start": start},
                    )
                )
            start += step
            index += 1
        return chunks

    def _normalize_text(self, text: str, path: Path) -> str:
        if path.suffix.lower() in {".md", ".csv"}:
            lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
            return "\n".join(line for line in lines if line).strip()
        return re.sub(r"\s+", " ", text).strip()

    def _load_jsonl(self, path: Path) -> list[DocumentChunk]:
        chunks = []
        with path.open("r", encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                if not line.strip():
                    continue
                payload = json.loads(line)
                text = self._payload_text(payload)
                chunks.extend(self._chunk_text(text, path, page_number=payload.get("page_number")))
                for chunk in chunks[-1:]:
                    chunk.chunk_id = f"{path.stem}_{index}_{chunk.chunk_id}"
                    chunk.metadata = {**(chunk.metadata or {}), "record_id": payload.get("id", index)}
        return chunks

    def _load_json(self, path: Path) -> list[DocumentChunk]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            text = "\n".join(self._payload_text(item) for item in payload)
        else:
            text = self._payload_text(payload)
        return self._chunk_text(text, path)

    def _load_csv(self, path: Path) -> list[DocumentChunk]:
        rows = []
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                rows.append(" | ".join(f"{key}: {value}" for key, value in row.items()))
        return self._chunk_text("\n".join(rows), path)

    def _load_pdf(self, path: Path) -> list[DocumentChunk]:
        try:
            import pypdf
        except Exception as exc:
            raise RuntimeError("PDF loading requires pypdf. Install pypdf or use text/JSONL corpus files.") from exc

        chunks = []
        reader = pypdf.PdfReader(str(path))
        for page_index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            chunks.extend(self._chunk_text(text, path, page_number=page_index))
        return chunks

    def _payload_text(self, payload: Any) -> str:
        if isinstance(payload, str):
            return payload
        if isinstance(payload, dict):
            preferred = [payload.get(key) for key in ("text", "content", "caption", "answer")]
            if any(preferred):
                return "\n".join(str(value) for value in preferred if value)
            return "\n".join(f"{key}: {value}" for key, value in payload.items())
        return str(payload)

    def _skip_file(self, path: Path) -> bool:
        return path.name.startswith(".") or any(part in {"outputs", "__pycache__"} for part in path.parts)


def load_chunks_from_index(index_path: str | Path) -> list[DocumentChunk]:
    payload = json.loads(Path(index_path).read_text(encoding="utf-8"))
    return [DocumentChunk.from_dict(item) for item in payload["chunks"]]


def dump_chunks(chunks: Iterable[DocumentChunk], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"chunks": [chunk.to_dict() for chunk in chunks]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
