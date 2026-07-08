from __future__ import annotations

import os
import math
import re
from collections import Counter, defaultdict
from hashlib import blake2b
from pathlib import Path
from typing import Any

from evigraph.document_loader import DocumentChunk, DocumentLoader, load_chunks_from_index
from evigraph.schema import EvidenceNode


RETRIEVAL_MODES = (
    "oracle_doc",
    "open",
    "open_tfidf",
    "open_dense",
    "open_hybrid",
    "open_neural_dense",
    "open_neural_hybrid",
    "source_rerank",
)
_DENSE_VECTOR_CACHE: dict[tuple[int, tuple[str, ...]], list[dict[int, float]]] = {}
_TFIDF_CACHE: dict[tuple[str, ...], tuple[object, object]] = {}
_NEURAL_MODEL_CACHE: dict[str, Any] = {}
_NEURAL_VECTOR_CACHE: dict[tuple[str, tuple[str, ...]], Any] = {}
DEFAULT_NEURAL_DENSE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


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
        for rank, (score, chunk) in enumerate(
            sorted(scored, key=lambda item: (-item[0], item[1].chunk_id))[:top_k],
            start=1,
        ):
            nodes.append(self._node_from_chunk(rank, score, chunk))
        return nodes

    def _node_from_chunk(
        self,
        rank: int,
        score: float,
        chunk: DocumentChunk,
        metadata_extra: dict[str, object] | None = None,
    ) -> EvidenceNode:
        node_type, modality, content = _infer_node_content(chunk.text)
        return EvidenceNode(
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
                "retrieval_rank": rank,
                "chunk_id": chunk.chunk_id,
                **(chunk.metadata or {}),
                **(metadata_extra or {}),
            },
        )

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


class HybridRetriever(BM25Retriever):
    """Deterministic BM25 reranker with numeric/table operation features."""

    def retrieve(self, query: str, top_k: int = 8) -> list[EvidenceNode]:
        query_terms = _tokens(query)
        query_term_set = set(query_terms)
        query_years = set(_years(query))
        query_numbers = set(_numbers(query))
        query_operations = _operation_cues(query)
        scored = []

        for chunk, doc_terms in zip(self.chunks, self.tokenized):
            bm25_score = self._score(query_terms, doc_terms)
            doc_text = chunk.text
            doc_term_set = set(doc_terms)
            doc_years = set(_years(doc_text))
            doc_numbers = set(_numbers(doc_text))
            doc_operations = _operation_cues(doc_text)

            lexical_overlap = len(query_term_set & doc_term_set) / max(1, len(query_term_set))
            year_overlap = len(query_years & doc_years) / max(1, len(query_years)) if query_years else 0.0
            number_overlap = (
                len(query_numbers & doc_numbers) / max(1, len(query_numbers)) if query_numbers else 0.0
            )
            operation_overlap = 1.0 if query_operations & doc_operations else 0.0
            table_prior = 1.0 if _looks_like_table(doc_text) and _asks_numeric_table_question(query) else 0.0

            hybrid_score = (
                bm25_score
                + 0.45 * lexical_overlap
                + 0.65 * year_overlap
                + 0.35 * number_overlap
                + 0.30 * operation_overlap
                + 0.25 * table_prior
            )
            if hybrid_score > 0:
                scored.append(
                    (
                        hybrid_score,
                        bm25_score,
                        {
                            "hybrid_lexical_overlap": round(lexical_overlap, 4),
                            "hybrid_year_overlap": round(year_overlap, 4),
                            "hybrid_number_overlap": round(number_overlap, 4),
                            "hybrid_operation_overlap": round(operation_overlap, 4),
                            "hybrid_table_prior": round(table_prior, 4),
                        },
                        chunk,
                    )
                )
        if not scored:
            scored = [(0.0, 0.0, {}, chunk) for chunk in self.chunks]

        nodes = []
        for rank, (hybrid_score, bm25_score, features, chunk) in enumerate(
            sorted(scored, key=lambda item: (-item[0], item[3].chunk_id))[:top_k],
            start=1,
        ):
            nodes.append(
                self._node_from_chunk(
                    rank,
                    hybrid_score,
                    chunk,
                    {
                        "retrieval_model": "bm25_numeric_hybrid",
                        "bm25_score": round(bm25_score, 4),
                        **features,
                    },
                )
            )
        return nodes


