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
        numeric_supported = self._numeric_claim_supported(answer.text, support_graph, answer.calculations)
        calculation_supported = self._calculation_claim_supported(answer.text, answer.calculations)
        row_grounded = self._row_grounded(query, answer)
        answer_supported = has_citation and citation_nodes_exist and numeric_supported and row_grounded and not has_risky_support
        return {
            "answer_supported": answer_supported,
            "unsupported_claims": [] if answer_supported else [answer.text],
            "contradictions": [],
            "missing_evidence": self._missing_evidence(has_citation, numeric_supported, row_grounded),
            "citation_correct": citation_nodes_exist,
            "confidence": 0.85 if answer_supported else 0.35,
            "context_utilization": self._context_utilization(numeric_supported, calculation_supported, row_grounded),
            "checked_citations": list(answer.citations),
            "calculation_supported": calculation_supported,
            "row_grounded": row_grounded,
        }

    def _numeric_claim_supported(
        self,
        answer_text: str,
        support_graph: EvidenceGraph,
        calculations: list[str],
    ) -> bool:
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
        calculation_numbers = _calculation_result_numbers(calculations)
        if calculation_numbers:
            return all(
                _is_year(answer_number)
                or any(_close(answer_number, calculation_number) for calculation_number in calculation_numbers)
                for answer_number in answer_numbers
            )
        return all(
            any(_close(answer_number, support_number) for support_number in support_numbers)
            for answer_number in answer_numbers
        )

    def _calculation_claim_supported(self, answer_text: str, calculations: list[str]) -> bool:
        answer_numbers = _numbers(answer_text)
        if not answer_numbers:
            return False
        calculation_numbers = _calculation_result_numbers(calculations)
        if not calculation_numbers:
            return False
        return all(any(_close(answer_number, calculation_number) for calculation_number in calculation_numbers) for answer_number in answer_numbers)

    def _row_grounded(self, query: str, answer: Answer) -> bool:
        row_labels = []
        for calculation in answer.calculations:
            row_labels.extend(match.strip() for match in re.findall(r"\brow=([^:;]+)", calculation))
        row_labels = [label for label in row_labels if label]
        if not row_labels:
            return True
        query_terms = set(_grounding_terms(query))
        if "due after" in query.lower():
            query_terms.add("thereafter")
        if not query_terms:
            return True
        for label in row_labels:
            label_terms = set(_grounding_terms(label))
            if query_terms & label_terms:
                return True
        return False

    def _missing_evidence(self, has_citation: bool, numeric_supported: bool, row_grounded: bool) -> list[str]:
        missing = []
        if not has_citation:
            missing.append("No citations were selected.")
        if not numeric_supported:
            missing.append("Answer contains numeric claims not supported by source numbers or calculation results.")
        if not row_grounded:
            missing.append("Calculation row label does not match query terms.")
        return missing

    def _context_utilization(self, numeric_supported: bool, calculation_supported: bool, row_grounded: bool) -> str:
        if numeric_supported and calculation_supported and row_grounded:
            return "numeric_calculation_row_and_citation_checked"
        if numeric_supported and row_grounded:
            return "numeric_row_and_citation_checked"
        return "citation_only"


def _numbers(text: str) -> list[float]:
    return [float(match) for match in re.findall(r"[-+]?\d+(?:\.\d+)?", text)]


def _calculation_result_numbers(calculations: list[str]) -> list[float]:
    result_numbers = []
    for calculation in calculations:
        if "=" not in calculation:
            continue
        rhs = calculation.rsplit("=", 1)[1]
        result_numbers.extend(_numbers(rhs))
    return result_numbers


def _close(left: float, right: float) -> bool:
    return abs(left - right) < 1e-6


def _is_year(value: float) -> bool:
    return value.is_integer() and 1900 <= int(value) <= 2099


def _grounding_terms(text: str) -> list[str]:
    normalized_text = text.lower().replace("comodities", "commodities")
    stop = {
        "what",
        "was",
        "were",
        "is",
        "are",
        "the",
        "of",
        "in",
        "from",
        "to",
        "for",
        "by",
        "and",
        "or",
        "as",
        "a",
        "an",
        "percentage",
        "percent",
        "change",
        "increase",
        "decrease",
        "total",
        "net",
        "amount",
        "millions",
        "million",
        "year",
    }
    terms = []
    for token in re.findall(r"[a-z0-9]+", normalized_text):
        if token in stop or re.fullmatch(r"20\d{2}", token):
            continue
        if token.endswith("ies") and len(token) > 4:
            token = token[:-3] + "y"
        elif token.endswith("s") and len(token) > 4:
            token = token[:-1]
        terms.append(token)
    return terms
