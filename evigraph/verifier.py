from __future__ import annotations

from typing import Any

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import Answer


class ClaimVerifier:
    def verify(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> dict[str, Any]:
        has_citation = bool(answer.citations)
        citation_nodes_exist = all(citation in support_graph.nodes for citation in answer.citations)
        has_risky_support = any(
            node.scores.get("misleading_risk", 0.0) >= 0.65 or node.scores.get("contradiction_risk", 0.0) >= 0.65
            for node in support_graph.nodes.values()
        )
        answer_supported = has_citation and citation_nodes_exist and not has_risky_support
        return {
            "answer_supported": answer_supported,
            "unsupported_claims": [] if answer_supported else [answer.text],
            "contradictions": [],
            "missing_evidence": [] if has_citation else ["No citations were selected."],
            "citation_correct": citation_nodes_exist,
            "confidence": 0.85 if answer_supported else 0.35,
            "context_utilization": "support_subgraph_only",
        }