class DenseRetriever(BM25Retriever):
    """Local hashed-vector retriever for reproducible dense-style baselines."""

    def __init__(self, chunks: list[DocumentChunk], dimensions: int = 384) -> None:
        super().__init__(chunks)
        self.dimensions = dimensions
        cache_key = (dimensions, tuple(chunk.chunk_id for chunk in chunks))
        cached_vectors = _DENSE_VECTOR_CACHE.get(cache_key)
        if cached_vectors is None:
            cached_vectors = [self._embed(chunk.text) for chunk in chunks]
            _DENSE_VECTOR_CACHE[cache_key] = cached_vectors
        self.chunk_vectors = cached_vectors

    def retrieve(self, query: str, top_k: int = 8) -> list[EvidenceNode]:
        query_vector = self._embed(query)
        scored = []
        for chunk, vector in zip(self.chunks, self.chunk_vectors):
            score = _dot(query_vector, vector)
            if score > 0:
                scored.append((score, chunk))
        if not scored:
            scored = [(0.0, chunk) for chunk in self.chunks]

        nodes = []
        for rank, (score, chunk) in enumerate(
            sorted(scored, key=lambda item: (-item[0], item[1].chunk_id))[:top_k],
            start=1,
        ):
            nodes.append(
                self._node_from_chunk(
                    rank,
                    score,
                    chunk,
                    {"retrieval_model": "local_hashed_dense", "embedding_dimensions": self.dimensions},
                )
            )
        return nodes

    def _embed(self, text: str) -> dict[int, float]:
        vector: dict[int, float] = defaultdict(float)
        for feature, weight in _dense_features(text).items():
            digest = blake2b(feature.encode("utf-8"), digest_size=8).digest()
            raw = int.from_bytes(digest, byteorder="big", signed=False)
            index = raw % self.dimensions
            sign = 1.0 if (raw >> 8) & 1 else -1.0
            vector[index] += sign * weight
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return dict(vector)
        return {index: value / norm for index, value in vector.items()}


class SklearnTfidfRetriever(BM25Retriever):
    """Scikit-learn TF-IDF cosine retrieval baseline for local reproducibility."""

    def __init__(self, chunks: list[DocumentChunk]) -> None:
        super().__init__(chunks)
        cache_key = tuple(chunk.chunk_id for chunk in chunks)
        cached = _TFIDF_CACHE.get(cache_key)
        if cached is None:
            vectorizer, matrix = self._fit_matrix(chunks)
            cached = (vectorizer, matrix)
            _TFIDF_CACHE[cache_key] = cached
        self.vectorizer, self.matrix = cached

    def retrieve(self, query: str, top_k: int = 8) -> list[EvidenceNode]:
        query_vector = self.vectorizer.transform([query])
        scores = (self.matrix @ query_vector.T).toarray().ravel()
        scored = [(float(score), chunk) for score, chunk in zip(scores, self.chunks) if float(score) > 0]
        if not scored:
            scored = [(0.0, chunk) for chunk in self.chunks]

        nodes = []
        for rank, (score, chunk) in enumerate(
            sorted(scored, key=lambda item: (-item[0], item[1].chunk_id))[:top_k],
            start=1,
        ):
            nodes.append(
                self._node_from_chunk(
                    rank,
                    score,
                    chunk,
                    {"retrieval_model": "sklearn_tfidf", "tfidf_analyzer": "word_1_2"},
                )
            )
        return nodes

    def _fit_matrix(self, chunks: list[DocumentChunk]) -> tuple[object, object]:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.preprocessing import normalize
        except ImportError as exc:
            raise RuntimeError(
                "open_tfidf retrieval requires scikit-learn. Install optional retrieval dependencies first."
            ) from exc

        vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            token_pattern=r"(?u)\b[A-Za-z0-9][A-Za-z0-9_./%-]*\b",
            sublinear_tf=True,
            min_df=1,
        )
        matrix = vectorizer.fit_transform(chunk.text for chunk in chunks)
        return vectorizer, normalize(matrix, norm="l2", copy=False)


