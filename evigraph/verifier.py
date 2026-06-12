from __future__ import annotations

import re
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
        numeric_supported = self._numeric_claim_supported(answer.text, support_graph)
        answer_supported = has_citation and citation_nodes_exist and numeric_supported and not has_risky_support
        return {
            "answer_supported": answer_supported,
            "unsupported_claims": [] if answer_supported else [answer.text],
            "contradictions": [],
            "missing_evidence": self._missing_evidence(has_citation, numeric_supported),
            "citation_correct": citation_nodes_exist,
            "confidence": 0.85 if answer_supported else 0.35,
            "context_utilization": "numeric_and_citation_checked" if numeric_supported else "citation_only",
            "checked_citations": list(answer.citations),
        }

    def _numeric_claim_supported(self, answer_text: str, support_graph: EvidenceGraph) -> bool:
        answer_numbers = _numbers(answer_text)
        if not answer_numbers:
            return bool(support_graph.nodes)

        support_numbers: list[float] = []
        for node in support_graph.nodes.values():
            content = node.content
            if isinstance(content, dict):
                if "result" in content:
                    support_numbers.append(float(content["result"]))
                if "values" in content and isinstance(content["values"], dict):
                    support_numbers.extend(float(value) for value in content["values"].values())
                if "rows" in content:
                    for row in content["rows"]:
                        support_numbers.extend(_numbers(" ".join(str(item) for item in row)))
            else:
                support_numbers.extend(_numbers(content))
        return all(any(abs(answer_number - support_number) < 1e-6 for support_number in support_numbers) for answer_number in answer_numbers)

    def _missing_evidence(self, has_citation: bool, numeric_supported: bool) -> list[str]:
        missing = []
        if not has_citation:
            missing.append("No citations were selected.")
        if not numeric_supported:
            missing.append("Answer contains numeric claims not found in support graph.")
        return missing


def _numbers(text: str) -> list[float]:
    return [float(match) for match in re.findall(r"[-+]?\d+(?:\.\d+)?", text)]
