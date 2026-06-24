from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol

from evigraph.clients import LLMClient, make_llm_client
from evigraph.table_executor import TableOperationExecutor, TableOperationResult


@dataclass
class PlannedNumericAnswer:
    text: str
    calculation: str


class NumericPlanClient(Protocol):
    def plan(self, query: str, contexts: list[tuple[str, str]]) -> dict[str, Any]:
        ...


class LLMNumericPlanClient:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def plan(self, query: str, contexts: list[tuple[str, str]]) -> dict[str, Any]:
        return self.llm_client.chat_json(self._messages(query, contexts))

    def _messages(self, query: str, contexts: list[tuple[str, str]]) -> list[dict[str, str]]:
        compact_context = "\n\n".join(
            f"[{node_id}]\n{text[:2200]}" for node_id, text in contexts[:4]
        )
        return [
            {
                "role": "system",
                "content": (
                    "You are a numeric QA planner. Return JSON only. "
                    "Do not compute the final answer in prose. Produce a verifiable plan over cited context."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {query}\n\n"
                    f"Context:\n{compact_context}\n\n"
                    "Return a JSON object with this schema:\n"
                    "{"
                    "\"operation\": \"difference|ratio|percent_change|percent_of_increase|average|sum|product|lookup\", "
                    "\"node_id\": \"context id\", "
                    "\"target\": {\"label\": \"row label or phrase\", \"year\": \"optional column/year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"base\": {\"label\": \"row label or phrase\", \"year\": \"optional column/year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"numerator_target\": {\"label\": \"row label\", \"year\": \"target year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"numerator_base\": {\"label\": \"row label\", \"year\": \"base year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"numerator_delta\": {\"label\": \"waterfall contribution row\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"denominator_target\": {\"label\": \"row label\", \"year\": \"target year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"denominator_base\": {\"label\": \"row label\", \"year\": \"base year\", \"period\": \"optional duration\", \"value\": number}, "
                    "\"values\": [{\"label\": \"row label or phrase\", \"year\": \"optional column/year\", \"period\": \"optional duration\", \"value\": number}], "
                    "\"scale\": \"number|percent\", "
                    "\"rationale\": \"short\""
                    "}\n"
                    "Use target/base for difference, ratio, and percent_change. Use target for lookup. "
                    "Use numerator_target/base and denominator_target/base for percent_of_increase. "
                    "When a waterfall table gives the contribution row directly, use numerator_delta "
                    "with denominator_target/base for percent_of_increase. "
                    "Use values for sum, average, and product. Values must appear in the context or question. "
                    "If the context is a table, you may omit value when label plus year/column identifies a cell; "
                    "the executor will read that cell locally. When multiple columns share a year, set period to "
                    "phrases such as three months ended, six months ended, nine months ended, or twelve months ended."
                ),
            },
        ]


