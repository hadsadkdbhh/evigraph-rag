from __future__ import annotations

import math
import re

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import EvidenceNode, EvidenceScore


def _clip(value: float) -> float:
    return max(0.0, min(1.0, value))


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[A-Za-z0-9.]+", text.lower()) if len(token) > 1}


class RuleBasedUtilityRiskScorer:
    def score_all(self, query: str, graph: EvidenceGraph) -> dict[str, EvidenceScore]:
        scores = {}
        for node in graph.nodes.values():
            score = self.score_node(query, node, graph)
            node.scores = score.to_dict()
            scores[node.node_id] = score
        return scores

    def score_node(self, query: str, node: EvidenceNode, graph: EvidenceGraph) -> EvidenceScore:
        query_tokens = _tokens(query)
        node_tokens = _tokens(node.text())
        overlap = len(query_tokens & node_tokens) / max(1, len(query_tokens))
        modality_bonus = 0.25 if self._modality_matches(query, node) else 0.0
        relevance = _clip(0.35 + overlap + modality_bonus)

        has_numbers = bool(re.search(r"\d", node.text()))
        utility = _clip(0.25 + 0.45 * relevance + (0.25 if has_numbers else 0.0) + modality_bonus)
        grounding = _clip(0.2 + (0.35 if has_numbers else 0.0) + (0.25 if node.source_doc else 0.0) + modality_bonus)
        uncertainty = _clip(1.0 - node.confidence + (0.2 if "forecast" in node.text().lower() else 0.0))
        misleading_risk = _clip(
            (0.75 if node.metadata.get("is_misleading") else 0.0)
            + (0.25 if node.metadata.get("source_quality") in {"draft", "third_party"} else 0.0)
            + (0.15 if "forecast" in node.text().lower() else 0.0)
        )
        contradiction_risk = _clip(0.8 if node.metadata.get("is_conflicting") else 0.0)
        source_reliability = self._source_reliability(node)
        cost = self._normalized_cost(node)
        final_score = (
            1.0 * relevance
            + 1.5 * utility
            + 1.2 * grounding
            + 0.6 * source_reliability
            - 1.0 * misleading_risk
            - 1.0 * contradiction_risk
            - 0.7 * uncertainty
            - 0.4 * cost
        )
        return EvidenceScore(
            relevance=relevance,
            utility=utility,
            grounding=grounding,
            uncertainty=uncertainty,
            misleading_risk=misleading_risk,
            contradiction_risk=contradiction_risk,
            source_reliability=source_reliability,
            cost=cost,
            final_score=round(final_score, 4),
            reason=self._reason(node, misleading_risk, contradiction_risk, utility),
        )

    def _modality_matches(self, query: str, node: EvidenceNode) -> bool:
        query_lower = query.lower()
        if any(word in query_lower for word in ["chart", "plot", "trend"]):
            return node.modality == "chart"
        if any(word in query_lower for word in ["table", "cell", "row"]):
            return node.modality == "table"
        return node.modality == "text"

    def _source_reliability(self, node: EvidenceNode) -> float:
        quality = node.metadata.get("source_quality")
        if quality == "draft":
            return 0.35
        if quality == "third_party":
            return 0.45
        if node.source_doc and node.source_doc.endswith(".pdf"):
            return 0.85
        return 0.65

    def _normalized_cost(self, node: EvidenceNode) -> float:
        tokens = float(node.cost.get("tokens", len(node.text().split())))
        tool_calls = float(node.cost.get("tool_calls", 0))
        latency_ms = float(node.cost.get("latency_ms", 0))
        return _clip(math.log1p(tokens) / 6.0 + 0.12 * tool_calls + latency_ms / 3000.0)

    def _reason(self, node: EvidenceNode, misleading: float, contradiction: float, utility: float) -> str:
        if misleading > 0.6:
            return "High misleading risk; likely not reliable evidence."
        if contradiction > 0.6:
            return "Conflicts with higher-grounding structured evidence."
        if utility > 0.7:
            return "Useful candidate with answer-bearing content."
        return "Low-to-medium utility candidate."
