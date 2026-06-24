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
        row_grounded = self._row_grounded(query, answer, support_graph)
        operation_semantics_checked = self._operation_semantics_checked(query, answer)
        semantically_grounded = citation_nodes_exist and row_grounded and operation_semantics_checked and not has_risky_support
        answer_supported = (
            has_citation
            and citation_nodes_exist
            and numeric_supported
            and row_grounded
            and operation_semantics_checked
            and not has_risky_support
        )
        return {
            "answer_supported": answer_supported,
            "unsupported_claims": [] if answer_supported else [answer.text],
            "contradictions": [],
            "missing_evidence": self._missing_evidence(has_citation, numeric_supported, row_grounded, operation_semantics_checked),
            "citation_correct": citation_nodes_exist,
            "confidence": 0.85 if answer_supported else 0.35,
            "context_utilization": self._context_utilization(
                numeric_supported,
                calculation_supported,
                row_grounded,
                operation_semantics_checked,
            ),
            "checked_citations": list(answer.citations),
            "arithmetically_supported": numeric_supported,
            "calculation_supported": calculation_supported,
            "operation_semantics_checked": operation_semantics_checked,
            "row_operation_grounded": row_grounded and operation_semantics_checked,
            "semantically_grounded": semantically_grounded,
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

    def _row_grounded(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> bool:
        row_labels = []
        for calculation in answer.calculations:
            row_labels.extend(self._calculation_row_labels(calculation))
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
            if self._generic_period_row_grounded(label, query_terms, support_graph):
                return True
        return False

    def _calculation_row_labels(self, calculation: str) -> list[str]:
        labels = []
        for match in re.finditer(r"\brow=", calculation):
            tail = calculation[match.end() :]
            end_positions = [
                position
                for marker in [
                    " denominator_row=",
                    " numerator_column=",
                    " denominator_column=",
                    " column=",
                    ";",
                ]
                if (position := tail.find(marker)) >= 0
            ]
            if end_positions:
                labels.append(tail[: min(end_positions)].strip())
                continue
            labels.append(tail.split(":", 1)[0].strip())
        return labels

    def _generic_period_row_grounded(
        self,
        label: str,
        query_terms: set[str],
        support_graph: EvidenceGraph,
    ) -> bool:
        label_lower = label.lower()
        generic_period_label = (
            "balance at december 31" in label_lower
            or "period-end" in label_lower
            or "period end" in label_lower
            or "period 2013end" in label_lower
            or ("period" in label_lower and "end" in label_lower)
        )
        if not generic_period_label or not query_terms:
            return False
        support_terms: set[str] = set()
        for node in support_graph.nodes.values():
            content = node.content
            if isinstance(content, dict):
                support_terms.update(_grounding_terms(" ".join(str(value) for value in content.values())))
            else:
                support_terms.update(_grounding_terms(str(content)))
        return len(query_terms & support_terms) >= min(2, len(query_terms))

    def _operation_semantics_checked(self, query: str, answer: Answer) -> bool:
        expected = _expected_operation(query)
        if expected is None:
            return True
        actual = {_calculation_operation(calculation) for calculation in answer.calculations}
        actual.discard(None)
        return bool(actual & expected)

    def _missing_evidence(
        self,
        has_citation: bool,
        numeric_supported: bool,
        row_grounded: bool,
        operation_semantics_checked: bool,
    ) -> list[str]:
        missing = []
        if not has_citation:
            missing.append("No citations were selected.")
        if not numeric_supported:
            missing.append("Answer contains numeric claims not supported by source numbers or calculation results.")
        if not row_grounded:
            missing.append("Calculation row label does not match query terms.")
        if not operation_semantics_checked:
            missing.append("Calculation operation type does not match query intent.")
        return missing

    def _context_utilization(
        self,
        numeric_supported: bool,
        calculation_supported: bool,
        row_grounded: bool,
        operation_semantics_checked: bool,
    ) -> str:
        if numeric_supported and calculation_supported and row_grounded and operation_semantics_checked:
            return "numeric_calculation_row_operation_and_citation_checked"
        if numeric_supported and row_grounded and operation_semantics_checked:
            return "numeric_row_operation_and_citation_checked"
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
    return abs(left - right) <= max(0.05, abs(right) * 0.005)


def _is_year(value: float) -> bool:
    return value.is_integer() and 1900 <= int(value) <= 2099


def _expected_operation(query: str) -> set[str] | None:
    query_lower = query.lower()
    if (
        re.search(r"\b(?:percent|percentage)\s+of\s+the\s+change\b", query_lower)
        and re.search(r"\b(?:due to|came from|attributable to)\b", query_lower)
    ):
        return {"percent_of_increase"}
    if (
        "difference" in query_lower
        and "as a percentage of" in query_lower
        and len(re.findall(r"\b20\d{2}\b", query_lower)) >= 2
    ):
        return {"percentage_point_row_difference", "row_year_difference", "difference"}
    if "percent higher" in query_lower or "percentage higher" in query_lower:
        return {"relative_difference_between_rows", "percent_change", "percent_delta"}
    if any(
        phrase in query_lower
        for phrase in [
            "percentage change",
            "percent change",
            "percent of the change",
            "percentage of the change",
            "percent of change",
            "percentage of change",
            "percentage increase",
            "percent increase",
            "percentual increase",
            "percentage decrease",
            "percent decrease",
            "percentual decrease",
            "percentage growth",
            "percent growth",
            "percentual growth",
            "percentage reduction",
            "percent reduction",
            "percentual reduction",
            "growth rate",
            "rate of return",
            "roi",
            "percent higher",
            "percentage higher",
        ]
    ):
        return {"percent_change", "percent_delta"}
    if any(
        phrase in query_lower
        for phrase in [
            "what percentage",
            "what percent",
            "what portion",
            "what share",
            "as a percentage of",
            "represented by",
            "allocated to",
            "comes from",
            "due to",
            "related to",
        ]
    ):
        return {"ratio_percent", "ratio_between_years"}
    if "ratio" in query_lower and len(re.findall(r"\b20\d{2}\b", query_lower)) >= 2:
        return {"ratio", "ratio_between_years"}
    if "average" in query_lower:
        return {"average", "row_average", "row_values_average", "year_range_average"}
    if any(phrase in query_lower for phrase in ["difference", "net change", "how much higher", "change in", "changed in"]):
        return {"difference", "row_year_difference", "pretax_aftertax_difference"}
    return None


def _calculation_operation(calculation: str) -> str | None:
    prefix = calculation.split(":", 1)[0].strip().lower()
    if prefix.startswith("calc_") or prefix == "derived_from_context":
        return "difference"
    operation = prefix.split(" ", 1)[0]
    if operation == "planned_ratio":
        return "ratio_percent" if "* 100" in calculation else "ratio"
    aliases = {
        "percent_change": "percent_change",
        "percent_change_from_to": "percent_change",
        "planned_percent_change": "percent_change",
        "planned_percent_of_increase": "percent_of_increase",
        "percent_delta": "percent_delta",
        "ratio_percent": "ratio_percent",
        "ratio_between_years": "ratio_between_years",
        "row_average": "row_average",
        "row_values_average": "row_values_average",
        "year_range_average": "year_range_average",
        "planned_average": "average",
        "row_year_difference": "row_year_difference",
        "planned_difference": "difference",
        "planned_absolute_difference": "difference",
        "percentage_point_row_difference": "percentage_point_row_difference",
        "relative_difference_between_rows": "relative_difference_between_rows",
        "pretax_aftertax_difference": "pretax_aftertax_difference",
        "difference": "difference",
        "planned_sum": "sum",
        "planned_lookup": "lookup",
        "repeated_increase_projection": "difference",
    }
    return aliases.get(operation)


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