class NeuralDenseRetriever(BM25Retriever):
    """Sentence-transformer dense retriever for paper-grade neural baselines."""

    def __init__(
        self,
        chunks: list[DocumentChunk],
        model_name: str | None = None,
        embedder: Any | None = None,
    ) -> None:
        super().__init__(chunks)
        self.model_name = model_name or os.environ.get("EVIGRAPH_NEURAL_DENSE_MODEL") or DEFAULT_NEURAL_DENSE_MODEL
        self.embedder = embedder if embedder is not None else self._load_embedder(self.model_name)
        cache_key = (self.model_name, tuple(chunk.chunk_id for chunk in chunks))
        cached_vectors = _NEURAL_VECTOR_CACHE.get(cache_key)
        if cached_vectors is None or embedder is not None:
            cached_vectors = self._encode([chunk.text for chunk in chunks])
            if embedder is None:
                _NEURAL_VECTOR_CACHE[cache_key] = cached_vectors
        self.chunk_vectors = cached_vectors

    def retrieve(self, query: str, top_k: int = 8) -> list[EvidenceNode]:
        query_vector = self._encode([query])[0]
        scores = self._scores(query_vector, self.chunk_vectors)
        scored = [(float(score), chunk) for score, chunk in zip(scores, self.chunks) if float(score) > 0]
        if not scored:
            scored = [(0.0, chunk) for chunk in self.chunks]

        nodes = []
        for rank, (score, chunk) in enumerate(
            sorted(scored, key=lambda item: (-item[0], item[1].chunk_id))[:top_k],
            start=1,
        ):
            nodes.append(
                self._node_from_chunk(
                    rank,
                    score,
                    chunk,
                    {"retrieval_model": "sentence_transformer_dense", "embedding_model": self.model_name},
                )
            )
        return nodes

    def _load_embedder(self, model_name: str) -> Any:
        cached = _NEURAL_MODEL_CACHE.get(model_name)
        if cached is not None:
            return cached
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "open_neural_dense/open_neural_hybrid require sentence-transformers. "
                "Install with: python -m pip install -r requirements-neural-retrieval.txt"
            ) from exc
        model = SentenceTransformer(model_name)
        _NEURAL_MODEL_CACHE[model_name] = model
        return model

    def _encode(self, texts: list[str]) -> Any:
        return self.embedder.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

    def _scores(self, query_vector: Any, chunk_vectors: Any) -> list[float]:
        return [
            sum(float(left) * float(right) for left, right in zip(vector, query_vector))
            for vector in chunk_vectors
        ]


