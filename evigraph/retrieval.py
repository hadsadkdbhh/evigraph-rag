from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

from evigraph.document_loader import DocumentChunk, DocumentLoader, load_chunks_from_index
from evigraph.schema import EvidenceNode


class MockRetriever:
    """Deterministic candidates for MVP-0 smoke tests."""

    def retrieve(self, query: str, corpus_path: str | None = None, top_k: int = 8) -> list[EvidenceNode]:
        query_lower = query.lower()
        nodes = [
            EvidenceNode(
                node_id="chart_2022_2023",
                node_type="chart",
                content={
                    "title": "Revenue by year",
                    "values": {"2022": 87.5, "2023": 100.0},
                    "caption": "Annual revenue increased from 2022 to 2023.",
                },
                source_doc="mock_report.pdf",
                page_number=4,
                bbox=[120, 180, 520, 420],
                modality="chart",
                cost={"tokens": 60, "tool_calls": 1, "latency_ms": 200},
            ),
            EvidenceNode(
                node_id="text_summary",
                node_type="text",
                content="The report states that 2023 revenue was higher than 2022.",
                source_doc="mock_report.pdf",
                page_number=4,
                modality="text",
                cost={"tokens": 18, "tool_calls": 0, "latency_ms": 20},
            ),
            EvidenceNode(
                node_id="table_revenue",
                node_type="table",
                content={
                    "columns": ["year", "revenue"],
                    "rows": [["2022", "87.5"], ["2023", "100.0"]],
                },
                source_doc="mock_report.pdf",
                page_number=5,
                modality="table",
                cost={"tokens": 44, "tool_calls": 1, "latency_ms": 150},
            ),
            EvidenceNode(
                node_id="misleading_old_forecast",
                node_type="text",
                content="A preliminary forecast expected 2023 revenue to be 91.0.",
                source_doc="mock_draft.pdf",
                page_number=2,
                modality="text",
                confidence=0.55,
                cost={"tokens": 16, "tool_calls": 0, "latency_ms": 20},
                metadata={"is_misleading": True, "source_quality": "draft"},
            ),
            EvidenceNode(
                node_id="irrelevant_margin",
                node_type="text",
                content="Operating margin changed because of procurement expenses.",
                source_doc="mock_report.pdf",
                page_number=7,
                modality="text",
                cost={"tokens": 12, "tool_calls": 0, "latency_ms": 20},
            ),
            EvidenceNode(
                node_id="conflicting_press",
                node_type="text",
                content="A press excerpt claims 2023 revenue was only 95.0.",
                source_doc="mock_press_clip.txt",
                modality="text",
                confidence=0.6,
                cost={"tokens": 14, "tool_calls": 0, "latency_ms": 20},
                metadata={"is_conflicting": True, "source_quality": "third_party"},
            ),
        ]

        if "chart" not in query_lower and "higher" not in query_lower:
            nodes = list(reversed(nodes))
        return nodes[:top_k]


class BM25Retriever:
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = chunks
        self.tokenized = [_tokens(chunk.text) for chunk in chunks]
        self.doc_freq = Counter(token for doc in self.tokenized for token in set(doc))
        self.avg_doc_len = sum(len(doc) for doc in self.tokenized) / max(1, len(self.tokenized))

    def retrieve(self, query: str, top_k: int = 8) -> list[EvidenceNode]:
        query_terms = _tokens(query)
        scored = []
        for chunk, doc_terms in zip(self.chunks, self.tokenized):
            score = self._score(query_terms, doc_terms)
            if score > 0:
                scored.append((score, chunk))
        if not scored:
            scored = [(0.0, chunk) for chunk in self.chunks]

        nodes = []
        for rank, (score, chunk) in enumerate(sorted(scored, key=lambda item: item[0], reverse=True)[:top_k], start=1):
            node_type, modality, content = _infer_node_content(chunk.text)
            nodes.append(
                EvidenceNode(
                    node_id=f"retrieved_{rank}_{chunk.chunk_id}",
                    node_type=node_type,
                    content=content,
                    source_doc=chunk.source_doc,
                    page_number=chunk.page_number,
                    modality=modality,
                    confidence=1.0,
                    cost={
                        "tokens": max(1, len(chunk.text.split())),
                        "tool_calls": 0,
                        "latency_ms": 10,
                    },
                    metadata={
                        "retrieval_score": round(score, 4),
                        "chunk_id": chunk.chunk_id,
                        **(chunk.metadata or {}),
                    },
                )
            )
        return nodes

    def _score(self, query_terms: list[str], doc_terms: list[str]) -> float:
        k1 = 1.5
        b = 0.75
        counts = Counter(doc_terms)
        doc_len = len(doc_terms)
        score = 0.0
        for term in query_terms:
            if term not in counts:
                continue
            df = self.doc_freq.get(term, 0)
            idf = math.log(1 + (len(self.chunks) - df + 0.5) / (df + 0.5))
            tf = counts[term]
            denom = tf + k1 * (1 - b + b * doc_len / max(1, self.avg_doc_len))
            score += idf * (tf * (k1 + 1) / denom)
        return score


class CorpusRetriever:
    def retrieve(self, query: str, corpus_path: str | None = None, top_k: int = 8) -> list[EvidenceNode]:
        if not corpus_path:
            return MockRetriever().retrieve(query, corpus_path, top_k)

        path = Path(corpus_path)
        if path.is_file() and path.suffix.lower() == ".json":
            chunks = load_chunks_from_index(path)
        else:
            chunks = DocumentLoader().load(path)
        return BM25Retriever(chunks).retrieve(query, top_k=top_k)


def _tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[A-Za-z0-9_]+", text.lower()) if len(token) > 1]


def _infer_node_content(text: str) -> tuple[str, str, str | dict]:
    values: dict[str, float] = {}
    for line in text.splitlines():
        row_match = re.search(r"\|\s*(20\d{2})\s*\|\s*(\d+(?:\.\d+)?)\s*\|", line)
        if row_match:
            values[row_match.group(1)] = float(row_match.group(2))

    if not values:
        for year, value in re.findall(r"\b(20\d{2})\b[^\n\r|]{0,20}[|,\s]+(\d+(?:\.\d+)?)", text):
            values.setdefault(year, float(value))

    if "2022" in values and "2023" in values:
        return (
            "table",
            "table",
            {
                "columns": ["year", "value"],
                "rows": [[year, str(value)] for year, value in sorted(values.items())],
                "raw_text": text,
            },
        )

    return "text", "text", text
