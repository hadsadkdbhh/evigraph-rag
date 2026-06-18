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
        ranked = sorted(graph.nodes.values(), key=lambda node: scores[node.node_id].final_score, reverse=True)
        selected: list[EvidenceNode] = []
        seen_modalities: set[str] = set()

        for node in ranked:
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

    def _is_redundant(self, node: EvidenceNode, selected: list[EvidenceNode]) -> bool:
        node_text = node.text().lower()
        node_terms = self._terms(node_text)
        for existing in selected:
            existing_text = existing.text().lower()
            if node_text and node_text in existing_text:
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