class NeuralHybridRetriever(NeuralDenseRetriever):
    """Hybrid neural dense, BM25, and numeric/table feature retriever."""

    def retrieve(self, query: str, top_k: int = 8) -> list[EvidenceNode]:
        query_terms = _tokens(query)
        query_term_set = set(query_terms)
        query_years = set(_years(query))
        query_numbers = set(_numbers(query))
        query_operations = _operation_cues(query)
        query_vector = self._encode([query])[0]
        neural_scores = self._scores(query_vector, self.chunk_vectors)
        bm25_scores = [self._score(query_terms, doc_terms) for doc_terms in self.tokenized]
        max_bm25 = max([score for score in bm25_scores if score > 0] or [1.0])
        scored = []

        for chunk, doc_terms, neural_score, bm25_score in zip(
            self.chunks,
            self.tokenized,
            neural_scores,
            bm25_scores,
        ):
            doc_text = chunk.text
            doc_term_set = set(doc_terms)
            doc_years = set(_years(doc_text))
            doc_numbers = set(_numbers(doc_text))
            doc_operations = _operation_cues(doc_text)

            lexical_overlap = len(query_term_set & doc_term_set) / max(1, len(query_term_set))
            year_overlap = len(query_years & doc_years) / max(1, len(query_years)) if query_years else 0.0
            number_overlap = (
                len(query_numbers & doc_numbers) / max(1, len(query_numbers)) if query_numbers else 0.0
            )
            operation_overlap = 1.0 if query_operations & doc_operations else 0.0
            table_prior = 1.0 if _looks_like_table(doc_text) and _asks_numeric_table_question(query) else 0.0
            normalized_bm25 = bm25_score / max_bm25 if max_bm25 else 0.0
            hybrid_score = (
                0.55 * neural_score
                + 0.30 * normalized_bm25
                + 0.05 * lexical_overlap
                + 0.05 * year_overlap
                + 0.025 * number_overlap
                + 0.015 * operation_overlap
                + 0.01 * table_prior
            )
            if hybrid_score > 0:
                scored.append(
                    (
                        hybrid_score,
                        neural_score,
                        bm25_score,
                        {
                            "hybrid_lexical_overlap": round(lexical_overlap, 4),
                            "hybrid_year_overlap": round(year_overlap, 4),
                            "hybrid_number_overlap": round(number_overlap, 4),
                            "hybrid_operation_overlap": round(operation_overlap, 4),
                            "hybrid_table_prior": round(table_prior, 4),
                        },
                        chunk,
                    )
                )
        if not scored:
            scored = [(0.0, 0.0, 0.0, {}, chunk) for chunk in self.chunks]

        nodes = []
        for rank, (hybrid_score, neural_score, bm25_score, features, chunk) in enumerate(
            sorted(scored, key=lambda item: (-item[0], item[4].chunk_id))[:top_k],
            start=1,
        ):
            nodes.append(
                self._node_from_chunk(
                    rank,
                    hybrid_score,
                    chunk,
                    {
                        "retrieval_model": "sentence_transformer_bm25_hybrid",
                        "embedding_model": self.model_name,
                        "neural_score": round(float(neural_score), 4),
                        "bm25_score": round(float(bm25_score), 4),
                        **features,
                    },
                )
            )
        return nodes


