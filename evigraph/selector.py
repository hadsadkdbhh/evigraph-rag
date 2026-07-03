from __future__ import annotations

import re

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import EvidenceNode, EvidenceScore


class EvidenceSetSelector:
    def __init__(self, max_nodes: int = 4, risk_threshold: float = 0.65) -> None:
        self.max_nodes = max_nodes
        self.risk_threshold = risk_threshold

    def select(
        self,
        query: str,
        graph: EvidenceGraph,
        scores: dict[str, EvidenceScore],
    ) -> list[EvidenceNode]:
        source_matched = self._source_matched_nodes(graph)
        candidate_nodes = source_matched or list(graph.nodes.values())
        ranked = sorted(
            candidate_nodes,
            key=lambda node: (
                -scores[node.node_id].final_score,
                self._retrieval_rank(node),
                node.node_id,
            ),
        )
        selected: list[EvidenceNode] = []
        seen_modalities: set[str] = set()

        anchor = self._safe_retrieval_anchor(graph, scores, source_matched)
        if anchor is not None:
            selected.append(anchor)
            seen_modalities.add(anchor.modality)
            anchor.metadata["selection_status"] = "selected"

        for node in ranked:
            if any(existing.node_id == node.node_id for existing in selected):
                continue
            if self._is_context_expansion(node):
                node.metadata["selection_status"] = "context_expansion"
                continue
            score = scores[node.node_id]
            if max(score.misleading_risk, score.contradiction_risk) >= self.risk_threshold:
                node.metadata["selection_status"] = "discarded_risk"
                continue
            if self._is_redundant(node, selected) and node.modality in seen_modalities:
                node.metadata["selection_status"] = "discarded_redundant"
                continue
            selected.append(node)
            seen_modalities.add(node.modality)
            node.metadata["selection_status"] = "selected"
            if len(selected) >= self.max_nodes:
                break
        return selected

    def _safe_retrieval_anchor(
        self,
        graph: EvidenceGraph,
        scores: dict[str, EvidenceScore],
        source_matched: list[EvidenceNode] | None = None,
    ) -> EvidenceNode | None:
        source_matched = source_matched if source_matched is not None else self._source_matched_nodes(graph)
        if source_matched:
            return self._best_safe_anchor(source_matched, scores)

        ranked_by_retrieval = sorted(
            graph.nodes.values(),
            key=lambda node: (self._retrieval_rank(node), node.node_id),
        )
        for node in ranked_by_retrieval:
            if self._is_context_expansion(node):
                continue
            if self._retrieval_rank(node) != 1:
                break
            score = scores[node.node_id]
            if max(score.misleading_risk, score.contradiction_risk) < self.risk_threshold:
                return node
        return None

    def _source_matched_nodes(self, graph: EvidenceGraph) -> list[EvidenceNode]:
        return [
            node
            for node in graph.nodes.values()
            if node.metadata.get("rerank_boost") == "source_doc_match" and not self._is_context_expansion(node)
        ]

    def _best_safe_anchor(
        self,
        nodes: list[EvidenceNode],
        scores: dict[str, EvidenceScore],
    ) -> EvidenceNode | None:
        safe_nodes = [
            node
            for node in nodes
            if max(scores[node.node_id].misleading_risk, scores[node.node_id].contradiction_risk) < self.risk_threshold
        ]
        if not safe_nodes:
            return None
        return max(
            safe_nodes,
            key=lambda node: (
                scores[node.node_id].final_score,
                -self._retrieval_rank(node),
                node.node_id,
            ),
        )

    def _retrieval_rank(self, node: EvidenceNode) -> int:
        try:
            return int(node.metadata.get("retrieval_rank", 999))
        except (TypeError, ValueError):
            return 999

    def _is_context_expansion(self, node: EvidenceNode) -> bool:
        return bool(node.metadata.get("neighbor_context"))

    def _is_redundant(self, node: EvidenceNode, selected: list[EvidenceNode]) -> bool:
        node_text = node.text().lower()
        node_terms = self._terms(node_text)
        for existing in selected:
            existing_text = existing.text().lower()
            if node.source_doc == existing.source_doc and node_text and node_text in existing_text:
                return True
            if (
                node.source_doc == existing.source_doc
                and node.modality == existing.modality
                and self._jaccard(node_terms, self._terms(existing_text)) >= 0.85
            ):
                return True
        return False

    def _terms(self, text: str) -> set[str]:
        return {term for term in re.findall(r"[a-z0-9]+", text.lower()) if len(term) > 2}

    def _jaccard(self, left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0
        return len(left & right) / len(left | right)