class HeuristicNumericPlanClient:
    """Local program planner used when an external LLM planner is unavailable."""

    def plan(self, query: str, contexts: list[tuple[str, str]]) -> dict[str, Any]:
        lowered = query.lower()
        years = self._years(lowered)
        period = self._period(lowered)
        operation_terms = self._content_terms(lowered)

        if self._is_complement_percent(lowered):
            row_terms = self._complement_terms(lowered) or operation_terms
            return {
                "operation": "complement_percent",
                "node_id": self._node_id(contexts, row_terms),
                "target": {"row_terms": row_terms, "period": period},
                "scale": "percent",
                "rationale": "heuristic complement-percent program",
            }

        if "percent of the increase" in lowered or "percentage of the increase" in lowered:
            target_year, base_year = self._target_base_years(lowered, years)
            numerator_terms = self._terms_after(lowered, ["from", "came from", "attributable to"]) or self._content_terms(lowered)
            denominator_terms = self._terms_after(lowered, ["increase in", "change in"]) or self._content_terms(lowered)
            return {
                "operation": "percent_of_increase",
                "node_id": self._node_id(contexts, [*numerator_terms, *denominator_terms]),
                "numerator_target": {"row_terms": numerator_terms, "year": target_year, "period": period},
                "numerator_base": {"row_terms": numerator_terms, "year": base_year, "period": period},
                "denominator_target": {"row_terms": denominator_terms, "year": target_year, "period": period},
                "denominator_base": {"row_terms": denominator_terms, "year": base_year, "period": period},
                "scale": "percent",
                "rationale": "heuristic percent-of-increase program",
            }

        if self._is_percent_of_change_contribution(lowered):
            target_year, base_year = self._target_base_years(lowered, years)
            numerator_terms, denominator_terms = self._percent_of_change_contribution_terms(lowered)
            return {
                "operation": "percent_of_increase",
                "node_id": self._node_id(contexts, [*numerator_terms, *denominator_terms]),
                "numerator_delta": {"row_terms": numerator_terms, "period": period},
                "denominator_target": {"row_terms": denominator_terms, "year": target_year, "period": period},
                "denominator_base": {"row_terms": denominator_terms, "year": base_year, "period": period},
                "scale": "percent",
                "rationale": "heuristic percent-of-change contribution program",
            }

        if self._is_due_after_ratio(lowered):
            row_terms = self._due_after_row_terms(lowered) or operation_terms
            return {
                "operation": "ratio",
                "node_id": self._node_id(contexts, row_terms),
                "target": {
                    "row_terms": row_terms,
                    "column_terms": ["thereafter", "after"],
                    "period": period,
                },
                "base": {"row_terms": row_terms, "column_terms": ["total"], "period": period},
                "scale": "percent",
                "rationale": "heuristic due-after same-row ratio program",
            }

        if self._is_ratio_percent(lowered):
            numerator_terms, denominator_terms = self._ratio_terms(lowered)
            target_year, _ = self._target_base_years(lowered, years)
            return {
                "operation": "ratio",
                "node_id": self._node_id(contexts, [*numerator_terms, *denominator_terms]),
                "target": {"row_terms": numerator_terms, "year": target_year, "period": period},
                "base": {"row_terms": denominator_terms, "year": target_year, "period": period},
                "scale": "percent",
                "rationale": "heuristic ratio-percent program",
            }

        if re.search(r"\bratio\s+of\b", lowered):
            numerator_terms, denominator_terms = self._ratio_terms(lowered)
            target_year, _ = self._target_base_years(lowered, years)
            return {
                "operation": "ratio",
                "node_id": self._node_id(contexts, [*numerator_terms, *denominator_terms]),
                "target": {"row_terms": numerator_terms, "year": target_year, "period": period},
                "base": {"row_terms": denominator_terms, "year": target_year, "period": period},
                "scale": "number",
                "rationale": "heuristic ratio program",
            }

        if self._is_percent_change(lowered):
            target_year, base_year = self._target_base_years(lowered, years)
            row_terms = self._content_terms(lowered)
            return {
                "operation": "percent_change",
                "node_id": self._node_id(contexts, row_terms),
                "target": {"row_terms": row_terms, "year": target_year, "period": period},
                "base": {"row_terms": row_terms, "year": base_year, "period": period},
                "scale": "percent",
                "rationale": "heuristic period-aware percent-change program",
            }

        entity_difference = self._entity_difference_terms(lowered)
        if entity_difference is not None:
            metric_terms, target_terms, base_terms = entity_difference
            return {
                "operation": "absolute_difference",
                "node_id": self._node_id(contexts, [*metric_terms, *target_terms, *base_terms]),
                "target": {"row_terms": target_terms, "column_terms": metric_terms, "period": period},
                "base": {"row_terms": base_terms, "column_terms": metric_terms, "period": period},
                "rationale": "heuristic entity-to-entity difference program",
            }

        if self._is_difference(lowered):
            target_year, base_year = self._target_base_years(lowered, years)
            row_terms = self._difference_terms(lowered) or operation_terms
            return {
                "operation": "difference",
                "node_id": self._node_id(contexts, row_terms),
                "target": {"row_terms": row_terms, "year": target_year, "period": period},
                "base": {"row_terms": row_terms, "year": base_year, "period": period},
                "rationale": "heuristic difference program",
            }

        if self._is_lookup(lowered, years):
            row_terms = self._lookup_terms(lowered) or operation_terms
            target_year = years[0] if len(years) == 1 else ""
            return {
                "operation": "lookup",
                "node_id": self._node_id(contexts, row_terms),
                "target": {"row_terms": row_terms, "year": target_year, "period": period},
                "rationale": "heuristic lookup program",
            }

        if self._is_average(lowered):
            year_list = self._year_series(lowered, years)
            row_terms = self._aggregate_terms(lowered) or operation_terms
            values = [
                {"row_terms": row_terms, "year": year, "period": period}
                for year in year_list
            ] or [{"row_terms": row_terms, "period": period}]
            return {
                "operation": "average",
                "node_id": self._node_id(contexts, row_terms),
                "values": values,
                "rationale": "heuristic average program",
            }

        if self._is_sum(lowered):
            year_list = self._year_series(lowered, years)
            row_terms = self._aggregate_terms(lowered) or operation_terms
            values = [
                {"row_terms": row_terms, "year": year, "period": period}
                for year in year_list
            ] or [{"row_terms": row_terms, "period": period}]
            return {
                "operation": "sum",
                "node_id": self._node_id(contexts, row_terms),
                "values": values,
                "rationale": "heuristic sum program",
            }

        if any(token in lowered for token in ("multiply", "product", "annualized")):
            values = [{"row_terms": terms} for terms in self._product_terms(lowered)]
            if "365" in lowered:
                values.append({"label": "days in year", "value": 365})
            return {
                "operation": "product",
                "node_id": self._node_id(contexts, operation_terms),
                "values": values,
                "rationale": "heuristic product program",
            }

        return {"operation": "unsupported", "node_id": self._node_id(contexts, operation_terms)}

    def _node_id(self, contexts: list[tuple[str, str]], terms: list[str] | None = None) -> str:
        if not contexts:
            return ""
        normalized_terms = self._content_terms(" ".join(terms or []))
        if not normalized_terms:
            return contexts[0][0]
        best: tuple[int, int, str] | None = None
        for index, (node_id, text) in enumerate(contexts):
            lowered = text.lower()
            score = sum(1 for term in normalized_terms if term in lowered)
            table_bonus = 2 if "|" in text else 0
            candidate = (score + table_bonus, -index, node_id)
            if best is None or candidate > best:
                best = candidate
        return best[2] if best else contexts[0][0]

    def _target_base_years(self, lowered: str, years: list[str]) -> tuple[str, str]:
        from_to = re.search(r"\bfrom\s+(20\d{2})\s+(?:to|through|-)\s+(20\d{2})\b", lowered)
        if from_to:
            return from_to.group(2), from_to.group(1)
        compared = re.search(r"\b(20\d{2})\b.+?\b(?:compared with|compared to)\s+(20\d{2})\b", lowered)
        if compared:
            return compared.group(1), compared.group(2)
        compared_in = re.search(r"\bcompared\s+(?:with|to)\s+(20\d{2})\b.+?\bin\s+(20\d{2})\b", lowered)
        if compared_in:
            return compared_in.group(2), compared_in.group(1)
        if len(years) >= 2:
            return years[-1], years[0]
        if len(years) == 1:
            return years[0], str(int(years[0]) - 1)
        return "", ""

    def _period(self, lowered: str) -> str:
        match = re.search(r"\b(?:three|six|nine|twelve|3|6|9|12)\s+months?\s+ended\b", lowered)
        if match:
            return match.group(0)
        if "year ended" in lowered or "twelve months ended" in lowered:
            return "twelve months ended"
        return ""

    def _years(self, lowered: str) -> list[str]:
        seen = []
        for year in re.findall(r"\b(20\d{2})(?:\b|(?=end\b))", lowered):
            if year not in seen:
                seen.append(year)
        return seen

    def _is_complement_percent(self, lowered: str) -> bool:
        return bool(
            re.search(r"\b(?:not|non|un)\s*-?\s*(?:leased|vested|exercised|paid|current)\b", lowered)
            and ("percent" in lowered or "percentage" in lowered)
        )

    def _is_due_after_ratio(self, lowered: str) -> bool:
        return bool(
            ("percent" in lowered or "percentage" in lowered or "portion" in lowered)
            and ("due after" in lowered or "thereafter" in lowered)
        )

    def _is_ratio_percent(self, lowered: str) -> bool:
        markers = [
            "what percentage of",
            "what percent of",
            "what portion of",
            "what share of",
            "as a percentage of",
            "represented by",
            "relative to",
        ]
        return (
            any(marker in lowered for marker in markers)
            or bool(re.search(r"\b(?:percentage|percent|portion|share)\s+of\b.+?\b(?:that|which)\s+(?:was|were|is|are)\b", lowered))
        ) and not self._is_percent_change(lowered)

    def _is_percent_change(self, lowered: str) -> bool:
        percent_markers = (
            "percent change",
            "percentage change",
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
        )
        if any(marker in lowered for marker in percent_markers):
            return True
        if ("percent" in lowered or "percentage" in lowered or "percentual" in lowered) and any(
            token in lowered for token in ("increase", "decrease", "growth", "decline")
        ):
            return True
        return False

    def _is_percent_of_change_contribution(self, lowered: str) -> bool:
        return bool(
            re.search(r"\b(?:percent|percentage)\s+of\s+the\s+change\b", lowered)
            and re.search(r"\b(?:due to|came from|attributable to)\b", lowered)
        )

    def _is_difference(self, lowered: str) -> bool:
        if self._is_percent_change(lowered):
            return False
        return bool(
            re.search(r"\b(?:difference|change|increase|decrease|decline)\b", lowered)
            and re.search(r"\b(?:between|from|compared with|compared to)\b", lowered)
        )

    def _is_average(self, lowered: str) -> bool:
        return bool(re.search(r"\baverage\b", lowered)) and not any(
            token in lowered for token in ("average daily", "average price")
        )

    def _is_sum(self, lowered: str) -> bool:
        return bool(re.search(r"\b(?:sum|total|combined|aggregate)\b", lowered)) and not self._is_ratio_percent(lowered)

    def _is_lookup(self, lowered: str, years: list[str]) -> bool:
        if self._is_sum(lowered) and len(years) > 1:
            return False
        return bool(
            re.search(r"\b(?:what (?:are|is|was|were) the )?(?:total amount|amount|value|number) of\b", lowered)
            and not any(token in lowered for token in ("average", "ratio", "percentage", "percent", "portion", "share"))
        )

    def _ratio_terms(self, lowered: str) -> tuple[list[str], list[str]]:
        patterns = [
            r"(?:what\s+(?:was|were|is|are)\s+the\s+)?(?:percentage|percent|portion|share) of (?P<base>.+?) (?:that|which) (?:was|were|is|are) (?P<target>.+?)(?:\?|$)",
            r"what (?:percentage|percent|portion|share) of (?P<base>.+?) (?:was|were|is|are) (?:represented by|attributable to|allocated to|related to|comprised of|made up by) (?P<target>.+?)(?:\?|$)",
            r"(?P<target>.+?) as a percentage of (?P<base>.+?)(?:\?|$)",
            r"ratio of (?P<target>.+?) to (?P<base>.+?)(?:\?|$)",
            r"ratio of (?P<target>.+?) compared to (?P<base>.+?)(?:\?|$)",
            r"ratio of (?P<target>.+?) compared with (?P<base>.+?)(?:\?|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, lowered)
            if match:
                return self._content_terms(match.group("target")), self._content_terms(match.group("base"), keep_total=True)

        target = self._terms_after(lowered, ["represented by", "allocated to", "attributable to", "related to"])
        base = self._terms_after(
            lowered,
            ["percentage of", "percent of", "portion of", "share of", "relative to"],
            keep_total=True,
        )
        return target or self._content_terms(lowered), base or self._content_terms(lowered)

    def _percent_of_change_contribution_terms(self, lowered: str) -> tuple[list[str], list[str]]:
        numerator_terms = (
            self._terms_after(lowered, ["due to", "came from", "attributable to"])
            or self._content_terms(lowered)
        )

        denominator_terms: list[str] = []
        for pattern in (
            r"\bchange\s+between\s+(?P<label>.+?)\s+(?:in\s+)?(?:19|20)\d{2}\b",
            r"\bchange\s+in\s+(?P<label>.+?)(?:\s+from\s+(?:19|20)\d{2}|\s+between\s+(?:19|20)\d{2}|\?|$)",
        ):
            match = re.search(pattern, lowered)
            if match:
                denominator_terms = self._content_terms(match.group("label"))
                if denominator_terms:
                    break

        return numerator_terms, denominator_terms or self._content_terms(lowered)

    def _difference_terms(self, lowered: str) -> list[str]:
        return self._terms_after(lowered, ["difference in", "change in", "increase in", "decrease in", "decline in"])

    def _entity_difference_terms(self, lowered: str) -> tuple[list[str], list[str], list[str]] | None:
        match = re.search(
            r"\bdifference\s+in\s+(?P<metric>.+?)\s+between\s+(?P<target>.+?)\s+and\s+(?P<base>.+?)(?:\?|$)",
            lowered,
        )
        if not match:
            return None
        metric_terms = self._content_terms(match.group("metric"))
        target_terms = self._content_terms(match.group("target"))
        base_terms = self._content_terms(re.split(r"\s*,\s*in\s+", match.group("base"), maxsplit=1)[0])
        if not metric_terms or not target_terms or not base_terms:
            return None
        return metric_terms, target_terms, base_terms

    def _aggregate_terms(self, lowered: str) -> list[str]:
        terms = self._terms_after(lowered, ["average", "sum of", "total of", "total amount of", "combined"])
        if terms:
            return terms
        total_match = re.search(r"\btotal\s+(?P<label>.+?)(?:\s+in\s+20\d{2}|\s+from\s+20\d{2}|\?|$)", lowered)
        if total_match:
            return self._content_terms(total_match.group("label"))
        return []

    def _lookup_terms(self, lowered: str) -> list[str]:
        return self._terms_after(lowered, ["total amount of", "amount of", "value of", "number of"])

    def _due_after_row_terms(self, lowered: str) -> list[str]:
        match = re.search(r"percentage of (?P<label>.+?) (?:is|are|was|were)?\s*due after", lowered)
        if match:
            return self._content_terms(match.group("label"))
        return self._terms_after(lowered, ["percentage of", "percent of", "portion of"])

    def _complement_terms(self, lowered: str) -> list[str]:
        terms = self._content_terms(lowered)
        complement_noise = {"not", "non", "un", "percentage", "percent"}
        cleaned = [term for term in terms if term not in complement_noise]
        for preferred in ("leased", "vested", "exercised", "paid", "current"):
            if preferred in cleaned:
                return [preferred]
        return cleaned

    def _terms_after(self, lowered: str, markers: list[str], keep_total: bool = False) -> list[str]:
        for marker in markers:
            index = lowered.find(marker)
            if index == -1:
                continue
            fragment = lowered[index + len(marker) :]
            fragment = re.split(r"\b(?:in|for|during|from|to|compared|was|were|came|represented|allocated)\b", fragment, maxsplit=1)[0]
            terms = self._content_terms(fragment, keep_total=keep_total)
            if terms:
                return terms
        return []

    def _year_series(self, lowered: str, years: list[str]) -> list[str]:
        range_match = re.search(r"\b(20\d{2})\b\s*(?:through|to|-)\s*\b(20\d{2})\b", lowered)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if abs(start - end) <= 10:
                step = 1 if end >= start else -1
                return [str(year) for year in range(start, end + step, step)]
        seen = []
        for year in years:
            if year not in seen:
                seen.append(year)
        return seen

    def _product_terms(self, lowered: str) -> list[list[str]]:
        groups = []
        for phrase in ("average daily volume", "average price", "volume", "price"):
            if phrase in lowered:
                groups.append(self._content_terms(phrase))
        return groups

    def _content_terms(self, text: str, keep_total: bool = False) -> list[str]:
        stopwords = {
            "what",
            "was",
            "were",
            "the",
            "a",
            "an",
            "of",
            "in",
            "for",
            "from",
            "to",
            "by",
            "with",
            "and",
            "or",
            "percentage",
            "percent",
            "change",
            "increase",
            "decrease",
            "growth",
            "compared",
            "months",
            "month",
            "ended",
            "three",
            "six",
            "nine",
            "twelve",
        }
        if not keep_total:
            stopwords.add("total")
        return [
            token
            for token in re.findall(r"[a-z&]+", text.lower())
            if token not in stopwords and len(token) > 1
        ][:8]


class NumericPlanExecutor:
    def __init__(self) -> None:
        self.executor = TableOperationExecutor()

    def execute(self, query: str, contexts: list[tuple[str, str]], plan: dict[str, Any]) -> PlannedNumericAnswer | None:
        operation = str(plan.get("operation", "")).lower()
        node_id = str(plan.get("node_id") or "")
        context_text = self._context_text(node_id, contexts)
        if context_text is None:
            return None

        if operation in {"multiply", "multiplication"}:
            operation = "product"

        if operation == "lookup":
            target = self.executor.resolve_value(plan.get("target"), context_text, support_text=query)
            if target is None:
                return None
            return PlannedNumericAnswer(
                text=f"{target.value:g}",
                calculation=f"planned_lookup target={self._value_ref(target)}: {target.value:g}",
            )

        if operation in {"difference", "absolute_difference", "ratio", "percent_change"}:
            target = self.executor.resolve_value(plan.get("target"), context_text, support_text=query)
            base = self.executor.resolve_value(plan.get("base"), context_text, support_text=query)
            if target is None or base is None:
                return None
            if operation == "difference":
                result = self.executor.difference(target.value, base.value)
                return PlannedNumericAnswer(
                    text=f"{result.value:g}",
                    calculation=self._calculation(
                        "planned_difference",
                        result.expression,
                        target,
                        base,
                    ),
                )
            if operation == "absolute_difference":
                result = self.executor.difference(target.value, base.value)
                value = abs(result.value)
                return PlannedNumericAnswer(
                    text=f"{value:g}",
                    calculation=self._calculation(
                        "planned_absolute_difference",
                        f"abs({target.value:g} - {base.value:g}) = {value:g}",
                        target,
                        base,
                    ),
                )
            if operation == "ratio":
                result = self.executor.ratio(target.value, base.value)
                if result is None:
                    return None
                value = result.value * 100.0 if str(plan.get("scale")) == "percent" else result.value
                suffix = "%" if str(plan.get("scale")) == "percent" else ""
                return PlannedNumericAnswer(
                    text=self._format_number(value, suffix),
                    calculation=self._calculation(
                        "planned_ratio",
                        f"{target.value:g} / {base.value:g}{' * 100' if suffix else ''} = {value:.1f}{suffix}",
                        target,
                        base,
                    ),
                )
            result = self.executor.percent_change(target.value, base.value)
            if result is None:
                return None
            return PlannedNumericAnswer(
                text=f"{result.value:.1f}%",
                calculation=self._calculation(
                    "planned_percent_change",
                    result.expression,
                    target,
                    base,
                ),
            )

        if operation == "complement_percent":
            target = self.executor.resolve_value(plan.get("target"), context_text, support_text=query)
            if target is None:
                return None
            percent = 100.0 - target.value
            if percent < -0.05 or percent > 100.05:
                return None
            return PlannedNumericAnswer(
                text=self._format_number(percent, "%"),
                calculation=(
                    f"planned_complement_percent target={self._value_ref(target)}: "
                    f"100 - {target.value:g} = {percent:.1f}%"
                ),
            )

        if operation == "percent_of_increase":
            numerator_delta_value = self.executor.resolve_value(
                plan.get("numerator_delta"),
                context_text,
                support_text=query,
            )
            numerator_target = self.executor.resolve_value(plan.get("numerator_target"), context_text, support_text=query)
            numerator_base = self.executor.resolve_value(plan.get("numerator_base"), context_text, support_text=query)
            denominator_target = self.executor.resolve_value(
                plan.get("denominator_target"),
                context_text,
                support_text=query,
            )
            denominator_base = self.executor.resolve_value(plan.get("denominator_base"), context_text, support_text=query)
            if denominator_target is None or denominator_base is None:
                return None
            if numerator_delta_value is not None:
                numerator_delta = TableOperationResult(
                    "difference",
                    numerator_delta_value.value,
                    f"{numerator_delta_value.value:g}",
                )
                numerator_ref = self._value_ref(numerator_delta_value)
                numerator_expr = f"{numerator_delta_value.value:g}"
            else:
                if numerator_target is None or numerator_base is None:
                    return None
                numerator_delta = self.executor.difference(numerator_target.value, numerator_base.value)
                numerator_ref = f"{self._value_ref(numerator_target)}-{self._value_ref(numerator_base)}"
                numerator_expr = f"({numerator_target.value:g} - {numerator_base.value:g})"
            denominator_delta = self.executor.difference(denominator_target.value, denominator_base.value)
            ratio = self.executor.ratio(numerator_delta.value, denominator_delta.value)
            if ratio is None:
                return None
            percent = ratio.value * 100.0
            calculation = (
                "planned_percent_of_increase "
                f"numerator={numerator_ref} "
                f"denominator={self._value_ref(denominator_target)}-{self._value_ref(denominator_base)}: "
                f"{numerator_expr} / "
                f"({denominator_target.value:g} - {denominator_base.value:g}) * 100 = {percent:.1f}%"
            )
            return PlannedNumericAnswer(text=self._format_number(percent, "%"), calculation=calculation)

        if operation == "sum" and self._query_requires_ratio_like_operation(query):
            return None

        if operation in {"sum", "average", "product"}:
            resolved_values = [
                value
                for item in plan.get("values", [])
                if (value := self.executor.resolve_value(item, context_text, support_text=query)) is not None
            ]
            values = [
                value.value
                for value in resolved_values
            ]
            if not values:
                return None
            if operation == "sum":
                result = self.executor.sum(values)
            elif operation == "average":
                result = self.executor.average(values)
            else:
                result = self.executor.product(values)
            if result is None:
                return None
            return PlannedNumericAnswer(
                text=f"{result.value:g}",
                calculation=f"planned_{operation} values={self._value_refs(resolved_values)}: {result.expression}",
            )
        return None

    def _query_requires_ratio_like_operation(self, query: str) -> bool:
        lowered = query.lower()
        return bool(re.search(r"\b(?:percent|percentage|portion|share|ratio)\b", lowered))

    def _context_text(self, node_id: str, contexts: list[tuple[str, str]]) -> str | None:
        if node_id:
            for candidate_id, text in contexts:
                if candidate_id == node_id:
                    return text
        if len(contexts) == 1:
            return contexts[0][1]
        return None

    def _format_number(self, value: float, suffix: str = "") -> str:
        if abs(value - round(value)) < 0.05:
            return f"{round(value):.0f}{suffix}"
        return f"{value:.1f}{suffix}"

    def _calculation(self, operation: str, expression: str, target: Any, base: Any) -> str:
        target_ref = self._value_ref(target)
        base_ref = self._value_ref(base)
        return f"{operation} target={target_ref} base={base_ref}: {expression}"

    def _value_ref(self, value: Any) -> str:
        row = getattr(value, "row_label", "") or "value"
        column = getattr(value, "column_label", "")
        period = getattr(value, "period_label", "")
        if column and period:
            return f"{row}/{period}/{column}"
        if column:
            return f"{row}/{column}"
        return str(row)

    def _value_refs(self, values: list[Any]) -> str:
        return ", ".join(self._value_ref(value) for value in values)


class NumericPlannerFallback:
    def __init__(
        self,
        plan_client: NumericPlanClient,
        strict: bool = False,
        log_errors: bool = False,
        fallback_client: NumericPlanClient | None = None,
        disable_primary_after_error: bool = False,
    ) -> None:
        self.plan_client = plan_client
        self.executor = NumericPlanExecutor()
        self.strict = strict
        self.log_errors = log_errors
        self.fallback_client = fallback_client
        self.disable_primary_after_error = disable_primary_after_error
        self.primary_disabled = False

    @classmethod
    def from_config(cls, config: dict[str, Any] | None = None) -> NumericPlannerFallback | None:
        config = config or {}
        if not config.get("enabled", False):
            return None
        llm_config = dict(config.get("llm", {}))
        for source_key, target_key in [
            ("llm_provider", "provider"),
            ("llm_base_url", "base_url"),
            ("llm_api_key", "api_key"),
            ("llm_model", "model"),
            ("llm_timeout", "timeout"),
        ]:
            if source_key in config:
                llm_config[target_key] = config[source_key]
        fallback_client = HeuristicNumericPlanClient() if config.get("fallback_to_heuristic", False) else None
        provider = str(llm_config.get("provider") or "").lower()
        if provider in {"heuristic", "local", "program", "local_program"} or not config.get("primary_enabled", True):
            return cls(
                HeuristicNumericPlanClient(),
                strict=bool(config.get("strict", False)),
                log_errors=bool(config.get("log_errors", False)),
            )
        return cls(
            LLMNumericPlanClient(make_llm_client(llm_config)),
            strict=bool(config.get("strict", False)),
            log_errors=bool(config.get("log_errors", False)),
            fallback_client=fallback_client,
            disable_primary_after_error=bool(config.get("disable_primary_after_error", False)),
        )

    def answer(self, query: str, contexts: list[tuple[str, str]]) -> PlannedNumericAnswer | None:
        if self.primary_disabled and self.fallback_client is not None:
            plan = self.fallback_client.plan(query, contexts)
        else:
            try:
                plan = self.plan_client.plan(query, contexts)
            except Exception as exc:
                if self.log_errors:
                    print(f"[numeric_planner] planner request failed: {exc}", flush=True)
                if self.fallback_client is None:
                    if self.strict:
                        raise
                    return None
                if self.disable_primary_after_error:
                    self.primary_disabled = True
                plan = self.fallback_client.plan(query, contexts)
        answer = self.executor.execute(query, contexts, plan)
        if answer is None and self.log_errors:
            print(f"[numeric_planner] planner returned unverifiable plan: {plan}", flush=True)
        if answer is None and self.strict:
            raise RuntimeError(f"Numeric planner returned unverifiable plan: {plan}")
        return answer