class CorpusRetriever:
    def retrieve(
        self,
        query: str,
        corpus_path: str | None = None,
        top_k: int = 8,
        source_doc: str | None = None,
        retrieval_mode: str = "oracle_doc",
        adjacent_window: int = 1,
    ) -> list[EvidenceNode]:
        if not corpus_path:
            return MockRetriever().retrieve(query, corpus_path, top_k)

        path = Path(corpus_path)
        if path.is_file() and path.suffix.lower() == ".json":
            chunks = load_chunks_from_index(path)
        else:
            chunks = DocumentLoader().load(path)
        if retrieval_mode == "open":
            nodes = BM25Retriever(chunks).retrieve(query, top_k=top_k)
            return self._with_adjacent_context(nodes, chunks, adjacent_window=adjacent_window)

        if retrieval_mode == "open_tfidf":
            nodes = SklearnTfidfRetriever(chunks).retrieve(query, top_k=top_k)
            return self._with_adjacent_context(nodes, chunks, adjacent_window=adjacent_window)

        if retrieval_mode == "open_dense":
            nodes = DenseRetriever(chunks).retrieve(query, top_k=top_k)
            return self._with_adjacent_context(nodes, chunks, adjacent_window=adjacent_window)

        if retrieval_mode == "open_hybrid":
            nodes = HybridRetriever(chunks).retrieve(query, top_k=top_k)
            return self._with_adjacent_context(nodes, chunks, adjacent_window=adjacent_window)

        if retrieval_mode == "open_neural_dense":
            nodes = NeuralDenseRetriever(chunks).retrieve(query, top_k=top_k)
            return self._with_adjacent_context(nodes, chunks, adjacent_window=adjacent_window)

        if retrieval_mode == "open_neural_hybrid":
            nodes = NeuralHybridRetriever(chunks).retrieve(query, top_k=top_k)
            return self._with_adjacent_context(nodes, chunks, adjacent_window=adjacent_window)

        if source_doc and retrieval_mode == "source_rerank":
            return self._source_rerank(query, chunks, source_doc, top_k, adjacent_window=adjacent_window)

        if source_doc:
            source_name = Path(source_doc).name
            filtered = self._source_doc_chunks(chunks, source_doc, source_name)
            if filtered:
                combined = self._combined_source_chunk(filtered, source_name)
                nodes = BM25Retriever([combined, *filtered]).retrieve(query, top_k=top_k)
                if not any(node.metadata.get("chunk_id") == combined.chunk_id for node in nodes):
                    oracle_node = BM25Retriever([combined]).retrieve(query, top_k=1)[0]
                    oracle_node.metadata["retrieval_rank"] = 0
                    nodes = [oracle_node, *nodes]
                return nodes
        return BM25Retriever(chunks).retrieve(query, top_k=top_k)

    def _combined_source_chunk(self, chunks: list[DocumentChunk], source_name: str) -> DocumentChunk:
        text = "\n".join(chunk.text for chunk in chunks)
        return DocumentChunk(
            chunk_id=f"{Path(source_name).stem}_full",
            text=text,
            source_doc=chunks[0].source_doc,
            metadata={"loader": "source_doc_oracle", "source_doc": source_name},
        )

    def _source_rerank(
        self,
        query: str,
        chunks: list[DocumentChunk],
        source_doc: str,
        top_k: int,
        adjacent_window: int = 1,
    ) -> list[EvidenceNode]:
        source_name = Path(source_doc).name
        open_candidates = BM25Retriever(chunks).retrieve(query, top_k=max(top_k * 4, top_k))
        source_chunks = self._source_doc_chunks(chunks, source_doc, source_name)
        source_candidates = []
        if source_chunks:
            source_candidates = BM25Retriever(
                [self._combined_source_chunk(source_chunks, source_name)] + source_chunks
            ).retrieve(query, top_k=top_k)
        candidates_by_id = {node.node_id: node for node in [*open_candidates, *source_candidates]}
        candidates = list(candidates_by_id.values())
        reranked = sorted(
            candidates,
            key=lambda node: (
                Path(str(node.source_doc)).name == source_name,
                float(node.metadata.get("retrieval_score", 0.0)),
            ),
            reverse=True,
        )
        for node in reranked:
            if Path(str(node.source_doc)).name == source_name or str(source_doc).lower() in node.text().lower():
                node.metadata["rerank_boost"] = "source_doc_match"
        return self._with_adjacent_context(
            reranked[:top_k],
            chunks,
            promote_existing=True,
            neighbor_rank_from_anchor=False,
            adjacent_window=adjacent_window,
        )

    def _matches_source_doc(self, chunk: DocumentChunk, source_doc: str, source_name: str) -> bool:
        if Path(chunk.source_doc).name == source_name:
            return True
        normalized_source = str(source_doc).replace("\\", "/").lower()
        text_lower = chunk.text.lower().replace("\\", "/")
        return normalized_source in text_lower

    def _source_doc_chunks(
        self,
        chunks: list[DocumentChunk],
        source_doc: str,
        source_name: str,
    ) -> list[DocumentChunk]:
        direct = [chunk for chunk in chunks if Path(chunk.source_doc).name == source_name]
        if direct:
            return direct
        matching_sources = {
            chunk.source_doc
            for chunk in chunks
            if self._matches_source_doc(chunk, source_doc, source_name)
        }
        if not matching_sources:
            return []
        return [chunk for chunk in chunks if chunk.source_doc in matching_sources]

    def _with_adjacent_context(
        self,
        nodes: list[EvidenceNode],
        chunks: list[DocumentChunk],
        promote_existing: bool = False,
        neighbor_rank_from_anchor: bool = True,
        adjacent_window: int = 1,
    ) -> list[EvidenceNode]:
        if not nodes:
            return nodes
        adjacent_window = max(0, int(adjacent_window))
        if adjacent_window == 0:
            return nodes
        chunks_by_source: dict[str, list[DocumentChunk]] = defaultdict(list)
        for chunk in chunks:
            chunks_by_source[chunk.source_doc].append(chunk)
        positions: dict[str, tuple[str, int]] = {}
        for source_doc, source_chunks in chunks_by_source.items():
            source_chunks.sort(key=self._chunk_order)
            for index, chunk in enumerate(source_chunks):
                positions[chunk.chunk_id] = (source_doc, index)

        expanded = list(nodes)
        nodes_by_chunk_id = {str(node.metadata.get("chunk_id", "")): node for node in expanded}
        seen_chunk_ids = set(nodes_by_chunk_id)
        for anchor in nodes:
            chunk_id = str(anchor.metadata.get("chunk_id", ""))
            if chunk_id not in positions:
                continue
            source_doc, index = positions[chunk_id]
            source_chunks = chunks_by_source[source_doc]
            for neighbor_index, distance in self._neighbor_indices(index, len(source_chunks), adjacent_window):
                if neighbor_index < 0 or neighbor_index >= len(source_chunks):
                    continue
                neighbor = source_chunks[neighbor_index]
                if neighbor.chunk_id in seen_chunk_ids:
                    if promote_existing:
                        self._mark_existing_neighbor(nodes_by_chunk_id[neighbor.chunk_id], anchor)
                    continue
                neighbor_node = self._neighbor_node(
                    neighbor,
                    anchor,
                    rank_from_anchor=neighbor_rank_from_anchor,
                    distance=distance,
                )
                expanded.append(neighbor_node)
                seen_chunk_ids.add(neighbor.chunk_id)
                nodes_by_chunk_id[neighbor.chunk_id] = neighbor_node
        return expanded

    def _neighbor_indices(self, index: int, source_length: int, adjacent_window: int) -> list[tuple[int, int]]:
        indices: list[tuple[int, int]] = []
        for distance in range(1, adjacent_window + 1):
            for neighbor_index in (index - distance, index + distance):
                if 0 <= neighbor_index < source_length:
                    indices.append((neighbor_index, distance))
        return indices

    def _chunk_order(self, chunk: DocumentChunk) -> tuple[int, int, str]:
        try:
            char_start = int((chunk.metadata or {}).get("char_start", 0))
        except (TypeError, ValueError):
            char_start = 0
        return chunk.page_number or 0, char_start, chunk.chunk_id

    def _neighbor_node(
        self,
        chunk: DocumentChunk,
        anchor: EvidenceNode,
        rank_from_anchor: bool = True,
        distance: int = 1,
    ) -> EvidenceNode:
        node_type, modality, content = _infer_node_content(chunk.text)
        try:
            anchor_score = float(anchor.metadata.get("retrieval_score", 0.0))
        except (TypeError, ValueError):
            anchor_score = 0.0
        retrieval_rank = anchor.metadata.get("retrieval_rank", 999) if rank_from_anchor else 999
        return EvidenceNode(
            node_id=f"neighbor_{anchor.metadata.get('retrieval_rank', 'x')}_{chunk.chunk_id}",
            node_type=node_type,
            content=content,
            source_doc=chunk.source_doc,
            page_number=chunk.page_number,
            modality=modality,
            confidence=1.0,
            cost={
                "tokens": max(1, len(chunk.text.split())),
                "tool_calls": 0,
                "latency_ms": 5,
            },
            metadata={
                "retrieval_score": round(max(0.0, anchor_score - 0.0001), 4),
                "retrieval_rank": retrieval_rank,
                "chunk_id": chunk.chunk_id,
                "neighbor_context": True,
                "neighbor_distance": distance,
                "expanded_from": anchor.node_id,
                "expanded_from_chunk_id": anchor.metadata.get("chunk_id"),
                **(chunk.metadata or {}),
            },
        )

    def _mark_existing_neighbor(self, node: EvidenceNode, anchor: EvidenceNode) -> None:
        try:
            anchor_rank = int(anchor.metadata.get("retrieval_rank", 999))
        except (TypeError, ValueError):
            anchor_rank = 999
        try:
            anchor_score = float(anchor.metadata.get("retrieval_score", 0.0))
        except (TypeError, ValueError):
            anchor_score = 0.0
        if anchor_rank < 999:
            node.metadata["retrieval_score"] = round(max(0.0, anchor_score - 0.0001), 4)
            node.metadata["neighbor_context"] = True
            node.metadata["expanded_from"] = anchor.node_id
            node.metadata["expanded_from_chunk_id"] = anchor.metadata.get("chunk_id")


