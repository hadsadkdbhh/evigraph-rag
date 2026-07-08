from __future__ import annotations

import re
from pathlib import Path
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
        operand_semantics_checked = self._operand_semantics_checked(query, answer)
        period_grounded = self._period_grounded(query, answer)
        source_consistent = self._source_consistent(query, answer, support_graph)
        semantically_grounded = (
            has_citation
            and citation_nodes_exist
            and row_grounded
            and period_grounded
            and operation_semantics_checked
            and not has_risky_support
        )
        answer_supported = (
            has_citation
            and citation_nodes_exist
            and numeric_supported
            and row_grounded
            and period_grounded
            and operation_semantics_checked
            and not has_risky_support
        )
        return {
            "answer_supported": answer_supported,
            "unsupported_claims": [] if answer_supported else [answer.text],
            "contradictions": [],
            "missing_evidence": self._missing_evidence(
                has_citation,
                numeric_supported,
                row_grounded,
                period_grounded,
                operation_semantics_checked,
            ),
            "citation_correct": citation_nodes_exist,
            "confidence": 0.85 if answer_supported else 0.35,
            "context_utilization": self._context_utilization(
                numeric_supported,
                calculation_supported,
                row_grounded,
                period_grounded,
                operation_semantics_checked,
            ),
            "diagnostic_warnings": self._diagnostic_warnings(operand_semantics_checked, source_consistent),
            "checked_citations": list(answer.citations),
            "arithmetically_supported": numeric_supported,
            "calculation_supported": calculation_supported,
            "operation_semantics_checked": operation_semantics_checked,
            "operand_semantics_checked": operand_semantics_checked,
            "period_grounded": period_grounded,
            "source_consistent": source_consistent,
            "row_operation_grounded": row_grounded and period_grounded and operation_semantics_checked,
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
            if self._cash_flow_reconciliation_row_grounded(label, query, support_graph):
                return True
            if self._tax_benefit_reconciliation_endpoint_grounded(label, query, support_graph):
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

    def _cash_flow_reconciliation_row_grounded(
        self,
        label: str,
        query: str,
        support_graph: EvidenceGraph,
    ) -> bool:
        label_lower = label.lower()
        query_lower = query.lower()
        if "net income adjusted" not in label_lower or "reconcile" not in label_lower:
            return False
        if "cash flow data" not in query_lower or "total" not in query_lower:
            return False
        support_lower = " ".join(
            " ".join(str(value) for value in node.content.values()) if isinstance(node.content, dict) else str(node.content)
            for node in support_graph.nodes.values()
        ).lower()
        return "cash flow data" in support_lower

    def _tax_benefit_reconciliation_endpoint_grounded(
        self,
        label: str,
        query: str,
        support_graph: EvidenceGraph,
    ) -> bool:
        label_lower = label.lower()
        if not any(term in label_lower for term in ("ending balance", "beginning balance", "balance at december 31", "balance at january 1")):
            return False
        query_lower = query.lower()
        if "unrecognized tax benefits" not in query_lower:
            return False
        support_lower = " ".join(
            " ".join(str(value) for value in node.content.values()) if isinstance(node.content, dict) else str(node.content)
            for node in support_graph.nodes.values()
        ).lower()
        return (
            "unrecognized tax benefits" in support_lower
            and any(term in support_lower for term in ("reconciliation", "beginning", "ending"))
        )

    def _operation_semantics_checked(self, query: str, answer: Answer) -> bool:
        expected = _expected_operation(query)
        if expected is None:
            return True
        actual = {_calculation_operation(calculation) for calculation in answer.calculations}
        actual.discard(None)
        return bool(actual & expected)

    def _operand_semantics_checked(self, query: str, answer: Answer) -> bool:
        query_terms = set(_grounding_terms(query))
        query_distinctive_terms = _distinctive_terms(query_terms)
        between_phrases = _between_phrases(query)
        for calculation in answer.calculations:
            operation = _calculation_operation(calculation)
            if operation is None:
                continue
            labels = _calculation_field_labels(calculation)
            if operation in {"ratio_percent", "ratio", "ratio_between_years", "percent_of_increase"}:
                numerator_labels = labels_for(labels, ["row", "numerator", "target"])
                denominator_labels = labels_for(labels, ["denominator_row", "denominator", "base"])
                if numerator_labels and not any(
                    _label_specific_to_query(label, query_terms, query_distinctive_terms) for label in numerator_labels
                ):
                    return False
                if denominator_labels and not any(
                    _label_specific_to_query(label, query_terms, query_distinctive_terms) for label in denominator_labels
                ):
                    return False
            elif operation in {"difference", "row_year_difference", "relative_difference_between_rows", "percentage_point_row_difference"}:
                comparison_labels = labels_for(labels, ["row", "target", "base", "denominator_row"])
                if between_phrases and comparison_labels:
                    if not _comparison_labels_cover_between_phrases(comparison_labels, between_phrases):
                        return False
                elif comparison_labels and not any(
                    _label_specific_to_query(label, query_terms, query_distinctive_terms) for label in comparison_labels
                ):
                    return False
            elif operation in {"percent_change", "percent_delta"}:
                row_labels = labels_for(labels, ["row", "target"])
                if row_labels and not any(
                    _label_specific_to_query(label, query_terms, query_distinctive_terms) for label in row_labels
                ):
                    return False
        return True

    def _period_grounded(self, query: str, answer: Answer) -> bool:
        query_years = set(re.findall(r"\b(?:19|20)\d{2}\b", query))
        if not query_years:
            return True
        explicit_calculation_years: set[str] = set()
        for calculation in answer.calculations:
            for match in re.finditer(r"\byears?=([^:;]+)", calculation, flags=re.IGNORECASE):
                explicit_calculation_years.update(re.findall(r"\b(?:19|20)\d{2}\b", match.group(1)))
        if not explicit_calculation_years:
            return True
        if len(query_years) == 1:
            return query_years <= explicit_calculation_years
        if re.search(r"\b(?:from|between)\b", query.lower()):
            return query_years <= explicit_calculation_years
        return bool(query_years & explicit_calculation_years)

    def _source_consistent(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> bool:
        cited_nodes = [support_graph.nodes[citation] for citation in answer.citations if citation in support_graph.nodes]
        cited_families = {
            family
            for node in cited_nodes
            if (family := self._source_family(node.source_doc or node.metadata.get("source_doc")))
        }
        if not cited_families:
            return True

        ranked_nodes = [
            node
            for node in support_graph.nodes.values()
            if self._source_family(node.source_doc or node.metadata.get("source_doc"))
            and self._retrieval_rank(node) < 999
            and node.node_type != "verifier_judgment"
        ]
        families = {self._source_family(node.source_doc or node.metadata.get("source_doc")) for node in ranked_nodes}
        families.discard("")
        if len(families) <= 1:
            return True

        cited_best_rank = min(
            (
                self._retrieval_rank(node)
                for node in ranked_nodes
                if self._source_family(node.source_doc or node.metadata.get("source_doc")) in cited_families
            ),
            default=999,
        )
        if cited_best_rank <= 1:
            return True

        top_nodes = [node for node in ranked_nodes if self._retrieval_rank(node) <= min(3, cited_best_rank - 1)]
        if not top_nodes:
            return True
        query_terms = set(_grounding_terms(query))
        family_stats: dict[str, dict[str, float]] = {}
        for node in top_nodes:
            family = self._source_family(node.source_doc or node.metadata.get("source_doc"))
            if not family:
                continue
            stats = family_stats.setdefault(family, {"count": 0.0, "best_rank": 999.0, "overlap": 0.0})
            stats["count"] += 1.0
            stats["best_rank"] = min(stats["best_rank"], float(self._retrieval_rank(node)))
            stats["overlap"] += float(len(query_terms & set(_grounding_terms(node.text()))))

        for family, stats in family_stats.items():
            if family in cited_families:
                continue
            if stats["count"] >= 3 and stats["best_rank"] < cited_best_rank:
                return False
        return True

    def _source_family(self, source_doc: object) -> str:
        if source_doc is None:
            return ""
        name = Path(str(source_doc)).name.lower()
        match = re.search(r"\bfinqa_\d+_([a-z0-9]+)_\d{4}_", name)
        if match:
            return match.group(1)
        stem = Path(name).stem
        return re.split(r"[_\-.]", stem)[0] if stem else name

    def _retrieval_rank(self, node: Any) -> int:
        try:
            return int(node.metadata.get("retrieval_rank", 999))
        except (TypeError, ValueError):
            return 999

    def _missing_evidence(
        self,
        has_citation: bool,
        numeric_supported: bool,
        row_grounded: bool,
        period_grounded: bool,
        operation_semantics_checked: bool,
    ) -> list[str]:
        missing = []
        if not has_citation:
            missing.append("No citations were selected.")
        if not numeric_supported:
            missing.append("Answer contains numeric claims not supported by source numbers or calculation results.")
        if not row_grounded:
            missing.append("Calculation row label does not match query terms.")
        if not period_grounded:
            missing.append("Calculation period or year does not match query terms.")
        if not operation_semantics_checked:
            missing.append("Calculation operation type does not match query intent.")
        return missing

    def _diagnostic_warnings(self, operand_semantics_checked: bool, source_consistent: bool = True) -> list[str]:
        warnings = []
        if not operand_semantics_checked:
            warnings.append("Calculation operand labels do not match query entities or measures.")
        if not source_consistent:
            warnings.append("Citation source is inconsistent with the higher-ranked source cluster.")
        return warnings

    def _context_utilization(
        self,
        numeric_supported: bool,
        calculation_supported: bool,
        row_grounded: bool,
        period_grounded: bool,
        operation_semantics_checked: bool,
    ) -> str:
        if (
            numeric_supported
            and calculation_supported
            and row_grounded
            and period_grounded
            and operation_semantics_checked
        ):
            return "numeric_calculation_row_operation_and_citation_checked"
        if numeric_supported and row_grounded and period_grounded and operation_semantics_checked:
            return "numeric_row_operation_and_citation_checked"
        return "citation_only"


def _numbers(text: str) -> list[float]:
    return [float(match) for match in re.findall(r"[-+]?\d+(?:\.\d+)?", text)]


def _calculation_field_labels(calculation: str) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    keys = [
        "denominator_row",
        "numerator_column",
        "denominator_column",
        "numerator",
        "denominator",
        "target",
        "base",
        "row",
        "column",
        "years",
        "year",
    ]
    key_pattern = "|".join(re.escape(key) for key in keys)
    pattern = re.compile(rf"\b({key_pattern})=", flags=re.IGNORECASE)
    matches = list(pattern.finditer(calculation))
    for index, match in enumerate(matches):
        key = match.group(1).lower()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(calculation)
        raw_value = calculation[start:end]
        raw_value = _strip_expression_suffix(raw_value)
        raw_value = raw_value.split(";", 1)[0]
        raw_value = raw_value.strip()
        if raw_value:
            fields.setdefault(key, []).append(raw_value)
    return fields


def _strip_expression_suffix(value: str) -> str:
    if ":" not in value:
        return value
    before, after = value.split(":", 1)
    if re.match(r"\s*[-+]?(?:\d|\()", after) or re.search(r"[*/+=]", after):
        return before
    return value


def labels_for(labels: dict[str, list[str]], keys: list[str]) -> list[str]:
    values: list[str] = []
    for key in keys:
        values.extend(labels.get(key, []))
    return values


def _distinctive_terms(terms: set[str]) -> set[str]:
    generic = {
        "amount",
        "amounts",
        "attributable",
        "base",
        "beginning",
        "current",
        "december",
        "ending",
        "first",
        "following",
        "fourth",
        "high",
        "low",
        "measure",
        "next",
        "observed",
        "price",
        "quarter",
        "quarters",
        "reported",
        "reporting",
        "sale",
        "second",
        "share",
        "target",
        "third",
        "unit",
        "value",
        "values",
        "year",
        "years",
    }
    return {term for term in terms if term not in generic and len(term) > 1}


def _label_specific_to_query(label: str, query_terms: set[str], query_distinctive_terms: set[str]) -> bool:
    if _is_generic_period_label(label):
        return True
    if _tax_benefit_endpoint_label_matches_query(label, query_terms):
        return True
    if _period_label_matches_query(label, query_terms):
        return True
    if _cash_flow_reconciliation_label_matches_query(label, query_terms):
        return True
    label_terms = set(_grounding_terms(label))
    if not label_terms:
        return True
    label_distinctive_terms = _distinctive_terms(label_terms)
    if label_distinctive_terms & query_distinctive_terms:
        return True
    if query_distinctive_terms:
        return False
    return bool(label_terms & query_terms)


def _is_generic_period_label(label: str) -> bool:
    label_lower = label.lower()
    return (
        "balance at december 31" in label_lower
        or "period-end" in label_lower
        or "period end" in label_lower
        or "period 2013end" in label_lower
        or ("period" in label_lower and "end" in label_lower)
    )


def _period_label_matches_query(label: str, query_terms: set[str]) -> bool:
    label_lower = label.lower()
    if re.search(r"\b(?:19|20)\d{2}\b", label_lower):
        return True
    return "thereafter" in label_lower


def _cash_flow_reconciliation_label_matches_query(label: str, query_terms: set[str]) -> bool:
    label_lower = label.lower()
    if "reconcile" not in label_lower:
        return False
    return "cash" in query_terms and "flow" in query_terms


def _tax_benefit_endpoint_label_matches_query(label: str, query_terms: set[str]) -> bool:
    label_lower = label.lower()
    if not any(term in label_lower for term in ("ending balance", "beginning balance", "balance at december 31", "balance at january 1")):
        return False
    return {"unrecognized", "tax", "benefit"} <= query_terms


def _between_phrases(query: str) -> list[set[str]]:
    query_lower = query.lower()
    match = re.search(r"\bbetween\s+(.+?)\s+and\s+(.+?)(?:\?|$|\bin\b|\bfrom\b|\bduring\b|\bfor\b|\bas\b)", query_lower)
    if not match:
        return []
    phrases = []
    for group in match.groups():
        terms = set(_grounding_terms(group))
        if terms:
            phrases.append(terms)
    return phrases if len(phrases) == 2 else []


def _comparison_labels_cover_between_phrases(labels: list[str], phrases: list[set[str]]) -> bool:
    label_terms = [set(_grounding_terms(label)) for label in labels]
    for phrase_terms in phrases:
        phrase_distinctive = _distinctive_terms(phrase_terms)
        if phrase_distinctive:
            if not any(phrase_distinctive <= _distinctive_terms(terms) for terms in label_terms):
                return False
        elif not any(phrase_terms <= terms for terms in label_terms):
            return False
    return True


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
    if "ratio" in query_lower and (
        len(re.findall(r"\b20\d{2}\b", query_lower)) >= 2
        or (
            "return" in query_lower
            and ("stock" in query_lower or "shareholder" in query_lower or "s&p" in query_lower)
        )
        or ("performance" in query_lower and ("s&p" in query_lower or "standard & poor" in query_lower))
    ):
        return {"ratio", "ratio_between_years"}
    if "average" in query_lower:
        return {"average", "row_average", "row_values_average", "year_range_average"}
    if any(phrase in query_lower for phrase in ["difference", "net change", "how much higher", "change in", "changed in", "five year change"]):
        return {"difference", "row_year_difference", "pretax_aftertax_difference"}
    if "cash flow" in query_lower and "result" in query_lower:
        return {"sum"}
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
        "quarterly_high_sale_price_percent_change": "percent_change",
        "implicit_percent_increase": "percent_change",
        "prose_current_balance_change": "percent_change",
        "planned_percent_of_increase": "percent_of_increase",
        "percent_delta": "percent_delta",
        "ratio_percent": "ratio_percent",
        "increase_component_ratio_percent": "ratio_percent",
        "future_minimum_payment_next_period_ratio": "ratio_percent",
        "component_amount_ratio": "ratio_percent",
        "ratio_between_years": "ratio_between_years",
        "stock_return_graph_ratio": "ratio",
        "stock_return_graph_growth": "percent_change",
        "stock_return_graph_difference": "difference",
        "component_value_from_total_percent": "ratio_percent",
        "same_column_row_ratio_percent": "ratio_percent",
        "shares_issued_from_dividend_table": "ratio",
        "row_average": "row_average",
        "average_high_low_price": "average",
        "row_values_average": "row_values_average",
        "year_range_average": "year_range_average",
        "planned_average": "average",
        "row_year_difference": "row_year_difference",
        "waterfall_table_change": "difference",
        "planned_difference": "difference",
        "planned_absolute_difference": "difference",
        "respectively_prose_difference": "difference",
        "percentage_point_row_difference": "percentage_point_row_difference",
        "relative_difference_between_rows": "relative_difference_between_rows",
        "pretax_aftertax_difference": "pretax_aftertax_difference",
        "difference": "difference",
        "planned_sum": "sum",
        "cash_flow_result": "sum",
        "next_months_debt_due": "sum",
        "square_feet_expiring_in_year": "sum",
        "options_available_under_plan": "difference",
        "contractual_commitments_total_column_sum": "sum",
        "spread_from_dropped_below_and_ending": "difference",
        "planned_lookup": "lookup",
        "planned_minimum": "lookup",
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