def _tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[A-Za-z0-9_]+", text.lower()) if len(token) > 1]


def _dense_features(text: str) -> Counter[str]:
    tokens = _tokens(text)
    features: Counter[str] = Counter()
    for token in tokens:
        features[f"tok:{token}"] += 1.0
        padded = f"^{token}$"
        for index in range(max(0, len(padded) - 2)):
            features[f"tri:{padded[index:index + 3]}"] += 0.35
    for first, second in zip(tokens, tokens[1:]):
        features[f"bi:{first}_{second}"] += 0.65
    return features


def _dot(left: dict[int, float], right: dict[int, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(value * right.get(index, 0.0) for index, value in left.items())


def _years(text: str) -> list[str]:
    return re.findall(r"\b(?:19|20)\d{2}\b", text)


def _numbers(text: str) -> list[str]:
    return [match.replace(",", "") for match in re.findall(r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?%?", text)]


def _operation_cues(text: str) -> set[str]:
    lowered = text.lower()
    cues = set()
    cue_groups = {
        "percent": ("percent", "percentage", "%", "rate", "margin"),
        "change": ("increase", "decrease", "change", "grew", "declined", "reduction"),
        "ratio": ("ratio", "represented", "as a percentage of"),
        "sum": ("total", "combined", "sum"),
        "average": ("average", "mean"),
        "difference": ("difference", "higher", "lower", "less", "more"),
    }
    for cue, patterns in cue_groups.items():
        if any(pattern in lowered for pattern in patterns):
            cues.add(cue)
    return cues


def _looks_like_table(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.strip()]
    pipe_rows = [line for line in lines if line.count("|") >= 2]
    return len(pipe_rows) >= 2


def _asks_numeric_table_question(query: str) -> bool:
    lowered = query.lower()
    return bool(
        re.search(r"\b(what|how|calculate|percentage|percent|ratio|average|total|increase|decrease|change)\b", lowered)
    )


def _infer_node_content(text: str) -> tuple[str, str, str | dict]:
    values: dict[str, float] = {}
    for line in text.splitlines():
        row_match = re.search(r"\|\s*(20\d{2})\s*\|\s*(\d+(?:\.\d+)?)\s*\|", line)
        if row_match:
            values[row_match.group(1)] = float(row_match.group(2))

    if not values:
        for year, value in re.findall(r"\b(20\d{2})\b[^\n\r|]{0,20}[|,\s]+(\d+(?:\.\d+)?)", text):
            values.setdefault(year, float(value))

    if len(values) >= 2:
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
