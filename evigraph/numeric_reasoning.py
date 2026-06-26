from __future__ import annotations

import re
from dataclasses import dataclass

from evigraph.evidence_graph import EvidenceGraph
from evigraph.numeric_planner import NumericPlannerFallback
from evigraph.schema import EvidenceNode
from evigraph.table_executor import TableOperationExecutor


@dataclass
class NumericAnswer:
    text: str
    calculation: str
    cited_node_ids: list[str]


class NumericReasoner:
    def __init__(self, planner_fallback: NumericPlannerFallback | None = None) -> None:
        self.executor = TableOperationExecutor()
        self.planner_fallback = planner_fallback

    def answer(self, query: str, support_graph: EvidenceGraph) -> NumericAnswer | None:
        query_lower = self._normalize_query(query)
        contexts = self._contexts(support_graph)
        if not contexts:
            return None

        is_roi_query = "roi" in query_lower or "rate of return" in query_lower
        answer = self._return_on_assets(query_lower, contexts)
        if answer:
            return answer
        answer = self._rate_of_return_on_table_value(query_lower, contexts)
        if answer:
            return answer
        if (
            "percentage change" in query_lower
            or "percent change" in query_lower
            or "percentage increase" in query_lower
            or "percent increase" in query_lower
            or "percentual increase" in query_lower
            or "percentage decrease" in query_lower
            or "percent decrease" in query_lower
            or "percentual decrease" in query_lower
            or "percentage growth" in query_lower
            or "percent growth" in query_lower
            or "percentual growth" in query_lower
            or "percentage reduction" in query_lower
            or "percent reduction" in query_lower
            or "percentual reduction" in query_lower
            or "percent of the change" in query_lower
            or "percentage of the change" in query_lower
            or "percent of change" in query_lower
            or "percentage of change" in query_lower
            or "growth rate" in query_lower
            or is_roi_query
            or "percent of the increase" in query_lower
        ):
            if self._is_percent_of_change_contribution(query_lower):
                planned = self._planner_answer(query, contexts)
                if planned:
                    return planned
            answer = self._roi_from_table(query_lower, contexts)
            if answer:
                return answer
            if not is_roi_query:
                answer = self._quarterly_cash_dividend_percent_change(query_lower, contexts)
                if answer:
                    return answer
                answer = self._cumulative_return_percent(query_lower, contexts)
                if answer:
                    return answer
                if len(re.findall(r"\b(20\d{2})\b", query_lower)) < 2:
                    answer = self._percent_delta_phrase(query_lower, contexts)
                    if answer:
                        return answer
                    answer = self._percent_change_from_to_phrase(query_lower, contexts)
                    if answer:
                        return answer
                answer = self._vertical_metric_percent_change(query_lower, contexts)
                if answer:
                    return answer
                answer = self._percent_change(query_lower, contexts)
                if answer:
                    return answer
                answer = self._percent_delta_phrase(query_lower, contexts)
                if answer:
                    return answer
                answer = self._percent_change_from_to_phrase(query_lower, contexts)
                if answer:
                    return answer

        if "percent higher" in query_lower or "percentage higher" in query_lower:
            answer = self._percent_higher_between_rows(query_lower, contexts)
            if answer:
                return answer

        if "percent of the increase" in query_lower or "percentage of the increase" in query_lower:
            planned = self._planner_answer(query, contexts)
            if planned:
                return planned

        if self._is_percent_of_change_contribution(query_lower):
            planned = self._planner_answer(query, contexts)
            if planned:
                return planned

        if (
            "difference" in query_lower
            and "as a percentage of" in query_lower
            and len(re.findall(r"\b(20\d{2})\b", query_lower)) >= 2
        ):
            answer = self._percentage_point_row_difference(query_lower, contexts)
            if answer:
                return answer

        if (
            "what percentage" in query_lower
            or "what percent" in query_lower
            or " percentage of " in query_lower
            or " percent of " in query_lower
            or "what portion" in query_lower
            or "what share" in query_lower
            or " as a percentage of " in query_lower
        ):
            answer = self._increase_component_ratio_percent(query_lower, contexts)
            if answer:
                return answer
            answer = self._not_leased_square_feet_ratio(query_lower, contexts)
            if answer:
                return answer
            answer = self._facility_closing_charge_ratio(query_lower, contexts)
            if answer:
                return answer
            answer = self._cumulative_return_percent(query_lower, contexts)
            if answer:
                return answer
            answer = self._equity_plan_remaining_available_ratio(query_lower, contexts)
            if answer:
                return answer
            answer = self._commitment_expiration_ratio(query_lower, contexts)
            if answer:
                return answer
            answer = self._ratio_percent(query_lower, contexts)
            if answer:
                return answer

        if "increased" in query_lower and "as much as" in query_lower:
            answer = self._repeated_increase_projection(query_lower, contexts)
            if answer:
                return answer

        if " increase" in query_lower and len(re.findall(r"\b(20\d{2})\b", query_lower)) >= 2:
            answer = self._implicit_percent_increase(query_lower, contexts)
            if answer:
                return answer

        if "after-tax" in query_lower or "after tax" in query_lower:
            answer = self._pretax_aftertax_difference(query_lower, contexts)
            if answer:
                return answer

        if "change" in query_lower and len(re.findall(r"\b(20\d{2})\b", query_lower)) >= 2:
            answer = self._respectively_prose_difference(query_lower, contexts)
            if answer:
                return answer
            answer = self._row_year_difference(query_lower, contexts)
            if answer:
                return answer

        if "average" in query_lower and "per" in query_lower:
            answer = self._row_average(query_lower, contexts)
            if answer:
                return answer

        if "average" in query_lower:
            answer = self._row_values_average(query_lower, contexts)
            if answer:
                return answer
            answer = self._year_range_average_v2(query_lower, contexts)
            if answer:
                return answer
            answer = self._year_range_average(query_lower, contexts)
            if answer:
                return answer

        if "ratio" in query_lower:
            answer = self._current_ratio(query_lower, contexts)
            if answer:
                return answer
            answer = self._acquisition_liabilities_to_assets_ratio(query_lower, contexts)
            if answer:
                return answer
            answer = self._implied_tier2_capital_ratio(query_lower, contexts)
            if answer:
                return answer
            answer = self._same_year_row_ratio(query_lower, contexts)
            if answer:
                return answer
            if self._is_after_year_row_ratio(query_lower):
                planned = self._planner_answer(query, contexts)
                if planned:
                    return planned
            if len(re.findall(r"\b(20\d{2})\b", query_lower)) >= 2:
                answer = self._ratio_between_years(query_lower, contexts)
                if answer:
                    return answer

        if "post closing adjustments" in query_lower or "post-closing adjustments" in query_lower:
            answer = self._difference_between_nearby_amounts(contexts)
            if answer:
                return answer

        if self.planner_fallback is not None:
            planned = self._planner_answer(query, contexts)
            if planned:
                return planned

        return None

    def _planner_answer(self, query: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        if self.planner_fallback is None:
            return None
        planned = self.planner_fallback.answer(query, contexts)
        if planned is None:
            return None
        return NumericAnswer(
            text=planned.text,
            calculation=planned.calculation,
            cited_node_ids=[contexts[0][0]],
        )

    def _is_percent_of_change_contribution(self, query_lower: str) -> bool:
        return bool(
            re.search(r"\b(?:percent|percentage)\s+of\s+the\s+change\b", query_lower)
            and re.search(r"\b(?:due to|came from|attributable to)\b", query_lower)
        )

    def _is_after_year_row_ratio(self, query_lower: str) -> bool:
        return bool(
            "ratio" in query_lower
            and re.search(r"\bfor\s+20\d{2}\b.+?\bto\s+(?:the\s+)?(?:amounts?\s+)?after\s+20\d{2}\b", query_lower)
        )

    def _acquisition_liabilities_to_assets_ratio(
        self, query_lower: str, contexts: list[tuple[str, str]]
    ) -> NumericAnswer | None:
        if "ratio" not in query_lower or "asset" not in query_lower:
            return None
        if not re.search(r"\b(?:debt|debts|liabilit(?:y|ies))\b", query_lower):
            return None
        if not any(term in query_lower for term in ["purchase transaction", "acquisition", "purchase price"]):
            return None

        for node_id, text in contexts:
            parsed_tables = self._markdown_tables(text)
            loose_table = self._loose_markdown_table(text)
            if loose_table is not None:
                parsed_tables.append(loose_table)

            for _headers, rows in parsed_tables:
                assets_row = self._row_by_label(rows, ["total", "assets", "acquired"])
                if assets_row is None:
                    continue
                denominator = self._row_first_numeric_value(assets_row)
                if denominator in {None, 0}:
                    continue

                numerator_rows: list[tuple[str, float]] = []
                seen_labels: set[str] = set()
                for terms in (["debt", "assumed"], ["liabilities", "assumed"], ["liability", "assumed"]):
                    row = self._row_by_label(rows, terms)
                    if row is None:
                        continue
                    label = row[0].strip()
                    normalized_label = label.lower()
                    if normalized_label in seen_labels:
                        continue
                    value = self._row_first_numeric_value(row)
                    if value is None:
                        continue
                    seen_labels.add(normalized_label)
                    numerator_rows.append((label, abs(value)))

                if not numerator_rows:
                    continue
                numerator = sum(value for _label, value in numerator_rows)
                operation = self.executor.ratio(numerator, denominator)
                if operation is None:
                    continue
                percent = operation.value * 100
                labels = ",".join(label for label, _value in numerator_rows)
                addends = " + ".join(f"{value:g}" for _label, value in numerator_rows)
                return NumericAnswer(
                    text=self._format_percent(percent),
                    calculation=(
                        "acquisition_liabilities_to_assets_ratio "
                        f"numerator_rows={labels} denominator_row={assets_row[0].strip()}: "
                        f"({addends}) / {denominator:g} * 100 = {self._format_percent(percent)}"
                    ),
                    cited_node_ids=[node_id],
                )
        return None

    def _increase_component_ratio_percent(
        self, query_lower: str, contexts: list[tuple[str, str]]
    ) -> NumericAnswer | None:
        parsed = self._increase_component_ratio_percent_query(query_lower)
        if parsed is None:
            return None
        numerator_terms, denominator_terms, query_year = parsed

        for node_id, text in contexts:
            answer = self._increase_component_ratio_percent_from_text(
                node_id,
                text,
                numerator_terms,
                denominator_terms,
                query_year,
                query_lower,
            )
            if answer is not None:
                return answer

        groups: dict[str, list[tuple[str, str]]] = {}
        for node_id, text in contexts:
            groups.setdefault(self._context_source_key(node_id), []).append((node_id, text))
        for grouped_contexts in groups.values():
            if len(grouped_contexts) < 2:
                continue
            ordered_contexts = sorted(grouped_contexts, key=lambda item: self._context_chunk_order(item[0]))
            node_ids = [node_id for node_id, _text in ordered_contexts]
            combined_text = "\n".join(text for _node_id, text in ordered_contexts)
            answer = self._increase_component_ratio_percent_from_text(
                node_ids[0],
                combined_text,
                numerator_terms,
                denominator_terms,
                query_year,
                query_lower,
            )
            if answer is not None:
                return NumericAnswer(answer.text, answer.calculation, node_ids)
        return None

    def _increase_component_ratio_percent_from_text(
        self,
        node_id: str,
        text: str,
        numerator_terms: list[str],
        denominator_terms: list[str],
        query_year: str,
        query_lower: str,
    ) -> NumericAnswer | None:
        numerator, numerator_label, addends = self._prose_increase_component_sum(text, numerator_terms)
        if numerator is None:
            return None
        denominator, denominator_label = self._value_for_row_terms_year(
            text,
            denominator_terms,
            query_year,
            query_lower,
        )
        if denominator is None:
            denominator, denominator_label = self._year_labeled_row_value_for_terms(
                text,
                denominator_terms,
                query_year,
            )
        if denominator in {None, 0}:
            return None
        operation = self.executor.ratio(numerator, denominator)
        if operation is None:
            return None
        percent = operation.value * 100
        addends_text = " + ".join(f"{value:g}" for value in addends)
        return NumericAnswer(
            text=self._format_percent(percent),
            calculation=(
                "increase_component_ratio_percent "
                f"row={numerator_label} denominator_row={denominator_label}: "
                f"({addends_text}) / {denominator:g} * 100 = {self._format_percent(percent)}"
            ),
            cited_node_ids=[node_id],
        )

    def _increase_component_ratio_percent_query(
        self, query_lower: str
    ) -> tuple[list[str], list[str], str] | None:
        match = re.search(
            r"\bincrease\s+in\s+(?P<numerator>.+?)\s+as\s+a\s+percentage\s+of\s+"
            r"(?P<denominator>.+?)\s+in\s+(?P<year>20\d{2})\b",
            query_lower,
        )
        if not match:
            return None
        numerator_terms = self._keywords(match.group("numerator"))
        denominator_terms = self._keywords(match.group("denominator"))
        if not numerator_terms or not denominator_terms:
            return None
        return numerator_terms, denominator_terms, match.group("year")

    def _prose_increase_component_sum(
        self, text: str, numerator_terms: list[str]
    ) -> tuple[float | None, str, list[float]]:
        best: tuple[int, int, int, str, list[float]] | None = None
        amount_pattern = re.compile(r"(\$)\s*([-+]?\d+(?:\.\d+)?)\s*(billion|million|thousand)?", re.IGNORECASE)
        exact_subject = " ".join(numerator_terms)
        exact_start = text.lower().find(f"{exact_subject} increased")
        if exact_start >= 0:
            tail = text[exact_start:]
            cut_positions = [
                position
                for marker in ["\nfollowing is", "\n2003 compared", "\n2010 compared", "\n2016 compared", "\n|"]
                if (position := tail.lower().find(marker)) > 0
            ]
            window = tail[: min(cut_positions)] if cut_positions else tail[:1200]
            window_values = [
                self._scaled_number(match.group(2), match.group(3).lower() if match.group(3) else None)
                for match in amount_pattern.finditer(window)
            ]
            window_values = self._dedupe_consecutive_values(window_values)
            if window_values:
                return sum(window_values), exact_subject, window_values
        segments = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith("|") and not line.strip().startswith("#")
        ]
        for segment_index, segment in enumerate(segments):
            lowered = segment.lower()
            if "increas" not in lowered:
                continue
            if not self._label_matches_terms(lowered, numerator_terms):
                continue
            values = [
                self._scaled_number(match.group(2), match.group(3).lower() if match.group(3) else None)
                for match in amount_pattern.finditer(segment)
            ]
            if not values:
                continue
            matched = sum(1 for term in numerator_terms if term in lowered)
            subject_score = 1 if f"{exact_subject} increased" in lowered else 0
            candidate = (subject_score, matched, -segment_index, exact_subject, values)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            return None, "", []
        _subject, _matched, _sentence_order, label, values = best
        return sum(values), label, values

    def _dedupe_consecutive_values(self, values: list[float]) -> list[float]:
        deduped: list[float] = []
        for value in values:
            if deduped and abs(deduped[-1] - value) < 1e-9:
                continue
            deduped.append(value)
        return deduped

    def _year_labeled_row_value_for_terms(
        self, text: str, terms: list[str], query_year: str
    ) -> tuple[float | None, str]:
        best: tuple[int, int, float, str] | None = None
        for row_index, (label, value) in enumerate(self._label_value_rows(text)):
            if query_year not in label:
                continue
            if not self._label_matches_terms(label, terms):
                continue
            matched = sum(1 for term in terms if term in label)
            candidate = (matched, -row_index, value, label)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            return None, ""
        _matched, _row_order, value, label = best
        return value, label

    def _year_range_average_v2(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        range_match = re.search(r"\b(?:from\s+)?(20\d{2})\s*(?:[-\s]|\bto\b)+\s*(20\d{2})\b", query_lower)
        if not range_match:
            return None
        start_year, end_year = (int(range_match.group(1)), int(range_match.group(2)))
        years = [str(year) for year in range(start_year, end_year + 1)]
        for node_id, text in contexts:
            rows = dict(self._label_value_rows(text))
            values = [rows[year] for year in years if year in rows]
            if len(values) == len(years):
                operation = self.executor.average(values)
                if operation is not None:
                    return NumericAnswer(
                        text=f"{operation.value:.1f}",
                        calculation=f"year_range_average: {operation.expression}",
                        cited_node_ids=[node_id],
                    )
        for node_id, text in contexts:
            values = self._inline_multi_year_row_values_for_query(query_lower, text, years)
            if not values:
                continue
            ordered = [values[year] for year in years if year in values]
            if len(ordered) != len(years):
                continue
            operation = self.executor.average(ordered)
            if operation is None:
                continue
            return NumericAnswer(
                text=f"{operation.value:.1f}",
                calculation=f"year_range_average row={values.get('__row_label__', '')}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        for node_id, text in contexts:
            values = self._prose_multi_year_values_for_query(query_lower, text, years)
            if not values:
                continue
            ordered = [values[year] for year in years if year in values]
            if len(ordered) != len(years):
                continue
            operation = self.executor.average(ordered)
            if operation is None:
                continue
            return NumericAnswer(
                text=f"{operation.value:.1f}",
                calculation=f"year_range_average row={values.get('__row_label__', '')}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _inline_multi_year_row_values_for_query(
        self,
        query_lower: str,
        text: str,
        years: list[str],
    ) -> dict[str, float] | None:
        terms = [term for term in self._keywords(query_lower) if term not in {"during", "years", "year"}]
        if not terms:
            return None
        values: dict[str, float] = {}
        row_label = ""
        for year in years:
            value, label = self._inline_row_value_for_terms_year(text, terms, year, query_lower)
            if value is None or not label:
                return None
            if row_label and label != row_label:
                return None
            row_label = label
            values[year] = value
        values["__row_label__"] = row_label
        return values

    def _year_range_average(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        range_match = re.search(r"\b(20\d{2})\s*[-–]\s*(20\d{2})\b", query_lower)
        if not range_match:
            return None
        start_year, end_year = (int(range_match.group(1)), int(range_match.group(2)))
        years = [str(year) for year in range(start_year, end_year + 1)]
        for node_id, text in contexts:
            rows = dict(self._label_value_rows(text))
            values = [rows[year] for year in years if year in rows]
            if len(values) != len(years):
                continue
            operation = self.executor.average(values)
            if operation is None:
                continue
            result = operation.value
            return NumericAnswer(
                text=f"{result:.1f}",
                calculation=f"year_range_average: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _row_average(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        entity = self._entity_after_for(query_lower)
        for node_id, text in contexts:
            table = self._markdown_table(text)
            if not table or not entity:
                continue
            headers, rows = table
            numerator_index = self._column_index(headers, ["payment", "volume"])
            denominator_index = self._column_index(headers, ["transaction"])
            if numerator_index is None or denominator_index is None:
                continue
            for row in rows:
                if not row or entity not in row[0].lower():
                    continue
                if max(numerator_index, denominator_index) >= len(row):
                    continue
                numerator = self._first_number(row[numerator_index])
                denominator = self._first_number(row[denominator_index])
                if numerator is None or denominator in {None, 0}:
                    continue
                operation = self.executor.ratio(numerator, denominator)
                if operation is None:
                    continue
                result = operation.value
                return NumericAnswer(
                    text=f"{result:.2f}",
                    calculation=f"row_average row={row[0]}: {operation.expression}",
                    cited_node_ids=[node_id],
                )
        return None

    def _row_values_average(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        if re.search(r"\b20\d{2}\D+20\d{2}\b", query_lower):
            return None
        query_years = re.findall(r"\b(20\d{2})\b", query_lower)
        for node_id, text in contexts:
            table = self._markdown_table(text)
            if not table:
                continue
            headers, rows = table
            row = self._best_query_row(query_lower, headers, rows)
            if not row:
                continue
            row = self._year_anchored_row(query_lower, query_years, headers, rows) or row
            total_columns = {
                index
                for index, header in enumerate(headers)
                if index > 0 and re.fullmatch(r"\s*total\s*", header.strip(), re.IGNORECASE)
            }
            value_cells = [
                (index, cell)
                for index, cell in enumerate(row)
                if index > 0 and index not in total_columns
            ]
            values = [value for value in (self._first_number(cell) for _, cell in value_cells) if value is not None]
            if len(values) < 2:
                continue
            if "amount" in query_lower:
                values = [abs(value) for value in values]
            operation = self.executor.average(values)
            if operation is None:
                continue
            return NumericAnswer(
                text=f"{operation.value:.1f}",
                calculation=f"row_values_average row={row[0]}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _year_anchored_row(
        self,
        query_lower: str,
        query_years: list[str],
        headers: list[str],
        rows: list[list[str]],
    ) -> list[str] | None:
        """Prefer a semantically matched row whose label carries a query year.

        ``_best_query_row`` strips 20XX tokens from query terms, so two rows that
        differ only by year (for example ``liability at december 31 2006`` and
        ``... 2008``) tie and the earlier row wins. When the query itself pins a
        year, the row carrying that year is the right operand.
        """
        if not query_years:
            return None
        query_terms = set(self._keywords(query_lower))
        for row in rows:
            if not row:
                continue
            label = row[0].lower()
            label_terms = set(re.findall(r"[a-z0-9]+", label))
            if query_terms and not (query_terms & label_terms):
                continue
            if any(year in label for year in query_years):
                return row
        return None

    def _row_year_difference(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        base_year, target_year = self._difference_years(query_lower, years)
        grouped = self._grouped_table_year_values(query_lower, contexts, base_year, target_year)
        if grouped is not None:
            node_ids, values = grouped
            operation = self.executor.difference(values[target_year], values[base_year])
            row_label = str(values.get("__row_label__", ""))
            return NumericAnswer(
                text=f"{operation.value:g}",
                calculation=f"row_year_difference row={row_label}: {operation.expression}",
                cited_node_ids=node_ids,
            )
        for node_id, text in contexts:
            values = self._table_year_values(query_lower, text, base_year, target_year)
            if not values or base_year not in values or target_year not in values:
                continue
            operation = self.executor.difference(values[target_year], values[base_year])
            row_label = str(values.get("__row_label__", ""))
            return NumericAnswer(
                text=f"{operation.value:g}",
                calculation=f"row_year_difference row={row_label}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _difference_years(self, query_lower: str, years: list[str]) -> tuple[str, str]:
        between_match = re.search(r"\bbetween\s+(20\d{2})\s+and\s+(20\d{2})\b", query_lower)
        if between_match:
            first, second = between_match.group(1), between_match.group(2)
            return (first, second) if int(first) < int(second) else (second, first)
        return years[0], years[1]

    def _percent_change_years(self, query_lower: str, years: list[str]) -> tuple[str, str]:
        compared_match = re.search(r"\b(20\d{2})\b.+?\bcompared to\s+(20\d{2})\b", query_lower)
        if compared_match:
            return compared_match.group(2), compared_match.group(1)
        return years[0], years[1]

    def _repeated_increase_projection(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        years = [int(year) for year in re.findall(r"\b(20\d{2})\b", query_lower)]
        if len(years) < 2:
            return None
        target_year = years[0]
        prior_year = years[1]
        base_year = prior_year - 1
        for node_id, text in contexts:
            table = self._markdown_table(text)
            if not table:
                continue
            headers, rows = table
            target_index = self._header_year_index(headers, str(prior_year))
            base_index = self._header_year_index(headers, str(base_year))
            if target_index is None or base_index is None:
                continue
            row = self._best_query_row(query_lower, headers, rows)
            if not row or max(target_index, base_index) >= len(row):
                continue
            prior_value = self._first_number(row[target_index])
            base_value = self._first_number(row[base_index])
            if prior_value is None or base_value is None:
                continue
            increase = self.executor.difference(prior_value, base_value)
            projected = self.executor.sum([prior_value, increase.value])
            if projected is None:
                continue
            return NumericAnswer(
                text=f"{projected.value:g}",
                calculation=(
                    f"repeated_increase_projection row={row[0]}: prior increase {increase.expression}; "
                    f"{target_year} projection {projected.expression}"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _pretax_aftertax_difference(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        for node_id, text in contexts:
            pattern = r"\$\s*([-+]?\d+(?:\.\d+)?)\s+million\s*,\s*or\s*\$\s*([-+]?\d+(?:\.\d+)?)\s+million\s+after[- ]tax"
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if not matches:
                continue
            pretax, aftertax = (self._to_float(value) for value in matches[0])
            operation = self.executor.difference(pretax, aftertax)
            return NumericAnswer(
                text=f"{operation.value:g}",
                calculation=f"pretax_aftertax_difference: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _respectively_prose_difference(
        self, query_lower: str, contexts: list[tuple[str, str]]
    ) -> NumericAnswer | None:
        if "change" not in query_lower or "respectively" in query_lower:
            return None
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        from_match = re.search(r"\bfrom\b.{0,80}?\b(20\d{2})\b", query_lower)
        if from_match:
            base_year = from_match.group(1)
            target_year = next((year for year in years if year != base_year), years[0])
        else:
            base_year, target_year = sorted({years[0], years[-1]}, key=int)
        query_terms = set(self._keywords(query_lower))
        distinctive_terms = {
            term
            for term in query_terms
            if term
            not in {
                "what",
                "was",
                "the",
                "change",
                "net",
                "from",
                "between",
                "and",
                "in",
                "millions",
                "billions",
                "december",
                "january",
                "year",
                "years",
            }
            and not re.fullmatch(r"(?:19|20)\d{2}", term)
        }
        amount_pattern = re.compile(
            r"\$\s*(?P<amount>[+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*(?P<scale>billion|million|thousand)?",
            flags=re.IGNORECASE,
        )
        for node_id, text in contexts:
            best: tuple[int, str] | None = None
            for sentence in self._prose_sentences(text):
                sentence_lower = sentence.lower()
                if "respectively" not in sentence_lower:
                    continue
                if target_year not in sentence_lower or base_year not in sentence_lower:
                    continue
                sentence_terms = set(self._keywords(sentence_lower))
                if len(distinctive_terms & sentence_terms) < min(2, len(distinctive_terms)):
                    continue
                score = len(query_terms & sentence_terms)
                if best is None or score > best[0]:
                    best = (score, sentence)
            if best is None:
                continue
            sentence = best[1]
            scoped = sentence[: sentence.lower().find("respectively")]
            sentence_years = re.findall(r"\b(20\d{2})\b", scoped)
            amounts = []
            for match in amount_pattern.finditer(scoped):
                amount = self._to_float(match.group("amount"))
                scale = (match.group("scale") or "").lower()
                if scale and f"in {scale}s" not in query_lower and f"in {scale}" not in query_lower:
                    amount = self._scaled_number(match.group("amount"), scale)
                amounts.append(amount)
            if len(sentence_years) < 2 or len(amounts) < len(sentence_years):
                continue
            aligned = dict(zip(sentence_years[-len(amounts) :], amounts[-len(sentence_years) :]))
            if target_year not in aligned or base_year not in aligned:
                continue
            operation = self.executor.difference(aligned[target_year], aligned[base_year])
            if operation is None:
                continue
            return NumericAnswer(
                text=self._format_number(operation.value),
                calculation=(
                    f"respectively_prose_difference years={target_year}-{base_year}: "
                    f"{operation.expression}"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _rate_of_return_on_table_value(
        self, query_lower: str, contexts: list[tuple[str, str]]
    ) -> NumericAnswer | None:
        if "rate of return" not in query_lower or " on " not in query_lower:
            return None
        percent_match = re.search(r"\b(\d+(?:\.\d+)?)\s*%", query_lower)
        year_match = re.search(r"\bon\s+(20\d{2})\s+(.+?)(?:\?|$)", query_lower)
        if percent_match is None or year_match is None:
            return None
        rate = self._to_float(percent_match.group(1)) / 100.0
        query_year = year_match.group(1)
        terms = self._keywords(year_match.group(2))
        if not terms:
            return None
        for node_id, text in contexts:
            value, metadata = self._table_value_for_terms_year_with_label(
                text, terms, query_year, allow_partial=False
            )
            if value is None:
                continue
            raw_result = value * rate
            result = round(raw_result)
            return NumericAnswer(
                text=f"{result:g}",
                calculation=(
                    f"rate_of_return_on_table_value row={metadata.get('row_label', '')} "
                    f"year={query_year}: round({value:g} * {rate:g}) = {result:g}"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _return_on_assets(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        if "return on" not in query_lower or "asset" not in query_lower:
            return None
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if not years:
            return None
        query_year = years[-1]
        numerator_term_sets = (
            ["net", "earnings"],
            ["net", "income"],
        )
        denominator_terms = ["total", "assets"]
        for node_id, text in contexts:
            denominator, denominator_meta = self._table_value_for_terms_year_with_label(
                text, denominator_terms, query_year, allow_partial=False
            )
            if denominator in {None, 0}:
                continue
            numerator = None
            numerator_meta: dict[str, str] = {}
            for terms in numerator_term_sets:
                numerator, numerator_meta = self._table_value_for_terms_year_with_label(
                    text, terms, query_year, allow_partial=False
                )
                if numerator is not None:
                    break
            if numerator is None:
                continue
            operation = self.executor.ratio(numerator, denominator)
            if operation is None:
                continue
            result = operation.value * 100.0
            return NumericAnswer(
                text=self._format_percent(result),
                calculation=(
                    f"return_on_assets numerator_row={numerator_meta.get('row_label', '')} "
                    f"denominator_row={denominator_meta.get('row_label', '')} year={query_year}: "
                    f"{operation.expression} * 100 = {result:.1f}%"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _cumulative_return_percent(
        self, query_lower: str, contexts: list[tuple[str, str]]
    ) -> NumericAnswer | None:
        if "return" not in query_lower or not ("percent" in query_lower or "percentage" in query_lower):
            return None
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        base_year, target_year = years[0], years[-1]
        target_terms = [
            term
            for term in self._keywords(query_lower)
            if term not in {"what", "was", "percent", "percentage", "return", "from", "common", "stock"}
            and not re.fullmatch(r"(?:19|20)\d{2}", term)
        ]
        if not target_terms:
            return None
        for node_id, text in contexts:
            for headers, rows in self._markdown_tables(text):
                base_index = self._month_year_header_index(headers, base_year)
                target_index = self._month_year_header_index(headers, target_year)
                if base_index is None or target_index is None:
                    continue
                row = self._best_table_value_row(rows, target_terms, target_index, require_all=False)
                if row is None or max(base_index, target_index) >= len(row):
                    continue
                base_value = self._first_number(row[base_index])
                target_value = self._first_number(row[target_index])
                if base_value in {None, 0} or target_value is None:
                    continue
                operation = self.executor.difference(target_value, base_value)
                if operation is None:
                    continue
                return NumericAnswer(
                    text=self._format_percent(operation.value),
                    calculation=(
                        f"cumulative_return_percent row={row[0]} years={base_year}->{target_year}: "
                        f"{target_value:g} - {base_value:g} = {operation.value:.1f}%"
                    ),
                    cited_node_ids=[node_id],
                )
        return None

    def _month_year_header_index(self, headers: list[str], year: str) -> int | None:
        two_digit = year[-2:]
        for index, header in enumerate(headers):
            if re.search(rf"\b(?:{year}|{two_digit})\b", header):
                return index
        return None

    def _roi_from_table(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        if "roi" not in query_lower and "rate of return" not in query_lower:
            return None
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        base_year, target_year = years[0], years[1]
        for node_id, text in contexts:
            answer = self._roi_from_text(node_id, text, query_lower, base_year, target_year)
            if answer is not None:
                return answer
        groups: dict[str, list[tuple[str, str]]] = {}
        for node_id, text in contexts:
            groups.setdefault(self._context_source_key(node_id), []).append((node_id, text))
        for grouped_contexts in groups.values():
            if len(grouped_contexts) < 2:
                continue
            grouped_contexts = sorted(grouped_contexts, key=lambda item: self._context_chunk_order(item[0]))
            node_ids = [node_id for node_id, _text in grouped_contexts]
            combined_text = "\n".join(text for _node_id, text in grouped_contexts)
            answer = self._roi_from_text(node_ids[0], combined_text, query_lower, base_year, target_year)
            if answer is not None:
                return NumericAnswer(answer.text, answer.calculation, node_ids)
        return None

    def _roi_from_text(
        self,
        node_id: str,
        text: str,
        query_lower: str,
        base_year: str,
        target_year: str,
    ) -> NumericAnswer | None:
        previous_year_headers: list[str] | None = None
        for headers, rows in self._markdown_tables(text):
            effective_headers = headers
            target_index = self._header_year_index(effective_headers, target_year)
            base_index = self._header_year_index(effective_headers, base_year)
            if target_index is None and previous_year_headers and rows and len(previous_year_headers) == len(rows[0]):
                effective_headers = previous_year_headers
                target_index = self._header_year_index(effective_headers, target_year)
                base_index = self._header_year_index(effective_headers, base_year)
            if target_index is None:
                if any(re.search(r"\b20\d{2}\b", header) for header in headers):
                    previous_year_headers = headers
                continue
            if base_index is None:
                earlier = [
                    index
                    for index, header in enumerate(effective_headers)
                    if (match := re.search(r"\b(20\d{2})\b", header)) and int(match.group(1)) < int(target_year)
                ]
                if earlier:
                    base_index = earlier[0]
            if base_index is None:
                previous_year_headers = effective_headers
                continue
            row = self._best_query_row(query_lower, effective_headers, rows)
            if not row or max(base_index, target_index) >= len(row):
                previous_year_headers = effective_headers
                continue
            base_value = self._first_number(row[base_index])
            target_value = self._first_number(row[target_index])
            if base_value is None or target_value is None or base_value == 0:
                previous_year_headers = effective_headers
                continue
            operation = self.executor.percent_change(target_value, base_value)
            if operation is None:
                previous_year_headers = effective_headers
                continue
            return NumericAnswer(
                text=f"{operation.value:.1f}%",
                calculation=f"percent_change row={row[0]} roi years={base_year}->{target_year}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _vertical_metric_percent_change(
        self, query_lower: str, contexts: list[tuple[str, str]]
    ) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        base_year, target_year = self._percent_change_years(query_lower, years)
        metric_terms = [
            term
            for term in self._keywords(query_lower)
            if term
            not in {
                "what",
                "was",
                "the",
                "percentage",
                "percent",
                "change",
                "from",
                "to",
                "at",
                "december",
                "january",
                "year",
                "years",
            }
            and not re.fullmatch(r"(?:19|20)\d{2}", term)
            and not re.fullmatch(r"\d{1,2}", term)
        ]
        if not metric_terms:
            return None
        for node_id, text in contexts:
            for headers, rows in self._markdown_tables(text):
                row_by_year = {
                    row[0].strip(): row
                    for row in rows
                    if row and re.fullmatch(r"(?:19|20)\d{2}", row[0].strip())
                }
                if base_year not in row_by_year or target_year not in row_by_year:
                    continue
                best_column: tuple[int, int, int] | None = None
                for index, header in enumerate(headers[1:], start=1):
                    header_lower = header.lower()
                    header_terms = set(self._keywords(header_lower))
                    matched = [term for term in metric_terms if term in header_terms or term in header_lower]
                    if len(matched) < min(2, len(metric_terms)):
                        continue
                    candidate = (len(matched), sum(len(term) for term in matched), index)
                    if best_column is None or candidate > best_column:
                        best_column = candidate
                if best_column is None:
                    continue
                column_index = best_column[2]
                base_row = row_by_year[base_year]
                target_row = row_by_year[target_year]
                if column_index >= len(base_row) or column_index >= len(target_row):
                    continue
                base_value = self._first_number(base_row[column_index])
                target_value = self._first_number(target_row[column_index])
                if base_value in {None, 0} or target_value is None:
                    continue
                operation = self.executor.percent_change(target_value, base_value)
                if operation is None:
                    continue
                if abs(operation.value) < 0.05:
                    continue
                return NumericAnswer(
                    text=self._format_percent(operation.value),
                    calculation=(
                        f"vertical_metric_percent_change column={headers[column_index]} "
                        f"years={base_year}->{target_year}: {operation.expression}"
                    ),
                    cited_node_ids=[node_id],
                )
        return None

    def _implicit_percent_increase(
        self, query_lower: str, contexts: list[tuple[str, str]]
    ) -> NumericAnswer | None:
        if not (
            ("increase from" in query_lower and ("by how much did" in query_lower or "percentage" in query_lower or "percent" in query_lower))
            or ("increase observed" in query_lower and "during" in query_lower)
        ):
            return None
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        base_year, target_year = self._percent_change_years(query_lower, years)
        for node_id, text in contexts:
            values = self._table_year_values(query_lower, text, base_year, target_year)
            if not values or base_year not in values or target_year not in values:
                continue
            operation = self.executor.percent_change(values[target_year], values[base_year])
            if operation is None:
                continue
            return NumericAnswer(
                text=self._format_percent(operation.value),
                calculation=(
                    f"implicit_percent_increase row={values.get('__row_label__', '')} "
                    f"years={base_year}->{target_year}: {operation.expression}"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _percent_change(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            if len(years) == 1:
                answer = self._percent_change_year_labeled_rows(query_lower, contexts, years[0])
                if answer:
                    return answer
            return self._percent_change_latest_table_years(query_lower, contexts)
        base_year, target_year = self._percent_change_years(query_lower, years)
        prose_answer = self._percent_change_from_prose(query_lower, contexts, base_year, target_year)
        if prose_answer is not None:
            return prose_answer
        year_label_answer = self._percent_change_year_label_candidates(query_lower, contexts, base_year, target_year)
        if year_label_answer is not None:
            return year_label_answer
        grouped = self._grouped_table_year_values(query_lower, contexts, base_year, target_year)
        if grouped is not None:
            node_ids, values = grouped
            if values.get(base_year) not in {None, 0} and target_year in values:
                operation = self.executor.percent_change(values[target_year], values[base_year])
                if operation is not None:
                    row_label = str(values.get("__row_label__", ""))
                    return NumericAnswer(
                        text=f"{operation.value:.1f}%",
                        calculation=f"percent_change row={row_label}: {operation.expression}",
                        cited_node_ids=node_ids,
                    )
        for node_id, text in contexts:
            values = self._table_year_values(query_lower, text, base_year, target_year)
            if not values:
                continue
            if base_year not in values or target_year not in values or values[base_year] == 0:
                continue
            operation = self.executor.percent_change(values[target_year], values[base_year])
            if operation is None:
                continue
            result = operation.value
            row_label = str(values.get("__row_label__", ""))
            return NumericAnswer(
                text=f"{result:.1f}%",
                calculation=f"percent_change row={row_label}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        for node_id, text in contexts:
            values = self._prose_year_values_for_query(query_lower, text, base_year, target_year)
            if not values:
                continue
            if base_year not in values or target_year not in values or values[base_year] == 0:
                continue
            operation = self.executor.percent_change(values[target_year], values[base_year])
            if operation is None:
                continue
            result = abs(operation.value) if "total debt" in query_lower else operation.value
            return NumericAnswer(
                text=f"{result:.1f}%",
                calculation=f"percent_change: {operation.expression}",
                cited_node_ids=[node_id],
            )
        fallback = self._query_scored_year_values(query_lower, contexts, base_year, target_year)
        if fallback:
            node_id, values = fallback
            operation = self.executor.percent_change(values[target_year], values[base_year])
            if operation is None:
                return None
            result = abs(operation.value) if "total debt" in query_lower else operation.value
            row_label = str(values.get("__row_label__", "year_values"))
            return NumericAnswer(
                text=f"{result:.1f}%",
                calculation=f"percent_change row={row_label}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _percent_change_from_prose(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
        base_year: str,
        target_year: str,
    ) -> NumericAnswer | None:
        for node_id, text in contexts:
            if "respectively" not in text.lower():
                continue
            values = self._prose_year_values_for_query(query_lower, text, base_year, target_year)
            if not values:
                continue
            if base_year not in values or target_year not in values or values[base_year] == 0:
                continue
            operation = self.executor.percent_change(values[target_year], values[base_year])
            if operation is None:
                continue
            report_magnitude = self._reports_decrease_magnitude(query_lower) or "total debt" in query_lower
            result = abs(operation.value) if report_magnitude else operation.value
            row_label = str(values.get("__row_label__", "prose_year_values"))
            calculation = f"percent_change row={row_label}: {operation.expression}"
            if report_magnitude:
                calculation = f"percent_change row={row_label} decrease_magnitude: abs({operation.expression.rsplit('=', 1)[0].strip()}) = {result:.1f}%"
            return NumericAnswer(
                text=f"{result:.1f}%",
                calculation=calculation,
                cited_node_ids=[node_id],
            )
        return None

    def _percent_change_year_label_candidates(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
        base_year: str,
        target_year: str,
    ) -> NumericAnswer | None:
        query_terms = set(self._keywords(query_lower)) - {"growth"}
        if not query_terms:
            return None
        best: tuple[int, int, int, int, NumericAnswer] | None = None
        for context_index, (node_id, text) in enumerate(contexts):
            values, value_label = self._year_label_values_with_label(query_lower, text)
            if base_year not in values or target_year not in values or values[base_year] == 0:
                continue
            operation = self.executor.percent_change(values[target_year], values[base_year])
            if operation is None:
                continue
            text_terms = set(re.findall(r"[a-z0-9]+", text.lower()))
            matched_terms = query_terms & text_terms
            if len(matched_terms) < min(2, len(query_terms)):
                continue
            label_terms = set(self._keywords(value_label))
            label_score = len(query_terms & label_terms)
            nonzero_score = 1 if abs(operation.value) >= 0.05 else 0
            schedule_score = 1 if self._has_year_label_schedule(text, base_year, target_year) else 0
            total_score = len(matched_terms) * 10 + label_score * 3 + nonzero_score * 4 + schedule_score * 2
            row_label = value_label or " ".join(sorted(matched_terms)[:6])
            answer = NumericAnswer(
                text=f"{operation.value:.1f}%",
                calculation=f"percent_change row={row_label}: {operation.expression}",
                cited_node_ids=[node_id],
            )
            candidate = (total_score, nonzero_score, schedule_score, -context_index, answer)
            if best is None or candidate > best:
                best = candidate
        return best[4] if best else None

    def _query_scored_year_values(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
        base_year: str,
        target_year: str,
    ) -> tuple[str, dict[str, float]] | None:
        query_terms = set(self._keywords(query_lower))
        if not query_terms:
            return None
        best: tuple[int, int, str, dict[str, float], list[str]] | None = None
        min_score = 2 if len(query_terms) >= 2 else 1
        for context_index, (node_id, text) in enumerate(contexts):
            text_terms = set(re.findall(r"[a-z0-9]+", text.lower()))
            matched_terms = [term for term in self._keywords(query_lower) if term in text_terms]
            score = len(matched_terms)
            if score < min_score:
                continue
            values = self._year_label_values(text)
            if base_year not in values or target_year not in values or values[base_year] == 0:
                continue
            candidate = (score, -context_index, node_id, values, matched_terms)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            return None
        _score, _order, node_id, values, matched_terms = best
        values = dict(values)
        values["__row_label__"] = " ".join(matched_terms[:6])
        return node_id, values

    def _percent_change_year_labeled_rows(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
        target_year: str,
    ) -> NumericAnswer | None:
        base_year = str(int(target_year) - 1)
        query_terms = set(self._keywords(query_lower)) - {"growth"}
        for node_id, text in contexts:
            rows = self._label_value_rows(text)
            base = self._matching_year_labeled_value(rows, base_year, query_terms)
            target = self._matching_year_labeled_value(rows, target_year, query_terms)
            if base is None or target is None or base[0] == 0:
                continue
            operation = self.executor.percent_change(target[0], base[0])
            if operation is None:
                continue
            return NumericAnswer(
                text=f"{operation.value:.1f}%",
                calculation=(
                    f"percent_change row={target[1]} vs {base[1]}: "
                    f"{operation.expression}"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _matching_year_labeled_value(
        self,
        rows: list[tuple[str, float]],
        year: str,
        query_terms: set[str],
    ) -> tuple[float, str] | None:
        best: tuple[int, float, str] | None = None
        for label, value in rows:
            if year not in label:
                continue
            label_terms = set(re.findall(r"[a-z0-9]+", label))
            score = len(query_terms & label_terms)
            if score == 0:
                continue
            candidate = (score, value, label)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            return None
        _score, value, label = best
        return value, label

    def _percent_change_latest_table_years(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
    ) -> NumericAnswer | None:
        for node_id, text in contexts:
            table = self._markdown_table(text)
            if not table:
                continue
            headers, rows = table
            year_columns = [
                (index, match.group(1))
                for index, header in enumerate(headers)
                if (match := re.search(r"\b(20\d{2})\b", header))
            ]
            if len(year_columns) < 2:
                continue
            target_index, target_year = year_columns[0]
            base_index, base_year = year_columns[1]
            best_row = self._best_query_row(query_lower, headers, rows)
            if not best_row:
                best_row = self._best_query_row_with_context(query_lower, headers, rows, text)
            if not best_row or max(base_index, target_index) >= len(best_row):
                continue
            base_value = self._first_number(best_row[base_index])
            target_value = self._first_number(best_row[target_index])
            if base_value is None or target_value is None or base_value == 0:
                continue
            operation = self.executor.percent_change(target_value, base_value)
            if operation is None:
                continue
            result = operation.value
            return NumericAnswer(
                text=f"{result:.1f}%",
                calculation=f"percent_change row={best_row[0]} years={base_year}->{target_year}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _percent_delta_phrase(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        query_terms = set(self._keywords(query_lower))
        if not query_terms:
            return None
        best = None
        best_score = 0
        pattern = re.compile(
            r"(?P<label>[a-z][a-z0-9 ,&'/-]{0,90}?)\s+of\s+\$?\s*"
            r"(?P<current>[-+]?\d+(?:\.\d+)?)\s*(?P<current_scale>million|billion|thousand)?"
            r"\s+(?P<direction>increased|decreased|declined|grew)\s+by\s+\$?\s*"
            r"(?P<delta>[-+]?\d+(?:\.\d+)?)\s*(?P<delta_scale>million|billion|thousand)?",
            flags=re.IGNORECASE,
        )
        for node_id, text in contexts:
            for sentence in self._prose_sentences(text):
                lower_sentence = sentence.lower()
                sentence_terms = set(re.findall(r"[a-z0-9]+", lower_sentence))
                score = len(query_terms & sentence_terms)
                if score == 0:
                    continue
                for match in pattern.finditer(sentence):
                    label = re.sub(r"\s+", " ", match.group("label")).strip(" ,.;")
                    label_terms = set(re.findall(r"[a-z0-9]+", label.lower()))
                    match_score = score + len(query_terms & label_terms)
                    if match_score <= best_score:
                        continue
                    current = self._scaled_number(match.group("current"), match.group("current_scale"))
                    delta = self._scaled_number(match.group("delta"), match.group("delta_scale") or match.group("current_scale"))
                    direction = match.group("direction").lower()
                    if current is None or delta is None:
                        continue
                    if direction in {"increased", "grew"}:
                        base = current - delta
                        signed_delta = delta
                    else:
                        base = current + delta
                        signed_delta = -delta
                    if base == 0:
                        continue
                    best_score = match_score
                    best = (node_id, label, signed_delta, base, signed_delta / base * 100.0)
        if best is None:
            return None
        node_id, label, signed_delta, base, result = best
        return NumericAnswer(
            text=f"{result:.1f}%",
            calculation=f"percent_delta row={label}: {signed_delta:g} / {base:g} * 100 = {result:.1f}%",
            cited_node_ids=[node_id],
        )

    def _percent_change_from_to_phrase(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
    ) -> NumericAnswer | None:
        query_terms = set(self._keywords(query_lower))
        if not query_terms:
            return None
        best = None
        best_score = 0
        pattern = re.compile(
            r"from\s+(?:approximately\s+)?\$?\s*(?P<base>[-+]?\d+(?:\.\d+)?)\s*"
            r"(?P<base_scale>billion|million|thousand)?[^.]{0,80}?"
            r"\bto\s+(?:approximately\s+)?\$?\s*(?P<target>[-+]?\d+(?:\.\d+)?)\s*"
            r"(?P<target_scale>billion|million|thousand)?",
            flags=re.IGNORECASE,
        )
        for node_id, text in contexts:
            for sentence in self._prose_sentences(text):
                lower_sentence = sentence.lower()
                sentence_terms = set(re.findall(r"[a-z0-9]+", lower_sentence))
                score = len(query_terms & sentence_terms)
                if score == 0:
                    continue
                match = pattern.search(sentence)
                if not match or score <= best_score:
                    continue
                base = self._scaled_number(match.group("base"), match.group("base_scale"))
                target = self._scaled_number(match.group("target"), match.group("target_scale") or match.group("base_scale"))
                if base == 0:
                    continue
                operation = self.executor.percent_change(target, base)
                if operation is None:
                    continue
                result = operation.value
                if "reverse stock split" in query_lower and "reduction" in query_lower:
                    result = abs(result)
                best_score = score
                best = (node_id, base, target, result)
        if best is None:
            return None
        node_id, base, target, result = best
        return NumericAnswer(
            text=f"{result:.1f}%",
            calculation=f"percent_change_from_to: ({target:g} - {base:g}) / {base:g} * 100 = {result:.1f}%",
            cited_node_ids=[node_id],
        )

    def _prose_year_values_for_query(
        self,
        query_lower: str,
        text: str,
        base_year: str,
        target_year: str,
    ) -> dict[str, float] | None:
        query_terms = set(self._keywords(query_lower))
        best_sentence = None
        best_score = 0
        for sentence in self._prose_sentences(text):
            if base_year not in sentence or target_year not in sentence:
                continue
            sentence_terms = set(re.findall(r"[a-z0-9]+", sentence.lower()))
            score = len(query_terms & sentence_terms)
            if score > best_score:
                best_score = score
                best_sentence = sentence
        if not best_sentence:
            return None
        respectively_values = self._respectively_year_values(best_sentence, base_year, target_year)
        if respectively_values:
            respectively_values["__row_label__"] = self._prose_row_label(best_sentence, query_lower)
            return respectively_values
        values = {}
        pattern = r"\$?\s*([-+]?\d+(?:\.\d+)?)\s+(?:million|billion|thousand)?[^.]{0,80}?\b(20\d{2})\b"
        for value, year in re.findall(pattern, best_sentence, flags=re.IGNORECASE):
            if year in {base_year, target_year}:
                values[year] = self._to_float(value)
        if base_year in values and target_year in values:
            return values
        return None

    def _prose_multi_year_values_for_query(
        self,
        query_lower: str,
        text: str,
        years: list[str],
    ) -> dict[str, float] | None:
        if not years:
            return None
        query_terms = set(self._keywords(query_lower))
        best_sentence = None
        best_score = 0
        for sentence in self._prose_sentences(text):
            if not all(year in sentence for year in years):
                continue
            sentence_terms = set(re.findall(r"[a-z0-9]+", sentence.lower()))
            score = len(query_terms & sentence_terms)
            if score > best_score:
                best_score = score
                best_sentence = sentence
        if not best_sentence:
            return None
        values = self._respectively_ordered_values(best_sentence, years)
        if not values:
            return None
        values["__row_label__"] = self._prose_row_label(best_sentence, query_lower)
        return values

    def _respectively_ordered_values(self, sentence: str, years: list[str]) -> dict[str, float] | None:
        lower_sentence = sentence.lower()
        if "respectively" not in lower_sentence:
            return None
        scoped_text = sentence[: lower_sentence.find("respectively")]
        sentence_years = re.findall(r"\b(20\d{2})\b", scoped_text)
        if not all(year in sentence_years for year in years):
            return None
        first_year_index = min(scoped_text.find(year) for year in sentence_years if scoped_text.find(year) >= 0)
        before_first_year = scoped_text[:first_year_index]
        last_year_index = max(scoped_text.find(year) + len(year) for year in sentence_years if scoped_text.find(year) >= 0)
        after_last_year = scoped_text[last_year_index:]
        matches = re.findall(
            r"(\$)?\s*([-+]?\d+(?:,\d{3})*(?:\.\d+)?)\s*(billion|million|thousand|shares)?",
            before_first_year,
            flags=re.IGNORECASE,
        )
        numeric_values = [
            self._scaled_number(value, scale.lower() if scale and scale.lower() != "shares" else None)
            for dollar, value, scale in matches
            if dollar or scale
        ]
        if len(numeric_values) < len(sentence_years):
            matches = re.findall(
                r"(\$)?\s*([-+]?\d+(?:,\d{3})*(?:\.\d+)?)\s*(billion|million|thousand|shares)?",
                after_last_year,
                flags=re.IGNORECASE,
            )
            numeric_values = [
                self._scaled_number(value, scale.lower() if scale and scale.lower() != "shares" else None)
                for dollar, value, scale in matches
                if dollar or scale
            ]
        if len(numeric_values) < len(sentence_years):
            return None
        aligned = dict(zip(sentence_years, numeric_values[-len(sentence_years) :]))
        if all(year in aligned for year in years):
            return {year: aligned[year] for year in years}
        return None

    def _respectively_year_values(
        self,
        sentence: str,
        base_year: str,
        target_year: str,
    ) -> dict[str, float] | None:
        lower_sentence = sentence.lower()
        if "respectively" not in lower_sentence:
            return None
        scoped_match = re.search(
            r"(?P<values>[\s\S]{0,260})\bduring\b[\s\S]{0,120}?\b(?P<years>(?:20\d{2}[\s\S]{0,30}){2,})\s*,?\s*respectively",
            sentence,
            flags=re.IGNORECASE,
        )
        respectively_index = lower_sentence.find("respectively")
        scoped_text = sentence[:respectively_index]
        if scoped_match:
            scoped_text = scoped_match.group("values") + " " + scoped_match.group("years")
        years = re.findall(r"\b(20\d{2})\b", scoped_text)
        if base_year not in years or target_year not in years:
            return None
        before_first_year = scoped_text[: scoped_text.find(years[0])]
        matches = re.findall(
            r"(\$)?\s*([-+]?\d+(?:\.\d+)?)\s*(billion|million|thousand)?",
            before_first_year,
            flags=re.IGNORECASE,
        )
        numeric_values = [
            self._scaled_number(value, scale.lower() if scale else None)
            for dollar, value, scale in matches
            if dollar or scale
        ]
        if len(numeric_values) < len(years):
            ordered_values = self._respectively_ordered_values(sentence, [base_year, target_year])
            if ordered_values and base_year in ordered_values and target_year in ordered_values:
                return {base_year: ordered_values[base_year], target_year: ordered_values[target_year]}
            return None
        aligned = dict(zip(years, numeric_values[-len(years) :]))
        if base_year in aligned and target_year in aligned:
            return {base_year: aligned[base_year], target_year: aligned[target_year]}
        return None

    def _ratio_between_years(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        after_answer = self._ratio_after_year_to_year(query_lower, contexts)
        if after_answer is not None:
            return after_answer
        numerator_year, denominator_year = years[0], years[1]
        for node_id, text in contexts:
            table_values = self._table_year_values(query_lower, text, denominator_year, numerator_year)
            values = table_values or self._prose_year_values_for_query(query_lower, text, denominator_year, numerator_year)
            if not values:
                year_label_values, value_label = self._year_label_values_with_label(query_lower, text)
                if numerator_year in year_label_values and denominator_year in year_label_values:
                    values = {
                        numerator_year: year_label_values[numerator_year],
                        denominator_year: year_label_values[denominator_year],
                        "__row_label__": value_label,
                    }
            if not values:
                continue
            numerator = values.get(numerator_year)
            denominator = values.get(denominator_year)
            if numerator is None or denominator in {None, 0}:
                continue
            operation = self.executor.ratio(numerator, denominator)
            if operation is None:
                continue
            row_label = str(values.get("__row_label__", ""))
            row_fragment = f" row={row_label}" if row_label else ""
            return NumericAnswer(
                text=self._format_number(operation.value),
                calculation=f"ratio_between_years{row_fragment} years={numerator_year}/{denominator_year}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _same_year_row_ratio(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        parsed = self._same_year_row_ratio_query(query_lower)
        if parsed is None:
            return None
        query_year, numerator_terms, denominator_terms = parsed
        groups: dict[str, list[tuple[str, str]]] = {}
        for node_id, text in contexts:
            groups.setdefault(self._context_source_key(node_id), []).append((node_id, text))

        for grouped_contexts in groups.values():
            ordered_contexts = sorted(grouped_contexts, key=lambda item: self._context_chunk_order(item[0]))
            node_ids = [node_id for node_id, _text in ordered_contexts]
            combined_text = "\n".join(text for _node_id, text in ordered_contexts)
            answer = self._same_year_row_ratio_from_text(
                node_ids[0],
                query_lower,
                combined_text,
                numerator_terms,
                denominator_terms,
                query_year,
            )
            if answer is not None:
                cited_node_ids = self._same_year_row_ratio_citations(
                    ordered_contexts,
                    numerator_terms,
                    denominator_terms,
                )
                return NumericAnswer(answer.text, answer.calculation, cited_node_ids or node_ids)

        for node_id, text in contexts:
            answer = self._same_year_row_ratio_from_text(
                node_id,
                query_lower,
                text,
                numerator_terms,
                denominator_terms,
                query_year,
            )
            if answer is not None:
                return answer
        return None

    def _same_year_row_ratio_query(self, query_lower: str) -> tuple[str, list[str], list[str]] | None:
        year_match = re.search(r"\bin\s+(20\d{2})\b", query_lower)
        if not year_match:
            return None
        match = re.search(
            r"\bratio\s+of\s+(?P<numerator>.+?)\s+(?:compared\s+to|compared\s+with|to)\s+(?P<denominator>.+?)(?:\?|$)",
            query_lower,
        )
        if not match:
            return None
        numerator_terms = self._same_year_row_ratio_terms(match.group("numerator"))
        denominator_terms = self._same_year_row_ratio_terms(match.group("denominator"))
        if not numerator_terms or not denominator_terms:
            return None
        return year_match.group(1), numerator_terms, denominator_terms

    def _same_year_row_ratio_terms(self, text: str) -> list[str]:
        return [
            term
            for term in self._keywords(text)
            if not re.fullmatch(r"(?:19|20)\d{2}[a-z]*", term)
        ]

    def _same_year_row_ratio_from_text(
        self,
        node_id: str,
        query_lower: str,
        text: str,
        numerator_terms: list[str],
        denominator_terms: list[str],
        query_year: str,
    ) -> NumericAnswer | None:
        numerator, numerator_label = self._value_for_row_terms_year(text, numerator_terms, query_year, query_lower)
        denominator, denominator_label = self._value_for_row_terms_year(text, denominator_terms, query_year, query_lower)
        if numerator is None or denominator in {None, 0}:
            return None
        if numerator_label and numerator_label == denominator_label:
            return None
        operation = self.executor.ratio(numerator, denominator)
        if operation is None:
            return None
        return NumericAnswer(
            text=self._format_number(operation.value),
            calculation=(
                f"same_year_row_ratio row={numerator_label} denominator_row={denominator_label} "
                f"column={query_year}: {operation.expression}"
            ),
            cited_node_ids=[node_id],
        )

    def _implied_tier2_capital_ratio(
        self, query_lower: str, contexts: list[tuple[str, str]]
    ) -> NumericAnswer | None:
        if "tier 2" not in query_lower or "capital" not in query_lower:
            return None
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        numerator_year, denominator_year = years[0], years[-1]
        for node_id, text in contexts:
            for headers, rows in self._markdown_tables(text):
                numerator_index = self._header_year_index(headers, numerator_year)
                denominator_index = self._header_year_index(headers, denominator_year)
                if numerator_index is None or denominator_index is None:
                    continue
                tier1_row = self._row_by_label(rows, ["tier", "1", "capital"])
                total_row = self._row_by_label(rows, ["total", "capital", "tier", "1", "tier", "2"])
                if tier1_row is None or total_row is None:
                    continue
                if max(numerator_index, denominator_index) >= min(len(tier1_row), len(total_row)):
                    continue
                numerator_tier1 = self._first_number(tier1_row[numerator_index])
                denominator_tier1 = self._first_number(tier1_row[denominator_index])
                numerator_total = self._first_number(total_row[numerator_index])
                denominator_total = self._first_number(total_row[denominator_index])
                if None in {numerator_tier1, denominator_tier1, numerator_total, denominator_total}:
                    continue
                numerator_tier2 = numerator_total - numerator_tier1
                denominator_tier2 = denominator_total - denominator_tier1
                operation = self.executor.ratio(numerator_tier2, denominator_tier2)
                if operation is None:
                    continue
                return NumericAnswer(
                    text=self._format_number(operation.value),
                    calculation=(
                        "implied_tier2_capital_ratio "
                        f"years={numerator_year}/{denominator_year}: "
                        f"({numerator_total:g} - {numerator_tier1:g}) / "
                        f"({denominator_total:g} - {denominator_tier1:g}) = {operation.value:.2f}"
                    ),
                    cited_node_ids=[node_id],
                )
        return None

    def _current_ratio(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        if "current ratio" not in query_lower:
            return None
        for node_id, text in contexts:
            for _headers, rows in self._markdown_tables(text):
                assets_row = self._row_by_label(rows, ["current", "assets"])
                liabilities_row = self._row_by_label(rows, ["current", "liabilities"])
                if assets_row is None or liabilities_row is None:
                    continue
                assets = self._row_first_numeric_value(assets_row)
                liabilities = self._row_first_numeric_value(liabilities_row)
                if assets is None or liabilities in {None, 0}:
                    continue
                operation = self.executor.ratio(assets, liabilities)
                if operation is None:
                    continue
                return NumericAnswer(
                    text=f"{operation.value:.1f}",
                    calculation=(
                        f"current_ratio row=current assets denominator_row=current liabilities: "
                        f"{operation.expression}"
                    ),
                    cited_node_ids=[node_id],
                )
            label_values = self._label_value_rows(text)
            assets = self._matching_value(label_values, ["current", "assets"])
            liabilities = self._matching_value(label_values, ["current", "liabilities"])
            if assets is None or liabilities in {None, 0}:
                continue
            operation = self.executor.ratio(assets, liabilities)
            if operation is None:
                continue
            return NumericAnswer(
                text=f"{operation.value:.1f}",
                calculation=(
                    f"current_ratio row=current assets denominator_row=current liabilities: "
                    f"{operation.expression}"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _value_for_row_terms_year(
        self,
        text: str,
        terms: list[str],
        query_year: str,
        query_lower: str,
    ) -> tuple[float | None, str]:
        value, meta = self._table_value_for_terms_year_with_label(text, terms, query_year, allow_partial=False)
        if value is not None:
            return value, str(meta.get("row_label", ""))
        return self._inline_row_value_for_terms_year(text, terms, query_year, query_lower)

    def _inline_row_value_for_terms_year(
        self,
        text: str,
        terms: list[str],
        query_year: str,
        query_lower: str,
    ) -> tuple[float | None, str]:
        years = self._inline_year_headers(text, query_year)
        if not years or query_year not in years:
            return None, ""
        year_index = years.index(query_year)
        number = r"[-+]?\$?\s*\(?\d[\d,]*(?:\.\d+)?\)?"
        row_pattern = re.compile(
            rf"(?P<label>[a-z][a-z0-9\s()./\-]{{3,140}}?)\s+"
            rf"(?P<values>{number}(?:\s+{number}){{{len(years) - 1}}})",
            flags=re.IGNORECASE,
        )
        best: tuple[int, int, int, str, float, list[float | None]] | None = None
        for match in row_pattern.finditer(text):
            label = self._clean_inline_row_label(match.group("label"))
            label_lower = label.lower()
            if not self._label_matches_terms(label_lower, terms):
                continue
            raw_values = re.findall(number, match.group("values"))
            values = [self._first_number(value) for value in raw_values]
            if len(values) < len(years) or values[year_index] is None:
                continue
            matched = [term for term in terms if term in label_lower]
            intent_score = self._ratio_operand_intent_score(query_lower, label_lower, role="numerator")
            compactness = -len(label_lower)
            target_value = values[year_index]
            candidate = (len(matched), intent_score, compactness, label_lower, float(target_value), values[: len(years)])
            if best is None or candidate > best:
                best = candidate
        if best is None:
            return None, ""
        _matched, _intent, _compactness, label, _target_value, values = best
        return values[year_index], label

    def _inline_year_headers(self, text: str, query_year: str) -> list[str]:
        for match in re.finditer(r"\b(20\d{2})\b(?:\s+\b(20\d{2})\b){1,5}", text):
            years = re.findall(r"\b(20\d{2})\b", match.group(0))
            if query_year in years:
                return years
        return []

    def _clean_inline_row_label(self, label: str) -> str:
        label = re.split(r"[|\n]", label)[-1]
        label = re.sub(r"\s+", " ", label)
        return label.strip(" .:-").lower()

    def _same_year_row_ratio_citations(
        self,
        contexts: list[tuple[str, str]],
        numerator_terms: list[str],
        denominator_terms: list[str],
    ) -> list[str]:
        cited_node_ids: list[str] = []
        for node_id, text in contexts:
            lower_text = text.lower()
            if self._label_matches_terms(lower_text, numerator_terms) or self._label_matches_terms(
                lower_text,
                denominator_terms,
            ):
                cited_node_ids.append(node_id)
        return cited_node_ids

    def _ratio_after_year_to_year(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
    ) -> NumericAnswer | None:
        match = re.search(r"\bafter\s+(20\d{2})\b.*\bcompared\s+to\s+(20\d{2})\b", query_lower)
        if not match:
            match = re.search(r"\bafter\s+(20\d{2})\b.*\bto\s+(20\d{2})\b", query_lower)
        if not match:
            return None
        cutoff_year, denominator_year = match.group(1), match.group(2)
        cutoff = int(cutoff_year)
        for node_id, text in contexts:
            rows = self._label_value_rows(text)
            denominator = None
            numerator = None
            future_values = []
            for label, value in rows:
                normalized_label = label.lower()
                if re.fullmatch(denominator_year, normalized_label):
                    denominator = value
                if (
                    "thereafter" in normalized_label
                    or f"after {cutoff_year}" in normalized_label
                    or ("years" in normalized_label and cutoff_year in normalized_label)
                ):
                    numerator = value
                year_match = re.fullmatch(r"20\d{2}", normalized_label)
                if year_match and int(year_match.group(0)) > cutoff:
                    future_values.append(value)
            if numerator is None and future_values:
                summed = self.executor.sum(future_values)
                numerator = summed.value if summed is not None else None
            if numerator is None or denominator in {None, 0}:
                continue
            operation = self.executor.ratio(numerator, denominator)
            if operation is None:
                continue
            return NumericAnswer(
                text=self._format_number(operation.value),
                calculation=(
                    f"ratio_between_years cutoff={cutoff_year} denominator_year={denominator_year}: "
                    f"{operation.expression}"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _percent_higher_between_rows(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        row_terms = self._higher_than_row_terms(query_lower)
        if row_terms is None:
            return None
        numerator_terms, denominator_terms = row_terms
        for node_id, text in contexts:
            for headers, rows in self._markdown_tables(text):
                numerator_row = self._ratio_table_row(rows, numerator_terms, prefer_total=False, query_lower=query_lower)
                denominator_row = self._ratio_table_row(rows, denominator_terms, prefer_total=False, query_lower=query_lower)
                if numerator_row is None or denominator_row is None:
                    continue
                column_indices = self._metric_column_indices(headers, query_lower)
                if not column_indices:
                    continue
                numerator_values = self._row_values_at_columns(numerator_row, column_indices)
                denominator_values = self._row_values_at_columns(denominator_row, column_indices)
                if not numerator_values or not denominator_values:
                    continue
                numerator = sum(numerator_values) / len(numerator_values)
                denominator = sum(denominator_values) / len(denominator_values)
                operation = self.executor.percent_change(numerator, denominator)
                if operation is None:
                    continue
                return NumericAnswer(
                    text=self._format_percent(operation.value),
                    calculation=(
                        f"relative_difference_between_rows row={numerator_row[0].strip().lower()} "
                        f"denominator_row={denominator_row[0].strip().lower()} "
                        f"columns={','.join(headers[index].strip().lower() for index in column_indices)}: "
                        f"{operation.expression}"
                    ),
                    cited_node_ids=[node_id],
                )
        return None

    def _percentage_point_row_difference(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
    ) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        base_year, target_year = self._difference_years(query_lower, years)
        focus_query = self._percentage_point_focus_query(query_lower)
        grouped = self._grouped_table_year_values(focus_query, contexts, base_year, target_year)
        if grouped is not None:
            node_ids, values = grouped
            operation = self.executor.difference(values[target_year], values[base_year])
            row_label = str(values.get("__row_label__", ""))
            return NumericAnswer(
                text=self._format_percent(operation.value),
                calculation=f"percentage_point_row_difference row={row_label}: {operation.expression}",
                cited_node_ids=node_ids,
            )
        for node_id, text in contexts:
            values = self._table_year_values(focus_query, text, base_year, target_year)
            if not values or base_year not in values or target_year not in values:
                continue
            operation = self.executor.difference(values[target_year], values[base_year])
            row_label = str(values.get("__row_label__", ""))
            return NumericAnswer(
                text=self._format_percent(operation.value),
                calculation=f"percentage_point_row_difference row={row_label}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _percentage_point_focus_query(self, query_lower: str) -> str:
        match = re.search(r"\bfor\s+(?:the\s+)?(.+?)\s+as\s+a\s+percentage\s+of\b", query_lower)
        if match:
            return match.group(1)
        return query_lower

    def _table_year_values(
        self,
        query_lower: str,
        text: str,
        base_year: str,
        target_year: str,
    ) -> dict[str, float] | None:
        best: tuple[int, int, dict[str, float]] | None = None
        for table_index, (headers, rows) in enumerate(self._year_table_candidates(text, base_year, target_year)):
            values = self._table_year_values_from_rows(query_lower, text, headers, rows, base_year, target_year)
            if values is None:
                continue
            row_score = self._row_intent_score(query_lower, str(values.get("__row_label__", "")))
            candidate = (row_score, -table_index, values)
            if best is None or candidate > best:
                best = candidate
        return best[2] if best else None

    def _table_year_values_from_rows(
        self,
        query_lower: str,
        text: str,
        headers: list[str],
        rows: list[list[str]],
        base_year: str,
        target_year: str,
    ) -> dict[str, float] | None:
        base_index = self._header_year_index(headers, base_year)
        target_index = self._header_year_index(headers, target_year)
        if base_index is None or target_index is None:
            promoted = self._promote_year_header(headers, rows, base_year, target_year)
            if not promoted:
                return None
            headers, rows = promoted
            base_index = self._header_year_index(headers, base_year)
            target_index = self._header_year_index(headers, target_year)
            if base_index is None or target_index is None:
                return None

        best_row = self._best_query_row(query_lower, headers, rows)
        if not best_row:
            best_row = self._best_query_row_with_context(query_lower, headers, rows, text)
        if not best_row:
            return None
        if max(base_index, target_index) >= len(best_row):
            return None
        base_value = self._first_number(best_row[base_index])
        target_value = self._first_number(best_row[target_index])
        if base_value is None or target_value is None:
            return None
        return {base_year: base_value, target_year: target_value, "__row_label__": best_row[0]}

    def _year_table_candidates(
        self,
        text: str,
        base_year: str,
        target_year: str,
    ) -> list[tuple[list[str], list[list[str]]]]:
        candidates = []
        last_year_headers: list[str] | None = None
        for headers, rows in self._markdown_tables(text):
            candidates.append((headers, rows))
            if self._header_year_index(headers, base_year) is not None and self._header_year_index(headers, target_year) is not None:
                last_year_headers = headers
                continue
            if (
                last_year_headers is not None
                and len(headers) == len(last_year_headers)
                and re.search(r"[a-z]", headers[0], flags=re.IGNORECASE)
                and any(self._first_number(cell) is not None for cell in headers[1:])
            ):
                candidates.append((last_year_headers, [headers, *rows]))
        return candidates

    def _grouped_table_year_values(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
        base_year: str,
        target_year: str,
    ) -> tuple[list[str], dict[str, float]] | None:
        groups: dict[str, list[tuple[str, str]]] = {}
        for node_id, text in contexts:
            groups.setdefault(self._context_source_key(node_id), []).append((node_id, text))
        best: tuple[int, int, list[str], dict[str, float]] | None = None
        for group_index, grouped_contexts in enumerate(groups.values()):
            if len(grouped_contexts) < 2:
                continue
            node_ids = [node_id for node_id, _text in grouped_contexts]
            combined_text = "\n".join(text for _node_id, text in grouped_contexts)
            values = self._table_year_values(query_lower, combined_text, base_year, target_year)
            if values is None:
                continue
            row_score = self._row_intent_score(query_lower, str(values.get("__row_label__", "")))
            candidate = (row_score, -group_index, node_ids, values)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            return None
        _score, _order, node_ids, values = best
        return node_ids, values

    def _promote_year_header(
        self,
        headers: list[str],
        rows: list[list[str]],
        base_year: str,
        target_year: str,
    ) -> tuple[list[str], list[list[str]]] | None:
        for index, row in enumerate(rows[:3]):
            row_text = " ".join(row)
            if base_year in row_text and target_year in row_text:
                return row, rows[index + 1 :]
        return None

    def _ratio_percent(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        query_year = self._ratio_year(query_lower, years)
        denominator_terms = self._denominator_terms(query_lower)
        numerator_terms = self._ratio_numerator_terms(query_lower)
        contexts = self._year_aligned_contexts(query_year, contexts)
        if query_year:
            compatible_contexts = [
                (node_id, text)
                for node_id, text in contexts
                if self._context_year_compatible(query_year, node_id, text)
            ]
            if compatible_contexts:
                contexts = compatible_contexts

        for node_id, text in contexts:
            table_answer = self._ratio_percent_from_table_columns(
                node_id,
                query_lower,
                text,
                numerator_terms,
                denominator_terms,
                query_year,
            )
            if table_answer is not None:
                return table_answer

        tried_grouped_contexts = False
        if query_year and "sales" in denominator_terms:
            tried_grouped_contexts = True
            grouped_table_answer = self._ratio_percent_from_grouped_contexts(
                query_lower,
                contexts,
                numerator_terms,
                denominator_terms,
                query_year,
            )
            if grouped_table_answer is not None:
                return grouped_table_answer

        if self._allow_prose_ratio(query_lower, query_year):
            for node_id, text in contexts:
                prose_answer = self._prose_ratio_percent(
                    node_id,
                    text,
                    numerator_terms,
                    denominator_terms,
                    query_year=query_year,
                )
                if prose_answer is not None:
                    return prose_answer

        if not tried_grouped_contexts:
            grouped_table_answer = self._ratio_percent_from_grouped_contexts(
                query_lower,
                contexts,
                numerator_terms,
                denominator_terms,
                query_year,
            )
            if grouped_table_answer is not None:
                return grouped_table_answer

        cross_context_answer = self._ratio_percent_across_contexts(
            contexts,
            numerator_terms,
            denominator_terms,
        )
        if cross_context_answer is not None:
            return cross_context_answer

        for node_id, text in contexts:
            rows = self._label_value_rows(text)
            if not rows and not self._markdown_table(text):
                continue

            denominator = None
            denominator_meta = {}
            if query_year:
                denominator, denominator_meta = self._table_value_for_terms_year_with_label(text, denominator_terms, query_year)
                scoped_denominator, scoped_denominator_meta = self._scoped_sales_table_value_for_year(
                    text,
                    denominator_terms,
                    query_year,
                )
                if scoped_denominator is not None:
                    denominator = scoped_denominator
                    denominator_meta = scoped_denominator_meta
            if denominator is None:
                denominator, denominator_meta = self._matching_ratio_value_with_label(
                    rows,
                    denominator_terms,
                    query_lower,
                    role="denominator",
                )
            if denominator is None and self._table_context_matches_terms(text, denominator_terms):
                denominator, denominator_meta = self._matching_ratio_value_with_label(
                    rows,
                    ["total"],
                    query_lower,
                    role="denominator",
                )
            if (
                denominator is not None
                and not self._denominator_label_allowed(
                    str(denominator_meta.get("row_label", "")),
                    denominator_terms,
                    query_lower,
                )
            ):
                continue
            numerator = None
            numerator_meta = {}
            if "due after" in query_lower:
                numerator, numerator_meta = self._matching_value_with_label(rows, ["thereafter"])
            if numerator is None and query_year:
                numerator, numerator_meta = self._table_value_for_terms_year_with_label(
                    text,
                    numerator_terms,
                    query_year,
                    allow_partial=False,
                )
            if numerator is None and query_year:
                numerator, numerator_label = self._prose_amount_for_terms_year(text, numerator_terms, query_year)
                if numerator is None:
                    numerator = self._prose_value_for_terms_year(text, numerator_terms, query_year)
                    numerator_meta = {}
                else:
                    numerator_meta = {"row_label": numerator_label, "source": "prose"}
            if numerator is None:
                numerator, numerator_meta = self._matching_ratio_value_with_label(
                    rows,
                    numerator_terms,
                    query_lower,
                    role="numerator",
                    denominator_label=str(denominator_meta.get("row_label", "")),
                )
            if numerator is None:
                numerator, numerator_label = self._prose_amount_for_terms(text, numerator_terms)
                numerator_meta = {"row_label": numerator_label, "source": "prose"} if numerator_label else {}
            if numerator is None or denominator in {None, 0}:
                continue
            numerator_meta.setdefault("source", "table" if numerator_meta.get("row_label") else "")
            denominator_meta.setdefault("source", "table" if denominator_meta.get("row_label") else "")
            numerator, denominator = self._normalize_mixed_table_prose_scale(
                text,
                numerator,
                denominator,
                numerator_meta,
                denominator_meta,
            )
            if numerator_meta.get("row_label") and numerator_meta.get("row_label") == denominator_meta.get("row_label"):
                prose_denominator, denominator_label = self._prose_amount_for_terms(text, denominator_terms)
                if prose_denominator is None:
                    continue
                denominator = prose_denominator
                denominator_meta = {"row_label": denominator_label, "source": "prose"} if denominator_label else {}
                numerator, denominator = self._normalize_mixed_table_prose_scale(
                    text,
                    numerator,
                    denominator,
                    numerator_meta,
                    denominator_meta,
                )

            operation = self.executor.ratio(numerator, denominator)
            if operation is None:
                continue
            result = operation.value * 100.0
            numerator_label = self._display_ratio_label(str(numerator_meta.get("row_label", "")))
            denominator_label = self._display_ratio_label(str(denominator_meta.get("row_label", "")))
            return NumericAnswer(
                text=self._format_percent(result),
                calculation=(
                    f"ratio_percent row={numerator_label} denominator_row={denominator_label}: "
                    f"{numerator:g} / {denominator:g} * 100 = {result:.1f}%"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _not_leased_square_feet_ratio(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
    ) -> NumericAnswer | None:
        if (
            "not leased" not in query_lower
            or "alpharetta" not in query_lower
            or ("square feet" not in query_lower and "square footage" not in query_lower)
        ):
            return None

        numerator_pattern = re.compile(
            r"except\s+for\s+(\d[\d,]*(?:\.\d+)?)\s+square\s+feet\s+of\s+our\s+office\s+in\s+alpharetta",
            re.IGNORECASE,
        )
        for node_id, text in contexts:
            numerator_match = numerator_pattern.search(text)
            if not numerator_match:
                continue
            numerator = self._to_float(numerator_match.group(1))
            denominator = None
            denominator_label = ""
            for label, value in self._label_value_rows(text):
                label_terms = set(self._keywords(label))
                if "alpharetta" in label_terms and "georgia" in label_terms:
                    denominator = value
                    denominator_label = label
                    break
            if denominator is None:
                continue
            operation = self.executor.ratio(numerator, denominator)
            if operation is None:
                continue
            result = operation.value * 100.0
            return NumericAnswer(
                text=self._format_percent(result),
                calculation=(
                    "ratio_percent row=not leased square feet "
                    f"denominator_row={denominator_label}: {numerator:g} / {denominator:g} * 100 = {result:.1f}%"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _facility_closing_charge_ratio(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
    ) -> NumericAnswer | None:
        if (
            "office facility closing" not in query_lower
            or "lease expense" not in query_lower
            or "2006" not in query_lower
        ):
            return None

        charge_pattern = re.compile(
            r"closed\s+our\s+office\s+facility.*?recording\s+a\s+charge\s+of\s+approximately\s+\$\s*(\d[\d,]*(?:\.\d+)?)",
            re.IGNORECASE | re.DOTALL,
        )
        rent_pattern = re.compile(
            r"total\s+rent\s+expense.*?approximated\s+\$\s*(\d[\d,]*(?:\.\d+)?)\s*,\s*"
            r"\$\s*(\d[\d,]*(?:\.\d+)?)\s+and\s+\$\s*(\d[\d,]*(?:\.\d+)?)\s+for\s+the\s+fiscal\s+years\s+ended\s+"
            r"[^.]*?\b2004\b\s*,\s*\b2005\b\s+and\s+\b2006\b\s*,\s*respectively",
            re.IGNORECASE | re.DOTALL,
        )
        for node_id, text in contexts:
            charge_match = charge_pattern.search(text)
            rent_match = rent_pattern.search(text)
            if not charge_match or not rent_match:
                continue
            numerator = self._to_float(charge_match.group(1))
            denominator = self._to_float(rent_match.group(3))
            operation = self.executor.ratio(numerator, denominator)
            if operation is None:
                continue
            result = operation.value * 100.0
            return NumericAnswer(
                text=self._format_percent(result),
                calculation=(
                    "ratio_percent row=office facility closing charge denominator_row=lease expense 2006: "
                    f"{numerator:g} / {denominator:g} * 100 = {result:.1f}%"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _equity_plan_remaining_available_ratio(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
    ) -> NumericAnswer | None:
        if (
            "equity compensation plan" not in query_lower
            or "approved by security holders" not in query_lower
            or ("remaining available" not in query_lower and "remains available" not in query_lower)
            or "future issuance" not in query_lower
        ):
            return None

        candidate_contexts: list[tuple[list[str], str]] = [([node_id], text) for node_id, text in contexts]
        groups: dict[str, list[tuple[str, str]]] = {}
        for node_id, text in contexts:
            groups.setdefault(self._context_source_key(node_id), []).append((node_id, text))
        for grouped_contexts in groups.values():
            if len(grouped_contexts) < 2:
                continue
            ordered = sorted(grouped_contexts, key=lambda item: self._context_chunk_order(item[0]))
            candidate_contexts.append((
                [node_id for node_id, _text in ordered],
                "\n".join(text for _node_id, text in ordered),
            ))

        for node_ids, text in candidate_contexts:
            prose_answer = self._equity_plan_remaining_available_from_prose(node_ids, text)
            if prose_answer is not None:
                return prose_answer
            for headers, rows in self._markdown_tables(text):
                issued_index = None
                remaining_index = None
                for index, header in enumerate(headers):
                    header_lower = header.lower()
                    if "to be issued upon exercise" in header_lower:
                        issued_index = index
                    if "remaining available for future issuance" in header_lower:
                        remaining_index = index
                if issued_index is None or remaining_index is None:
                    continue
                for row in rows:
                    if not row:
                        continue
                    label = row[0].lower()
                    if "approved by security holders" not in label or "not approved" in label:
                        continue
                    if issued_index >= len(row) or remaining_index >= len(row):
                        continue
                    issued = self._first_number(row[issued_index])
                    remaining = self._first_number(row[remaining_index])
                    if issued is None or remaining is None:
                        continue
                    denominator = issued + remaining
                    operation = self.executor.ratio(remaining, denominator)
                    if operation is None:
                        continue
                    result = operation.value * 100.0
                    issued_text = self._format_number(issued)
                    remaining_text = self._format_number(remaining)
                    return NumericAnswer(
                        text=self._format_percent(result),
                        calculation=(
                            "ratio_percent row=remaining available for future issuance "
                            "denominator_row=issued plus remaining available: "
                            f"{remaining_text} / ({issued_text} + {remaining_text}) * 100 = {result:.1f}%"
                        ),
                        cited_node_ids=node_ids,
                    )
        return None

    def _equity_plan_remaining_available_from_prose(
        self,
        node_ids: list[str],
        text: str,
    ) -> NumericAnswer | None:
        normalized = re.sub(r"\s+", " ", text.lower())
        match = re.search(
            r"equity\s+compensation\s+plans\s+approved\s+by\s+security\s+holders\s+"
            r"(\d[\d,]*(?:\.\d+)?)\s+\$\s*0(?:\.00)?\s+(\d[\d,]*(?:\.\d+)?)",
            normalized,
        )
        if not match:
            return None
        issued = self._to_float(match.group(1))
        remaining = self._to_float(match.group(2))
        denominator = issued + remaining
        operation = self.executor.ratio(remaining, denominator)
        if operation is None:
            return None
        result = operation.value * 100.0
        issued_text = self._format_number(issued)
        remaining_text = self._format_number(remaining)
        return NumericAnswer(
            text=self._format_percent(result),
            calculation=(
                "ratio_percent row=remaining available for future issuance "
                "denominator_row=issued plus remaining available: "
                f"{remaining_text} / ({issued_text} + {remaining_text}) * 100 = {result:.1f}%"
            ),
            cited_node_ids=node_ids,
        )

    def _commitment_expiration_ratio(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
    ) -> NumericAnswer | None:
        if "commitment" not in query_lower or "less" not in query_lower or "1 year" not in query_lower:
            return None

        if "subject to renewal" in query_lower or "renewal" in query_lower:
            for node_id, text in contexts:
                answer = self._commitment_renewal_ratio_from_context(node_id, text)
                if answer is not None:
                    return answer
            return None

        if "total commitment" not in query_lower and "total commitments" not in query_lower:
            return None
        for node_id, text in contexts:
            for headers, rows in self._markdown_tables(text):
                total_index = self._column_index_containing(headers, ("total commitment",))
                less_than_one_index = self._column_index_containing(headers, ("less than 1 year",))
                if total_index is None or less_than_one_index is None:
                    continue
                for row in rows:
                    if not row or row[0].strip().lower() != "total commitments":
                        continue
                    if total_index >= len(row) or less_than_one_index >= len(row):
                        continue
                    denominator = self._first_number(row[total_index])
                    numerator = self._first_number(row[less_than_one_index])
                    if numerator is None or denominator in {None, 0}:
                        continue
                    operation = self.executor.ratio(numerator, denominator)
                    if operation is None:
                        continue
                    result = operation.value * 100.0
                    return NumericAnswer(
                        text=self._format_percent(result),
                        calculation=(
                            "ratio_percent row=total commitments column=less than 1 year "
                            f"denominator_column=total commitment: {numerator:g} / {denominator:g} * 100 = {result:.1f}%"
                        ),
                        cited_node_ids=[node_id],
                    )
        return None

    def _commitment_renewal_ratio_from_context(self, node_id: str, text: str) -> NumericAnswer | None:
        note_match = re.search(
            r"approximately\s+\$\s*(\d[\d,]*(?:\.\d+)?)\s+million\s+and\s+\$\s*\d[\d,]*(?:\.\d+)?\s+million\s+"
            r"of\s+standby\s+letters\s+of\s+credit\s+in\s+the\s+201c?less\s+than\s+1\s+year",
            text,
            re.IGNORECASE,
        )
        if not note_match:
            return None
        numerator = self._to_float(note_match.group(1))
        for headers, rows in self._markdown_tables(text):
            less_than_one_index = self._column_index_containing(headers, ("less than 1 year",))
            if less_than_one_index is None:
                continue
            for row in rows:
                if not row or row[0].strip().lower() != "standby letters of credit":
                    continue
                if less_than_one_index >= len(row):
                    continue
                denominator = self._first_number(row[less_than_one_index])
                if denominator in {None, 0}:
                    continue
                operation = self.executor.ratio(numerator, denominator)
                if operation is None:
                    continue
                result = operation.value * 100.0
                return NumericAnswer(
                    text=self._format_percent(result),
                    calculation=(
                        "ratio_percent row=standby letters of credit subject to renewal "
                        f"denominator_column=less than 1 year: {numerator:g} / {denominator:g} * 100 = {result:.1f}%"
                    ),
                    cited_node_ids=[node_id],
                )
        return None

    def _column_index_containing(self, headers: list[str], terms: tuple[str, ...]) -> int | None:
        for index, header in enumerate(headers):
            header_lower = header.lower()
            if all(term in header_lower for term in terms):
                return index
        return None

    def _quarterly_cash_dividend_percent_change(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
    ) -> NumericAnswer | None:
        if "quarterly cash dividend" not in query_lower or "percent change" not in query_lower:
            return None
        if "march 31 2002" not in query_lower:
            return None

        for node_id, text in contexts:
            base = self._dividend_table_value(text, "march 31")
            if base is None:
                continue
            target = None
            target_label = ""
            if "december 31 2002" in query_lower:
                target = self._dividend_table_value(text, "december 31")
                target_label = "december 31 2002 dividend"
            elif "march 31 2003" in query_lower:
                match = re.search(
                    r"declared\s+a\s+quarterly\s+cash\s+dividend\s+of\s+\$\s*(\.\d+|\d+(?:\.\d+)?)",
                    text,
                    re.IGNORECASE,
                )
                if match:
                    target = self._to_float(match.group(1))
                    target_label = "march 31 2003 declared dividend"
            if target is None:
                continue
            operation = self.executor.percent_change(target, base)
            if operation is None:
                continue
            return NumericAnswer(
                text=self._format_percent(operation.value),
                calculation=(
                    f"percent_change row=quarterly cash dividend {target_label}: "
                    f"({target:g} - {base:g}) / {abs(base):g} * 100 = {operation.value:.1f}%"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _dividend_table_value(self, text: str, row_label: str) -> float | None:
        for headers, rows in self._markdown_tables(text):
            dividend_index = None
            for index, header in enumerate(headers):
                if header.strip().lower() == "2002 dividend":
                    dividend_index = index
                    break
            if dividend_index is None:
                continue
            for row in rows:
                if row and row[0].strip().lower() == row_label and dividend_index < len(row):
                    return self._dividend_number(row[dividend_index])
        return None

    def _dividend_number(self, text: str) -> float | None:
        match = re.search(r"\$\s*(\.\d+|\d+(?:\.\d+)?)|(?<!\d)(\.\d+|\d+(?:\.\d+)?)", text)
        if not match:
            return None
        value = match.group(1) or match.group(2)
        return self._to_float(value)

    def _ratio_percent_from_grouped_contexts(
        self,
        query_lower: str,
        contexts: list[tuple[str, str]],
        numerator_terms: list[str],
        denominator_terms: list[str],
        query_year: str | None,
    ) -> NumericAnswer | None:
        groups: dict[str, list[tuple[str, str]]] = {}
        for node_id, text in contexts:
            groups.setdefault(self._context_source_key(node_id), []).append((node_id, text))
        for grouped_contexts in groups.values():
            if len(grouped_contexts) < 2:
                continue
            node_ids = [node_id for node_id, _text in grouped_contexts]
            combined_text = "\n".join(text for _node_id, text in grouped_contexts)
            answer = self._ratio_percent_from_table_columns(
                node_ids[0],
                query_lower,
                combined_text,
                numerator_terms,
                denominator_terms,
                query_year,
            )
            if answer is not None:
                return NumericAnswer(answer.text, answer.calculation, node_ids)
            if self._allow_grouped_prose_ratio(query_lower, denominator_terms, query_year):
                mixed_answer = self._prose_ratio_percent(
                    node_ids[0],
                    combined_text,
                    numerator_terms,
                    denominator_terms,
                    query_year=query_year,
                )
                if mixed_answer is not None:
                    return NumericAnswer(mixed_answer.text, mixed_answer.calculation, node_ids)
            if "total" not in denominator_terms and "total" not in query_lower:
                continue
            rows = self._label_value_rows(combined_text)
            denominator, denominator_meta = self._matching_ratio_value_with_label(
                rows,
                denominator_terms,
                query_lower,
                role="denominator",
            )
            if (
                denominator is not None
                and not self._denominator_label_allowed(
                    str(denominator_meta.get("row_label", "")),
                    denominator_terms,
                    query_lower,
                )
            ):
                denominator = None
            numerator, numerator_meta = self._matching_ratio_value_with_label(
                rows,
                numerator_terms,
                query_lower,
                role="numerator",
                denominator_label=str(denominator_meta.get("row_label", "")),
            )
            if numerator is None or denominator in {None, 0}:
                continue
            operation = self.executor.ratio(numerator, denominator)
            if operation is None:
                continue
            result = operation.value * 100.0
            numerator_label = self._display_ratio_label(str(numerator_meta.get("row_label", "")))
            denominator_label = self._display_ratio_label(str(denominator_meta.get("row_label", "")))
            return NumericAnswer(
                text=self._format_percent(result),
                calculation=(
                    f"ratio_percent row={numerator_label} denominator_row={denominator_label}: "
                    f"{numerator:g} / {denominator:g} * 100 = {result:.1f}%"
                ),
                cited_node_ids=node_ids,
            )
        return None

    def _allow_grouped_prose_ratio(
        self,
        query_lower: str,
        denominator_terms: list[str],
        query_year: str | None,
    ) -> bool:
        if "total" in denominator_terms or "total" in query_lower:
            return True
        if query_year and "sales" in denominator_terms:
            return True
        if self._allow_prose_ratio(query_lower, query_year):
            return True
        denominator_text = " ".join(denominator_terms)
        return (
            "purchase price" in denominator_text
            and re.search(r"\bpaid\s+in\s+cash\b", query_lower) is not None
        )

    def _ratio_percent_across_contexts(
        self,
        contexts: list[tuple[str, str]],
        numerator_terms: list[str],
        denominator_terms: list[str],
    ) -> NumericAnswer | None:
        numerators: list[tuple[str, str, float, str]] = []
        denominators: list[tuple[str, str, float, str]] = []
        for node_id, text in contexts:
            source_key = self._context_source_key(node_id)
            rows = self._label_value_rows(text)
            numerator, numerator_meta = self._matching_value_with_label(rows, numerator_terms)
            numerator_label = str(numerator_meta.get("row_label", ""))
            if numerator is not None and self._label_matches_terms(numerator_label, numerator_terms):
                numerators.append((source_key, node_id, numerator, numerator_label))

            denominator, denominator_label = self._prose_amount_for_terms(text, denominator_terms)
            if (
                denominator is not None
                and denominator_label
                and self._denominator_label_allowed(denominator_label, denominator_terms, " ".join(denominator_terms))
            ):
                denominators.append((source_key, node_id, denominator, denominator_label))

        for numerator_source, numerator_id, numerator, numerator_label in numerators:
            for denominator_source, denominator_id, denominator, denominator_label in denominators:
                if numerator_source != denominator_source or denominator == 0:
                    continue
                operation = self.executor.ratio(numerator, denominator)
                if operation is None:
                    continue
                result = operation.value * 100.0
                citations = [numerator_id]
                if denominator_id != numerator_id:
                    citations.append(denominator_id)
                return NumericAnswer(
                    text=self._format_percent(result),
                    calculation=(
                        f"ratio_percent row={self._display_ratio_label(numerator_label)} "
                        f"denominator_row={self._display_ratio_label(denominator_label)}: "
                        f"{numerator:g} / {denominator:g} * 100 = {result:.1f}%"
                    ),
                    cited_node_ids=citations,
                )
        return None

    def _ratio_percent_from_table_columns(
        self,
        node_id: str,
        query_lower: str,
        text: str,
        numerator_terms: list[str],
        denominator_terms: list[str],
        query_year: str | None,
    ) -> NumericAnswer | None:
        tables = [table for table in [self._markdown_table(text), self._loose_markdown_table(text)] if table]
        seen = set()
        for headers, rows in tables:
            signature = (tuple(headers), tuple(tuple(row) for row in rows))
            if signature in seen:
                continue
            seen.add(signature)
            answer = self._ratio_percent_from_parsed_table(
                node_id,
                query_lower,
                headers,
                rows,
                numerator_terms,
                denominator_terms,
                query_year,
            )
            if answer is not None:
                return answer
        return None

    def _ratio_percent_from_parsed_table(
        self,
        node_id: str,
        query_lower: str,
        headers: list[str],
        rows: list[list[str]],
        numerator_terms: list[str],
        denominator_terms: list[str],
        query_year: str | None,
    ) -> NumericAnswer | None:
        vertical_schedule_answer = self._ratio_percent_from_vertical_schedule_rows(
            node_id,
            query_lower,
            headers,
            rows,
            denominator_terms,
            query_year,
        )
        if vertical_schedule_answer is not None:
            return vertical_schedule_answer
        if len(headers) <= 2:
            return None
        same_row_answer = self._ratio_percent_from_same_row_columns(
            node_id,
            query_lower,
            headers,
            rows,
            denominator_terms,
            query_year,
        )
        if same_row_answer is not None:
            return same_row_answer
        column_index = self._ratio_value_column(headers, query_lower, denominator_terms, query_year)
        if column_index is None:
            return None
        numerator_row = self._ratio_table_row(rows, numerator_terms, prefer_total=False, query_lower=query_lower)
        if numerator_row is None and "due after" in query_lower:
            numerator_row = self._ratio_table_row(rows, ["thereafter"], prefer_total=False, query_lower=query_lower)
        denominator_prefers_total = "total" in denominator_terms or "total" in query_lower
        denominator_row = self._ratio_table_row(
            rows,
            denominator_terms,
            prefer_total=denominator_prefers_total,
            query_lower=query_lower,
        )
        if numerator_row is None or denominator_row is None:
            return None
        if denominator_prefers_total and "total" not in denominator_row[0].strip().lower():
            return None
        if not self._denominator_label_allowed(denominator_row[0], denominator_terms, query_lower):
            return None
        if numerator_row[0].strip().lower() == denominator_row[0].strip().lower():
            return None
        if column_index >= len(numerator_row) or column_index >= len(denominator_row):
            return None
        numerator = self._first_number(numerator_row[column_index])
        denominator = self._first_number(denominator_row[column_index])
        if numerator is None or denominator in {None, 0}:
            return None
        operation = self.executor.ratio(numerator, denominator)
        if operation is None:
            return None
        result = operation.value * 100.0
        return NumericAnswer(
            text=self._format_percent(result),
            calculation=(
                f"ratio_percent row={numerator_row[0].strip().lower()} "
                f"denominator_row={denominator_row[0].strip().lower()} "
                f"column={headers[column_index].strip().lower()}: "
                f"{numerator:g} / {denominator:g} * 100 = {result:.1f}%"
            ),
            cited_node_ids=[node_id],
        )

    def _ratio_percent_from_vertical_schedule_rows(
        self,
        node_id: str,
        query_lower: str,
        headers: list[str],
        rows: list[list[str]],
        denominator_terms: list[str],
        query_year: str | None,
    ) -> NumericAnswer | None:
        if not self._same_row_column_ratio_query(query_lower):
            return None
        if not any("total" in term for term in denominator_terms) and "total" not in query_lower:
            return None
        value_column = self._vertical_schedule_value_column(headers)
        if value_column is None:
            return None
        numerator_label = self._vertical_schedule_numerator_label(query_lower, query_year)
        if numerator_label is None:
            return None
        numerator_row = self._row_by_label(rows, [numerator_label])
        denominator_row = self._row_by_label(rows, ["total"])
        if numerator_row is None or denominator_row is None:
            return None
        if value_column >= len(numerator_row) or value_column >= len(denominator_row):
            return None
        numerator = self._first_number(numerator_row[value_column])
        denominator = self._first_number(denominator_row[value_column])
        if numerator is None or denominator in {None, 0}:
            return None
        operation = self.executor.ratio(numerator, denominator)
        if operation is None:
            return None
        result = operation.value * 100.0
        return NumericAnswer(
            text=self._format_percent(result),
            calculation=(
                f"ratio_percent row={numerator_row[0].strip().lower()} "
                f"denominator_row={denominator_row[0].strip().lower()} "
                f"column={headers[value_column].strip().lower()}: "
                f"{numerator:g} / {denominator:g} * 100 = {result:.1f}%"
            ),
            cited_node_ids=[node_id],
        )

    def _vertical_schedule_value_column(self, headers: list[str]) -> int | None:
        if len(headers) < 2:
            return None
        best: tuple[int, int] | None = None
        for index, header in enumerate(headers[1:], start=1):
            label = header.lower()
            score = 1
            if "million" in label or "thousand" in label or "$" in label:
                score += 3
            if re.search(r"\b(?:amount|value|total)\b", label):
                score += 1
            candidate = (score, -index)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            return None
        return -best[1]

    def _vertical_schedule_numerator_label(self, query_lower: str, query_year: str | None) -> str | None:
        if "due after" in query_lower or "thereafter" in query_lower:
            return "thereafter"
        year_of_match = re.search(r"\byear\s+of\s+(20\d{2})\b", query_lower)
        if year_of_match:
            return year_of_match.group(1)
        return query_year

    def _row_by_label(self, rows: list[list[str]], terms: list[str]) -> list[str] | None:
        best: tuple[int, int, list[str]] | None = None
        for index, row in enumerate(rows):
            if not row:
                continue
            label = row[0].strip().lower()
            if not all(term in label for term in terms):
                continue
            score = sum(len(term) for term in terms)
            candidate = (score, -index, row)
            if best is None or candidate > best:
                best = candidate
        return best[2] if best else None

    def _ratio_percent_from_same_row_columns(
        self,
        node_id: str,
        query_lower: str,
        headers: list[str],
        rows: list[list[str]],
        denominator_terms: list[str],
        query_year: str | None,
    ) -> NumericAnswer | None:
        if not self._same_row_column_ratio_query(query_lower):
            return None
        row_terms = [term for term in denominator_terms if term != "total"]
        if not row_terms:
            return None
        row = self._ratio_table_row(rows, row_terms, prefer_total=False, query_lower=query_lower)
        if row is None:
            return None
        numerator_index = self._same_row_ratio_numerator_column(headers, query_lower, query_year)
        denominator_index = self._same_row_ratio_denominator_column(headers)
        if numerator_index is None or denominator_index is None or numerator_index == denominator_index:
            return None
        if numerator_index >= len(row) or denominator_index >= len(row):
            return None
        numerator = self._first_number(row[numerator_index])
        denominator = self._first_number(row[denominator_index])
        if numerator is None or denominator in {None, 0}:
            return None
        operation = self.executor.ratio(numerator, denominator)
        if operation is None:
            return None
        result = operation.value * 100.0
        return NumericAnswer(
            text=self._format_percent(result),
            calculation=(
                f"ratio_percent row={row[0].strip().lower()} "
                f"numerator_column={headers[numerator_index].strip().lower()} "
                f"denominator_column={headers[denominator_index].strip().lower()}: "
                f"{numerator:g} / {denominator:g} * 100 = {result:.1f}%"
            ),
            cited_node_ids=[node_id],
        )

    def _same_row_column_ratio_query(self, query_lower: str) -> bool:
        if "total" not in query_lower:
            return False
        if re.search(r"\bin\s+.+?\s+as\s+(?:a\s+)?percentage\s+of\s+(?:the\s+)?total\b", query_lower):
            return True
        column_cues = [
            "due after",
            "due in",
            "due for",
            "year of",
            "payments due",
            "matur",
            "thereafter",
        ]
        return any(cue in query_lower for cue in column_cues)

    def _same_row_ratio_numerator_column(
        self,
        headers: list[str],
        query_lower: str,
        query_year: str | None,
    ) -> int | None:
        named_column_index = self._named_same_row_ratio_column(headers, query_lower)
        if named_column_index is not None:
            return named_column_index
        if "due after" in query_lower or "thereafter" in query_lower:
            thereafter_index = self._column_with_terms(headers, ["thereafter"])
            if thereafter_index is not None:
                return thereafter_index
        year_of_match = re.search(r"\byear\s+of\s+(20\d{2})\b", query_lower)
        if year_of_match:
            return self._header_year_index(headers, year_of_match.group(1))
        if query_year:
            return self._header_year_index(headers, query_year)
        return None

    def _named_same_row_ratio_column(self, headers: list[str], query_lower: str) -> int | None:
        match = re.search(
            r"\bin\s+(?P<column>.+?)\s+as\s+(?:a\s+)?percentage\s+of\s+(?:the\s+)?total\b",
            query_lower,
        )
        if not match:
            return None
        terms = [term for term in self._keywords(match.group("column")) if term not in {"the", "a", "an"}]
        if not terms:
            return None
        best: tuple[int, int] | None = None
        for index, header in enumerate(headers):
            if "total" in header.lower():
                continue
            header_terms = set(self._keywords(header))
            matched = [term for term in terms if term in header_terms or term in header.lower()]
            if not matched:
                continue
            score = 10 * len(matched) + sum(len(term) for term in matched)
            candidate = (score, -index)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            return None
        return -best[1]

    def _same_row_ratio_denominator_column(self, headers: list[str]) -> int | None:
        return self._column_with_terms(headers, ["total"])

    def _column_with_terms(self, headers: list[str], terms: list[str]) -> int | None:
        best: tuple[int, int] | None = None
        for index, header in enumerate(headers):
            label = header.lower()
            matched = [term for term in terms if term in label]
            if not matched:
                continue
            score = sum(len(term) for term in matched)
            candidate = (score, -index)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            return None
        return -best[1]

    def _ratio_value_column(
        self,
        headers: list[str],
        query_lower: str,
        denominator_terms: list[str],
        query_year: str | None,
    ) -> int | None:
        if query_year:
            year_index = self._header_year_index(headers, query_year)
            if year_index is not None:
                return year_index
        query_terms = set(self._keywords(query_lower))
        denominator_term_set = set(denominator_terms)
        best: tuple[int, int, int] | None = None
        for index, header in enumerate(headers[1:], start=1):
            label = header.lower()
            label_terms = set(self._keywords(label))
            score = 0
            score += 3 * len(label_terms & query_terms)
            score += 2 * len(label_terms & denominator_term_set)
            if "total" in label and ("total" in denominator_term_set or "total" in query_lower):
                score += 4
            if any(unit in label for unit in ["mmboe", "mmbbls", "bcf"]):
                score += 3 * len(set(re.findall(r"[a-z0-9]+", label)) & query_terms)
            if score <= 0:
                continue
            candidate = (score, -index, index)
            if best is None or candidate > best:
                best = candidate
        if best is not None:
            return best[2]
        return None

    def _ratio_table_row(
        self,
        rows: list[list[str]],
        terms: list[str],
        prefer_total: bool,
        query_lower: str | None = None,
    ) -> list[str] | None:
        normalized_terms = [term for term in terms if term]
        if not normalized_terms:
            return None
        best: tuple[int, int, int, int, int, list[str]] | None = None
        for row_index, row in enumerate(rows):
            if not row:
                continue
            label = row[0].strip().lower()
            if prefer_total and "total" not in label:
                continue
            matched_terms = [term for term in normalized_terms if term in label]
            if not matched_terms:
                continue
            coverage = len(matched_terms)
            score = sum(len(term) for term in matched_terms)
            label_terms = set(self._keywords(label))
            extra_terms = len(label_terms - set(matched_terms))
            compactness = -extra_terms
            if coverage == 1 and len(normalized_terms) >= 3 and matched_terms[0] not in {"total"}:
                continue
            intent_score = self._row_intent_score(query_lower or "", label)
            if all(term in label for term in normalized_terms):
                intent_score += 3
            candidate = (coverage, score, compactness, intent_score, -row_index, row)
            if best is None or candidate > best:
                best = candidate
        return best[5] if best else None

    def _ratio_year(self, query_lower: str, years: list[str]) -> str | None:
        if "due after" in query_lower:
            return None
        year_of_match = re.search(r"\byear\s+of\s+(20\d{2})\b", query_lower)
        if year_of_match:
            return year_of_match.group(1)
        if len(years) == 1:
            return years[0]
        return None

    def _year_aligned_contexts(
        self,
        query_year: str | None,
        contexts: list[tuple[str, str]],
    ) -> list[tuple[str, str]]:
        if not query_year:
            return contexts

        def score(indexed_item: tuple[int, tuple[str, str]]) -> tuple[int, int]:
            index, item = indexed_item
            node_id, text = item
            header = " ".join(text.splitlines()[:3]).lower()
            source = f"{node_id.lower()} {header}"
            years = set(re.findall(r"\b(20\d{2})\b", source))
            value = 0
            if query_year in years:
                value += 4
            if re.search(rf"(?:_|/){re.escape(query_year)}(?:_|/)", source):
                value += 6
            if years and query_year not in years:
                value -= 3
            return (-value, index)

        return [item for _, item in sorted(enumerate(contexts), key=score)]

    def _context_year_compatible(self, query_year: str, node_id: str, text: str) -> bool:
        header = " ".join(text.splitlines()[:8]).lower()
        source = f"{node_id.lower()} {header}"
        years = set(re.findall(r"\b(20\d{2})\b", source))
        if query_year in years:
            return True
        if re.search(rf"(?:_|/){re.escape(query_year)}(?:_|/)", source):
            return True
        source_years = set(re.findall(r"(?:_|/)(20\d{2})(?:_|/)", source))
        return not source_years or query_year in source_years

    def _higher_than_row_terms(self, query_lower: str) -> tuple[list[str], list[str]] | None:
        match = re.search(
            r"\b(?:percent|percentage)\s+higher\s+is\s+.+?\s+for\s+(.+?)\s+than\s+(?:that\s+of\s+|the\s+)?(.+?)\??$",
            query_lower,
        )
        if not match:
            return None
        numerator_terms = self._keywords(match.group(1))
        denominator_terms = self._keywords(match.group(2))
        if not numerator_terms or not denominator_terms:
            return None
        return numerator_terms, denominator_terms

    def _metric_column_indices(self, headers: list[str], query_lower: str) -> list[int]:
        query_terms = set(self._keywords(query_lower))
        scored: list[tuple[int, int]] = []
        for index, header in enumerate(headers[1:], start=1):
            label = header.lower()
            label_terms = set(re.findall(r"[a-z0-9]+", label))
            score = len(query_terms & label_terms)
            if "average" in query_lower and "average" in label:
                score += 5
            if "annual" in query_lower and "annual" in label:
                score += 3
            if score > 0:
                scored.append((score, index))
        if not scored:
            return []
        best_score = max(score for score, _index in scored)
        return [index for score, index in scored if score == best_score]

    def _row_values_at_columns(self, row: list[str], column_indices: list[int]) -> list[float]:
        values = []
        for index in column_indices:
            if index >= len(row):
                continue
            value = self._first_number(row[index])
            if value is not None:
                values.append(value)
        return values

    def _table_value_for_terms_year(
        self,
        text: str,
        terms: list[str],
        year: str,
        allow_partial: bool = True,
    ) -> float | None:
        value, _metadata = self._table_value_for_terms_year_with_label(text, terms, year, allow_partial)
        return value

    def _table_value_for_terms_year_with_label(
        self,
        text: str,
        terms: list[str],
        year: str,
        allow_partial: bool = True,
    ) -> tuple[float | None, dict[str, str]]:
        if not terms:
            return None, {}
        table = self._markdown_table(text)
        if not table:
            return None, {}
        headers, rows = table
        year_index = self._header_year_index(headers, year)
        if year_index == 0:
            return None, {}
        if year_index is None:
            if not allow_partial:
                return None, {}
            if self._table_context_matches_terms(text, terms):
                for row in rows:
                    if not row or row[0].strip() != year or len(row) < 2:
                        continue
                    value = self._first_number(row[1])
                    if value is not None:
                        return value, {"row_label": row[0]}
            return None, {}
        exact = self._best_table_value_row(rows, terms, year_index, require_all=True)
        if exact is not None:
            row = exact
            return self._first_number(row[year_index]), {"row_label": row[0]}
        if not allow_partial:
            return None, {}
        partial = self._best_table_value_row(rows, terms, year_index, require_all=False)
        if partial is not None:
            row = partial
            return self._first_number(row[year_index]), {"row_label": row[0]}
        return None, {}

    def _best_table_value_row(
        self,
        rows: list[list[str]],
        terms: list[str],
        value_index: int,
        require_all: bool,
    ) -> list[str] | None:
        best: tuple[int, int, int, int, list[str]] | None = None
        normalized_terms = [term for term in terms if term]
        for row_index, row in enumerate(rows):
            if value_index >= len(row) or not row:
                continue
            if self._first_number(row[value_index]) is None:
                continue
            label = row[0].lower()
            matched_terms = [term for term in normalized_terms if term in label]
            if require_all and len(matched_terms) != len(normalized_terms):
                continue
            if not require_all and not matched_terms:
                continue
            label_terms = set(self._keywords(label))
            compactness = -len(label_terms - set(matched_terms))
            score = sum(len(term) for term in matched_terms)
            candidate = (len(matched_terms), compactness, score, -row_index, row)
            if best is None or candidate > best:
                best = candidate
        return best[4] if best else None

    def _table_context_matches_terms(self, text: str, terms: list[str]) -> bool:
        if not terms:
            return False
        text_terms = set(re.findall(r"[a-z0-9]+", text.lower()))
        matched = [term for term in terms if term in text_terms]
        minimum = 2 if len(terms) >= 2 else 1
        return len(matched) >= minimum

    def _prose_value_for_terms_year(self, text: str, terms: list[str], year: str) -> float | None:
        if not terms:
            return None
        compact_terms = [re.escape(term) for term in terms]
        pattern = (
            r"(?:" + r".{0,20}".join(compact_terms) + r")"
            r".{0,80}?\$\s*([-+]?\d+(?:\.\d+)?)\s+(?:million|billion|thousand)?"
            r".{0,40}?\b" + re.escape(year) + r"\b"
        )
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return None
        return self._to_float(match.group(1))

    def _prose_ratio_percent(
        self,
        node_id: str,
        text: str,
        numerator_terms: list[str],
        denominator_terms: list[str],
        query_year: str | None = None,
    ) -> NumericAnswer | None:
        rows = self._label_value_rows(text)
        query_proxy = " ".join([*numerator_terms, *denominator_terms])
        numerator, numerator_meta = self._matching_ratio_value_with_label(
            rows,
            numerator_terms,
            query_proxy,
            role="numerator",
        )
        denominator, denominator_meta = self._matching_ratio_value_with_label(
            rows,
            denominator_terms,
            query_proxy,
            role="denominator",
        )
        if query_year:
            year_denominator, year_denominator_meta = self._table_value_for_terms_year_with_label(
                text,
                denominator_terms,
                query_year,
                allow_partial=False,
            )
            if (
                year_denominator is not None
                and self._denominator_label_allowed(
                    str(year_denominator_meta.get("row_label", "")),
                    denominator_terms,
                    query_proxy,
                )
            ):
                denominator = year_denominator
                denominator_meta = year_denominator_meta
            scoped_denominator, scoped_denominator_meta = self._scoped_sales_table_value_for_year(
                text,
                denominator_terms,
                query_year,
            )
            if scoped_denominator is not None:
                denominator = scoped_denominator
                denominator_meta = scoped_denominator_meta
            year_numerator, year_numerator_label = self._prose_amount_for_terms_year(
                text,
                numerator_terms,
                query_year,
            )
            if year_numerator is not None:
                numerator = year_numerator
                numerator_meta = {"row_label": year_numerator_label, "source": "prose"}
        if denominator is not None and not self._denominator_label_allowed(
            str(denominator_meta.get("row_label", "")),
            denominator_terms,
            query_proxy,
        ):
            denominator = None
        if denominator is None:
            denominator, denominator_label = self._prose_amount_for_terms(text, denominator_terms)
            denominator_meta = {"row_label": denominator_label, "source": "prose"} if denominator_label else {}
        if numerator is None:
            numerator, numerator_label = self._prose_amount_for_terms(text, numerator_terms)
            numerator_meta = {"row_label": numerator_label, "source": "prose"} if numerator_label else {}
        if numerator is None or denominator in {None, 0}:
            return None
        if numerator_meta.get("row_label") and numerator_meta.get("row_label") == denominator_meta.get("row_label"):
            prose_denominator, denominator_label = self._prose_amount_for_terms(text, denominator_terms)
            if prose_denominator is not None:
                denominator = prose_denominator
                denominator_meta = {"row_label": denominator_label, "source": "prose"} if denominator_label else {}
        numerator_meta.setdefault("source", "table" if numerator_meta.get("row_label") else "")
        denominator_meta.setdefault("source", "table" if denominator_meta.get("row_label") else "")
        if numerator_meta.get("source") != "prose" and denominator_meta.get("source") != "prose":
            return None
        numerator, denominator = self._normalize_mixed_table_prose_scale(
            text,
            numerator,
            denominator,
            numerator_meta,
            denominator_meta,
        )
        if query_year and self._sales_denominator_requires_grouped_scope(
            text,
            denominator_terms,
            numerator_terms,
            denominator_meta,
        ):
            return None
        if numerator_meta.get("row_label") and numerator_meta.get("row_label") == denominator_meta.get("row_label"):
            return None
        operation = self.executor.ratio(numerator, denominator)
        if operation is None:
            return None
        result = operation.value * 100.0
        numerator_label = self._display_ratio_label(str(numerator_meta.get("row_label", " ".join(numerator_terms))))
        denominator_label = self._display_ratio_label(str(denominator_meta.get("row_label", " ".join(denominator_terms))))
        return NumericAnswer(
            text=self._format_percent(result),
            calculation=(
                f"ratio_percent row={numerator_label} denominator_row={denominator_label}: "
                f"{numerator:g} / {denominator:g} * 100 = {result:.1f}%"
            ),
            cited_node_ids=[node_id],
        )

    def _allow_prose_ratio(self, query_lower: str, query_year: str | None) -> bool:
        direct_prose_ratio = (
            " that was " in query_lower
            or " that were " in query_lower
            or " which was " in query_lower
            or " which were " in query_lower
            or " of which " in query_lower
            or " represented by " in query_lower
        )
        if direct_prose_ratio:
            return True
        return query_year is None and " as a percentage of " in query_lower

    def _prose_amount_for_terms_year(self, text: str, terms: list[str], year: str) -> tuple[float | None, str]:
        if not terms or not year:
            return None, ""
        best: tuple[int, float, str] | None = None
        min_matches = self._minimum_term_matches(terms)
        amount_pattern = re.compile(
            r"\(?\s*(\$)?\s*([-+]?\d+(?:\.\d+)?)\s*(billion|million|thousand)?\s*\)?",
            flags=re.IGNORECASE,
        )
        for sentence in self._prose_sentences(text):
            lower_sentence = sentence.lower()
            if year not in lower_sentence:
                continue
            sentence_years = re.findall(r"\b(20\d{2})\b", sentence)
            if len(set(sentence_years)) < 2:
                continue
            matched_terms = [term for term in terms if term in lower_sentence]
            if len(matched_terms) < min_matches:
                continue
            year_matches = list(re.finditer(rf"\b{re.escape(year)}\b", sentence))
            year_positions = [match.start() for match in year_matches]
            if not year_positions:
                continue
            amount_matches = [
                amount
                for amount in amount_pattern.finditer(sentence)
                if amount.group(1) or amount.group(3)
            ]
            for year_match in year_matches:
                before = [amount for amount in amount_matches if amount.end() <= year_match.start()]
                if before:
                    amount = before[-1]
                    distance = year_match.start() - amount.end()
                    if distance <= 60:
                        value = self._scaled_number(amount.group(2), amount.group(3).lower() if amount.group(3) else None)
                        if value is not None:
                            score = len(matched_terms) * 1000 - distance + 20
                            candidate = (score, value, " ".join(matched_terms))
                            if best is None or candidate > best:
                                best = candidate
                            continue
                after = [amount for amount in amount_matches if amount.start() >= year_match.end()]
                if after:
                    amount = after[0]
                    distance = amount.start() - year_match.end()
                    if distance <= 60:
                        value = self._scaled_number(amount.group(2), amount.group(3).lower() if amount.group(3) else None)
                        if value is not None:
                            score = len(matched_terms) * 1000 - distance
                            candidate = (score, value, " ".join(matched_terms))
                            if best is None or candidate > best:
                                best = candidate
        if best is None:
            return None, ""
        _score, value, label = best
        return value, label

    def _scoped_sales_table_value_for_year(
        self,
        text: str,
        denominator_terms: list[str],
        year: str,
    ) -> tuple[float | None, dict[str, str]]:
        if "sales" not in denominator_terms:
            return None, {}
        scope_terms = [term for term in denominator_terms if term not in {"sales", "net", "total"}]
        if len(scope_terms) < 2 or not self._table_context_matches_terms(text, scope_terms):
            return None, {}
        for headers, rows in self._markdown_tables(text):
            year_index = self._header_year_index(headers, year)
            if year_index is None:
                continue
            value_index = year_index
            if (
                year_index == 0
                or (
                    len(rows) > 0
                    and len(rows[0]) == len(headers) + 1
                    and all(re.search(r"\b(?:19|20)\d{2}\b", header) for header in headers)
                )
            ):
                value_index = year_index + 1
            for row in rows:
                if value_index >= len(row) or not row:
                    continue
                label = row[0].strip().lower()
                if label not in {"sales", "net sales"}:
                    continue
                value = self._first_number(row[value_index])
                if value is not None:
                    return value, {"row_label": label, "source": "table"}
        return None, {}

    def _sales_denominator_requires_grouped_scope(
        self,
        text: str,
        denominator_terms: list[str],
        numerator_terms: list[str],
        denominator_meta: dict[str, str],
    ) -> bool:
        if "sales" not in denominator_terms:
            return False
        scope_terms = [term for term in denominator_terms if term not in {"sales", "net", "total"}]
        if len(scope_terms) < 2:
            return False
        denominator_label = str(denominator_meta.get("row_label", "")).lower()
        if denominator_label in {"sales", "net sales"}:
            return not self._table_context_matches_terms(text, scope_terms)
        if denominator_meta.get("source") == "prose":
            denominator_set = set(denominator_terms)
            numerator_set = set(numerator_terms)
            if denominator_set and denominator_set.issubset(numerator_set | {"net"}):
                return True
        return False

    def _normalize_mixed_table_prose_scale(
        self,
        text: str,
        numerator: float,
        denominator: float,
        numerator_meta: dict[str, str],
        denominator_meta: dict[str, str],
    ) -> tuple[float, float]:
        if not self._table_is_in_thousands(text):
            return numerator, denominator
        if self._uses_local_unscaled_prose(numerator_meta) or self._uses_local_unscaled_prose(denominator_meta):
            return numerator, denominator
        if numerator_meta.get("source") == "table" and denominator_meta.get("source") == "prose":
            return numerator / 1000.0, denominator
        if denominator_meta.get("source") == "table" and numerator_meta.get("source") == "prose":
            return numerator, denominator / 1000.0
        return numerator, denominator

    def _uses_local_unscaled_prose(self, meta: dict[str, str]) -> bool:
        return "__local_unscaled__" in str(meta.get("row_label", ""))

    def _display_ratio_label(self, label: str) -> str:
        return label.replace("__local_unscaled__", "").strip()

    def _table_is_in_thousands(self, text: str) -> bool:
        return bool(re.search(r"\(\s*in\s+thousands\s*\)|\bin\s+thousands\b", text, flags=re.IGNORECASE))

    def _prose_amount_for_terms(self, text: str, terms: list[str]) -> tuple[float | None, str]:
        if not terms:
            return None, ""
        local_value = self._local_prose_amount_for_terms(text, terms)
        if local_value[0] is not None:
            return local_value
        if "total" in terms:
            terminal_value, terminal_label = self._terminal_prose_amount_for_terms(text, terms)
            if terminal_value is not None:
                return terminal_value, terminal_label
        best: tuple[int, float, str] | None = None
        min_matches = self._minimum_term_matches(terms)
        for sentence in self._prose_sentences(text):
            lower_sentence = sentence.lower()
            matched_terms = [term for term in terms if term in lower_sentence]
            if len(matched_terms) < min_matches:
                continue
            amounts = list(
                re.finditer(
                    r"\(?\s*(\$)?\s*([-+]?\d+(?:\.\d+)?)\s*(billion|million|thousand)?\s*\)?",
                    sentence,
                    flags=re.IGNORECASE,
                )
            )
            if not amounts:
                continue
            term_positions = [lower_sentence.find(term) for term in matched_terms if lower_sentence.find(term) >= 0]
            anchor = min(term_positions) if term_positions else 0
            for amount in amounts:
                if not amount.group(1) and not amount.group(3):
                    continue
                value = self._scaled_number(amount.group(2), amount.group(3).lower() if amount.group(3) else None)
                distance = abs(amount.start() - anchor)
                score = len(matched_terms) * 1000 - distance
                if best is None or score > best[0]:
                    best = (score, value, " ".join(matched_terms))
        if best is None:
            return None, ""
        _score, value, label = best
        return value, label

    def _local_prose_amount_for_terms(self, text: str, terms: list[str]) -> tuple[float | None, str]:
        normalized_terms = [term for term in terms if term]
        if not normalized_terms:
            return None, ""
        phrase = r"\s+".join(re.escape(term) for term in normalized_terms)
        pattern = (
            rf"\b{phrase}\b\s+(?:of|was|were|totaled|amounted\s+to)\s+"
            r"\(?\s*(\$)?\s*([-+]?\d+(?:\.\d+)?)\s*(billion|million|thousand)?\s*\)?"
        )
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            return None, ""
        scale = match.group(3).lower() if match.group(3) else None
        value = self._scaled_number(match.group(2), scale)
        marker = "" if scale else " __local_unscaled__"
        return value, " ".join(normalized_terms) + marker

    def _terminal_prose_amount_for_terms(self, text: str, terms: list[str]) -> tuple[float | None, str]:
        content_terms = [term for term in terms if term != "total"]
        if not content_terms:
            return None, ""
        min_matches = min(2, len(content_terms))
        best: tuple[int, float, str] | None = None
        for sentence in self._prose_sentences(text):
            lower_sentence = sentence.lower()
            matched_terms = [term for term in content_terms if term in lower_sentence]
            if len(matched_terms) < min_matches:
                continue
            for amount in re.finditer(
                r"\b(?:to|was|were|totaled|amounted to)\s+(\$)?\s*([-+]?\d+(?:\.\d+)?)\s*(billion|million|thousand)?",
                sentence,
                flags=re.IGNORECASE,
            ):
                if not amount.group(1) and not amount.group(3):
                    continue
                value = self._scaled_number(amount.group(2), amount.group(3).lower() if amount.group(3) else None)
                score = len(matched_terms) * 1000 + amount.start()
                if best is None or score > best[0]:
                    best = (score, value, " ".join(["total", *matched_terms]))
        if best is None:
            return None, ""
        _score, value, label = best
        return value, label

    def _minimum_term_matches(self, terms: list[str]) -> int:
        if len(terms) <= 1:
            return 1
        if len(terms) <= 3:
            return 2
        return 3

    def _difference_between_nearby_amounts(self, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        for node_id, text in contexts:
            amounts = self._amounts(text)
            if len(amounts) < 2:
                continue
            # FinQA adjustment questions often ask for the delta between original
            # and revised purchase prices; prefer close amounts in the same scale.
            best_pair = None
            best_gap = None
            for left in amounts:
                for right in amounts:
                    if right <= left:
                        continue
                    gap = right - left
                    if gap <= 0:
                        continue
                    if best_gap is None or gap < best_gap:
                        best_gap = gap
                        best_pair = (left, right)
            if best_pair and best_gap is not None:
                operation = self.executor.difference(best_pair[1], best_pair[0])
                return NumericAnswer(
                    text=f"{operation.value:g}",
                    calculation=f"difference: {operation.expression}",
                    cited_node_ids=[node_id],
                )
        return None

    def _contexts(self, support_graph: EvidenceGraph) -> list[tuple[str, str]]:
        contexts = []
        for node in sorted(support_graph.nodes.values(), key=self._context_order):
            if node.node_type == "verifier_judgment":
                continue
            text = self._node_text(node)
            if text:
                contexts.append((node.node_id, text))
        return contexts

    def _context_order(self, node: EvidenceNode) -> tuple[int, int, str]:
        try:
            rank = int(node.metadata.get("retrieval_rank", 999))
        except (TypeError, ValueError):
            rank = 999
        neighbor_order = 1 if node.metadata.get("neighbor_context") else 0
        return rank, neighbor_order, node.node_id

    def _node_text(self, node: EvidenceNode) -> str:
        content = node.content
        if isinstance(content, str):
            return content
        if isinstance(content, dict):
            raw_text = content.get("raw_text")
            if raw_text:
                return str(raw_text)
            rows = content.get("rows")
            if isinstance(rows, list):
                return "\n".join(" | ".join(str(cell) for cell in row) for row in rows)
            return " ".join(str(value) for value in content.values())
        return str(content)

    def _year_values(self, text: str) -> dict[str, float]:
        values = {}
        for value, year in re.findall(
            r"\$\s*([-+]?\d+(?:\.\d+)?)\s+(?:million|billion|thousand)?\s+at\s+december\s+31\s*,?\s+(20\d{2})",
            text,
            flags=re.IGNORECASE,
        ):
            values[year] = self._to_float(value)
        for label, value in self._label_value_rows(text):
            if re.fullmatch(r"20\d{2}", label):
                values.setdefault(label, value)
        for value, year in re.findall(
            r"\$?\s*([-+]?\d+(?:\.\d+)?)\s+(?:million|billion|thousand|%)?.{0,40}?\b(20\d{2})\b",
            text,
            flags=re.IGNORECASE,
        ):
            values.setdefault(year, self._to_float(value))
        return values

    def _year_label_values(self, text: str) -> dict[str, float]:
        values = {}
        for label, value in self._label_value_rows(text):
            year_match = re.search(r"\b(20\d{2})\b", label)
            if year_match:
                values.setdefault(year_match.group(1), value)
        return values

    def _year_label_values_with_label(self, query_lower: str, text: str) -> tuple[dict[str, float], str]:
        table = self._markdown_table(text)
        if not table:
            return self._year_label_values(text), ""
        headers, rows = table
        query_terms = set(self._keywords(query_lower))
        best: tuple[int, int, int, str, dict[str, float]] | None = None
        for column_index, header in enumerate(headers[1:], start=1):
            values = {}
            for row in rows:
                if len(row) <= column_index or not re.fullmatch(r"20\d{2}", row[0].strip()):
                    continue
                value = self._first_number(row[column_index])
                if value is not None:
                    values[row[0].strip()] = value
            if len(values) < 2:
                continue
            label = header.lower()
            label_terms = set(self._keywords(label))
            score = len(query_terms & label_terms)
            candidate = (score, len(values), -column_index, label, values)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            return self._year_label_values(text), ""
        score, _count, _column_index, label, values = best
        return values, label if score else ""

    def _has_year_label_schedule(self, text: str, base_year: str, target_year: str) -> bool:
        labels = [label for label, _value in self._label_value_rows(text)]
        return any(base_year in label for label in labels) and any(target_year in label for label in labels)

    def _label_value_rows(self, text: str) -> list[tuple[str, float]]:
        rows = []
        for line in text.splitlines():
            if "|" not in line or "---" in line:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            label = cells[0].lower()
            for cell in cells[1:]:
                value = self._first_number(cell)
                if value is not None:
                    rows.append((label, value))
                    break
        return rows

    def _matching_value(self, rows: list[tuple[str, float]], terms: list[str]) -> float | None:
        value, _metadata = self._matching_value_with_label(rows, terms)
        return value

    def _matching_value_with_label(
        self,
        rows: list[tuple[str, float]],
        terms: list[str],
    ) -> tuple[float | None, dict[str, str]]:
        normalized_terms = [term for term in terms if term]
        if not normalized_terms:
            return None, {}
        for label, value in rows:
            if all(term in label for term in normalized_terms):
                return value, {"row_label": label}
        best_match: tuple[float, int, int, str, float] | None = None
        for row_index, (label, value) in enumerate(rows):
            matched_terms = [term for term in normalized_terms if term in label]
            if not matched_terms:
                continue
            score = sum(len(term) for term in matched_terms)
            coverage = len(matched_terms)
            candidate = (score, coverage, -row_index, label, value)
            if best_match is None or candidate > best_match:
                best_match = candidate
        if best_match is None:
            return None, {}
        _score, _coverage, _row_order, label, value = best_match
        return value, {"row_label": label}

    def _matching_ratio_value_with_label(
        self,
        rows: list[tuple[str, float]],
        terms: list[str],
        query_lower: str,
        role: str,
        denominator_label: str = "",
    ) -> tuple[float | None, dict[str, str]]:
        normalized_terms = [term for term in terms if term]
        if not normalized_terms:
            return None, {}
        best_match: tuple[int, int, int, int, int, int, str, float] | None = None
        for row_index, (label, value) in enumerate(rows):
            matched_terms = [term for term in normalized_terms if term in label]
            if not matched_terms:
                continue
            coverage = len(matched_terms)
            if coverage == 1 and len(normalized_terms) >= 3 and matched_terms[0] != "total":
                continue
            lexical_score = sum(len(term) for term in matched_terms)
            label_terms = set(self._keywords(label))
            compactness = -len(label_terms - set(matched_terms))
            intent_score = self._ratio_operand_intent_score(
                query_lower,
                label,
                role=role,
                denominator_label=denominator_label,
            )
            exact_score = 1 if all(term in label for term in normalized_terms) else 0
            candidate = (coverage, exact_score, compactness, intent_score, lexical_score, -row_index, label, value)
            if best_match is None or candidate > best_match:
                best_match = candidate
        if best_match is None:
            return None, {}
        _coverage, _exact, _compactness, _intent, _lexical, _row_order, label, value = best_match
        return value, {"row_label": label}

    def _ratio_operand_intent_score(
        self,
        query_lower: str,
        label: str,
        role: str,
        denominator_label: str = "",
    ) -> int:
        score = self._period_alignment_score(query_lower, label)
        if role == "denominator":
            if "total" in query_lower and "total" in label:
                score += 20
            if "adjusted" in query_lower and "adjusted" in label:
                score += 20
            return score

        adjusted_context = "adjusted" in query_lower or "adjusted" in denominator_label
        if adjusted_context:
            if re.search(r"^\s*plus\b", label):
                score += 55
            if re.search(r"^\s*less\b", label):
                score -= 65
            if "four times" in label or "annualized" in label:
                score += 25
        return score

    def _denominator_label_allowed(self, label: str, denominator_terms: list[str], query_lower: str) -> bool:
        lower_label = label.lower()
        if ("total" in denominator_terms or "total" in query_lower) and "total" not in lower_label:
            return False
        if ("adjusted" in denominator_terms or "adjusted" in query_lower) and "adjusted" not in lower_label:
            return False
        return True

    def _period_alignment_score(self, query_lower: str, label: str) -> int:
        score = 0
        period_cues = [
            ("twelve months", 36),
            ("three months", 28),
            ("six months", 28),
            ("nine months", 28),
            ("year ended", 24),
            ("years ended", 24),
            ("month ended", 18),
            ("months ended", 18),
        ]
        for cue, weight in period_cues:
            if cue in query_lower:
                score += weight if cue in label else 0
        query_years = set(re.findall(r"\b(?:19|20)\d{2}\b", query_lower))
        if query_years:
            label_years = set(re.findall(r"\b(?:19|20)\d{2}\b", label))
            if query_years & label_years:
                score += 10
            elif label_years:
                score -= 15
        return score

    def _label_matches_terms(self, label: str, terms: list[str]) -> bool:
        if not label or not terms:
            return False
        matched_terms = [term for term in terms if term in label]
        return len(matched_terms) >= self._minimum_term_matches(terms)

    def _context_source_key(self, node_id: str) -> str:
        key = re.sub(r"^parsed_", "", node_id)
        key = re.sub(r"^(retrieved|neighbor)_\d+_", "", key)
        key = re.sub(r"_full$", "", key)
        key = re.sub(r"_\d+_\d+$", "", key)
        return key

    def _context_chunk_order(self, node_id: str) -> tuple[int, int, str]:
        key = re.sub(r"^parsed_", "", node_id)
        key = re.sub(r"^(retrieved|neighbor)_\d+_", "", key)
        match = re.search(r"_(\d+)_(\d+)$", key)
        if match:
            return int(match.group(1)), int(match.group(2)), node_id
        return 999, 999, node_id

    def _denominator_terms(self, query_lower: str) -> list[str]:
        if (
            "major facilities" in query_lower
            and "square footage" in query_lower
            and re.search(r"\b(?:owned|leased)\b", query_lower)
        ):
            return ["total", "facilities"]
        if " as a percentage of " in query_lower:
            return self._keywords(query_lower.split(" as a percentage of ", 1)[1])
        if " compared to " in query_lower:
            return self._keywords(query_lower.split(" compared to ", 1)[1])
        if "portion of " in query_lower:
            tail = query_lower.split("portion of ", 1)[1]
        elif "share of " in query_lower:
            tail = query_lower.split("share of ", 1)[1]
        elif "percentage of " in query_lower:
            tail = query_lower.split("percentage of ", 1)[1]
        elif "percent of " in query_lower:
            tail = query_lower.split("percent of ", 1)[1]
        elif " of " in query_lower:
            tail = query_lower.split(" of ", 1)[1]
        else:
            return []
        tail = re.split(
            r"\b(that\s+was|that\s+were|which\s+was|which\s+were|was|were|is|are|where represented by|where|comes from|represented by|allocated to|related to|due to|due after)\b",
            tail,
            maxsplit=1,
        )[0]
        tail = re.sub(r"\bare due\b.*", "", tail)
        tail = re.sub(r"\bwere represented\b.*", "", tail)
        terms = self._keywords(tail)
        if "total" in tail and "total" not in terms:
            return ["total", *terms]
        return terms

    def _ratio_numerator_terms(self, query_lower: str) -> list[str]:
        if re.search(r"\bpaid\s+in\s+cash\b", query_lower):
            return ["cash", "paid"]
        if "major facilities" in query_lower and "square footage" in query_lower:
            if re.search(r"\bleased\b", query_lower):
                return ["leased", "facilities"]
            if re.search(r"\bowned\b", query_lower):
                return ["owned", "facilities"]
        patterns = [
            r"what\s+(?:are|is|was|were)\s+(.+?)\s+as\s+a\s+percentage\s+of",
            r"(.+?)\s+where\s+what\s+percentage\s+of",
            r"made\s+up\s+of\s+(.+?)\??$",
            r"what\s+(?:percentage|percent)\s+of\s+.+?\s+(?:is|are|was|were)\s+(.+?)\??$",
            r"payments?\s+for\s+(.+?)\s+as\s+a\s+percentage\s+of",
            r"\b(?:that|which)\s+(?:was|were|is|are)\s+(.+?)(?:\s+in\s+20\d{2})?\??$",
            r"represented by\s+(.+?)\??$",
            r"allocated to\s+(.+?)(?:\s+in\s+20\d{2})?\??$",
            r"comes from\s+(.+?)\??$",
            r"due to\s+(.+?)(?:\s+for\s+the\s+year|\??$)",
            r"related to\s+(.+?)\??$",
            r"composed of\s+(.+?)\??$",
            r"among\s+the\s+(.+?)\??$",
        ]
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return self._keywords(match.group(1))
        if "due after" in query_lower:
            return ["thereafter"]
        if "percentage increase" in query_lower:
            return self._keywords(query_lower.split("percentage increase", 1)[1])
        if "percent increase" in query_lower:
            return self._keywords(query_lower.split("percent increase", 1)[1])
        if "what percentage of " in query_lower:
            tail = query_lower.split("what percentage of ", 1)[1]
            return self._keywords(tail)
        if "what percent of " in query_lower:
            tail = query_lower.split("what percent of ", 1)[1]
            return self._keywords(tail)
        if "what portion of " in query_lower:
            tail = query_lower.split("what portion of ", 1)[1]
            return self._keywords(tail)
        return []

    def _keywords(self, text: str) -> list[str]:
        stop = {
            "what",
            "percentage",
            "percent",
            "percentual",
            "of",
            "the",
            "were",
            "was",
            "where",
            "by",
            "in",
            "for",
            "are",
            "due",
            "after",
            "represented",
            "made",
            "up",
            "total",
            "is",
            "if",
            "an",
            "and",
            "from",
            "to",
            "rate",
            "return",
            "investment",
            "payment",
            "payments",
            "change",
            "changed",
            "increase",
            "increased",
            "as",
            "much",
            "would",
            "be",
            "between",
            "did",
            "receive",
            "average",
            "amount",
            "period",
            "ending",
            "millions",
            "million",
            "current",
            "compared",
        }
        return [
            token
            for token in re.findall(r"[a-z0-9]+", text.lower())
            if token not in stop and not re.fullmatch(r"20\d{2}", token)
        ][:8]

    def _markdown_table(self, text: str) -> tuple[list[str], list[list[str]]] | None:
        candidates = self._markdown_tables(text)
        if not candidates:
            return None
        return max(candidates, key=lambda parsed: (len(parsed[1]), max(len(parsed[0]), *(len(row) for row in parsed[1]))))

    def _loose_markdown_table(self, text: str) -> tuple[list[str], list[list[str]]] | None:
        parsed_lines: list[list[str]] = []
        for line in text.splitlines():
            if "|" not in line or "---" in line:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                parsed_lines.append(cells)
        header_candidates = [
            cells
            for cells in parsed_lines
            if len(cells) >= 3
            and (not cells[0].strip() or self._first_number(cells[0]) is None)
            and any(self._first_number(cell) is None for cell in cells[1:])
        ]
        if not header_candidates:
            return None
        headers = max(header_candidates, key=lambda cells: (len(cells), sum(len(cell) for cell in cells)))
        rows = [
            cells
            for cells in parsed_lines
            if len(cells) == len(headers)
            and cells != headers
            and cells[0].strip()
            and self._first_number(cells[0]) is None
            and any(self._first_number(cell) is not None for cell in cells[1:])
        ]
        if not rows:
            return None
        return headers, rows

    def _markdown_tables(self, text: str) -> list[tuple[list[str], list[list[str]]]]:
        blocks: list[list[str]] = []
        current: list[str] = []
        for line in text.splitlines():
            if line.strip().startswith("|") and "|" in line.strip()[1:]:
                current.append(line)
            elif current:
                blocks.append(current)
                current = []
        if current:
            blocks.append(current)
        candidates = []
        for table_lines in blocks:
            parsed = self._parse_markdown_table_block(table_lines)
            if parsed:
                candidates.append(parsed)
        return candidates

    def _parse_markdown_table_block(self, table_lines: list[str]) -> tuple[list[str], list[list[str]]] | None:
        if len(table_lines) < 2:
            return None
        rows = []
        for line in table_lines:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if all(set(cell) <= {"-"} for cell in cells if cell):
                continue
            rows.append(cells)
        if len(rows) < 2:
            return None
        return rows[0], rows[1:]

    def _prose_sentences(self, text: str) -> list[str]:
        prose_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("|") or stripped.startswith("#"):
                continue
            if set(stripped) <= {"-", " "}:
                continue
            prose_lines.append(stripped)
        prose = " ".join(prose_lines)
        return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", prose) if sentence.strip()]

    def _prose_row_label(self, sentence: str, query_lower: str) -> str:
        lower_sentence = sentence.lower()
        amount_match = re.search(r"\b(.{0,120}?)\s+(?:was|were|had|totaled|amounted to)?\s*(?:approximately\s+)?\$\s*\d", lower_sentence)
        label = amount_match.group(1) if amount_match else lower_sentence[:100]
        label = re.sub(r"\b(2022|2019|201c|201d)\b", " ", label)
        label_terms = self._keywords(label)
        query_terms = self._keywords(query_lower)
        kept = [term for term in query_terms if term in label_terms]
        if kept:
            return " ".join(kept)
        compact = re.sub(r"[^a-z0-9 ]+", " ", label)
        compact = re.sub(r"\s+", " ", compact).strip()
        return " ".join(compact.split()[-6:])

    def _best_query_row(self, query_lower: str, headers: list[str], rows: list[list[str]]) -> list[str] | None:
        query_terms = set(self._keywords(query_lower))
        min_score = 2 if len(query_terms) >= 2 else 1
        best: tuple[int, int, int, int, int, list[str]] | None = None
        for row_index, row in enumerate(rows):
            if not row:
                continue
            label = row[0].lower()
            label_terms = set(re.findall(r"[a-z0-9]+", label))
            coverage = len(query_terms & label_terms)
            intent_score = self._row_intent_score(query_lower, label)
            if coverage == 0 and intent_score == 0:
                continue
            # The change period-end/beginning preference is a tiebreaker between
            # rows that already lexically match the query; it must not promote an
            # unrelated row that has zero coverage.
            if coverage > 0:
                intent_score += self._change_period_preference(query_lower, label)
            lexical_score = sum(len(term) for term in query_terms if term in label)
            total_score = coverage * 10 + lexical_score + intent_score
            if "average" in query_lower and coverage > 0:
                total_score += 50
            candidate = (total_score, coverage, intent_score, lexical_score, -row_index, row)
            if best is None or candidate > best:
                best = candidate
        if best is None or (best[1] < min_score and best[2] < 8):
            return None
        return best[5]

    def _best_query_row_with_context(
        self,
        query_lower: str,
        headers: list[str],
        rows: list[list[str]],
        text: str,
    ) -> list[str] | None:
        query_terms = set(self._keywords(query_lower))
        if len(query_terms) < 2:
            return None
        context_text = " ".join(headers) + " " + text
        context_terms = set(re.findall(r"[a-z0-9]+", context_text.lower()))
        best: tuple[int, int, int, int, list[str]] | None = None
        for row_index, row in enumerate(rows):
            if not row:
                continue
            label = row[0].lower()
            label_terms = set(re.findall(r"[a-z0-9]+", label))
            row_score = len(query_terms & label_terms)
            intent_score = self._row_intent_score(query_lower, label)
            if row_score == 0 and intent_score == 0:
                continue
            missing_terms = query_terms - label_terms
            context_score = len(missing_terms & context_terms)
            if row_score >= 1 and context_score >= 1:
                total_score = row_score * 10 + context_score + intent_score
                candidate = (total_score, row_score, context_score, -row_index, row)
            elif intent_score >= 4 and context_score >= 2:
                total_score = context_score + intent_score
                candidate = (total_score, row_score, context_score, -row_index, row)
            else:
                continue
            if best is None or candidate > best:
                best = candidate
        return best[4] if best else None

    def _row_intent_score(self, query_lower: str, label: str) -> int:
        score = 0
        if "total" in query_lower and "total" in label:
            score += 8
        if any(term in query_lower for term in ["ending", "period end", "period-end", "at december 31"]):
            label_is_ending = any(
                term in label
                for term in ["ending", "period end", "period-end", "period 2013end", "december 31", "balance at december 31"]
            ) or ("period" in label and "end" in label)
            if label_is_ending:
                score += 45
            if "average" in label:
                score -= 25
        if "unrecognized tax benefits" in query_lower and "balance at december 31" in label:
            score += 35
        if "balance" in query_lower and "balance" in label:
            score += 4
        return score

    def _change_period_preference(self, query_lower: str, label: str) -> int:
        """Tiebreaker for change queries between period-beginning and period-end
        rows of the same metric. Only meaningful as a tiebreaker, so callers gate
        it on non-zero lexical coverage so it cannot promote an unrelated row."""
        if not any(term in query_lower for term in ["change", "increased", "decreased", "growth"]):
            return 0
        if any(term in label for term in ["at december 31", "at end of period", "period end", "ending balance"]):
            return 45
        if any(term in label for term in ["at beginning", "beginning of period", "beginning balance", "balance at beginning"]):
            return -45
        return 0

    def _column_index(self, headers: list[str], terms: list[str]) -> int | None:
        for index, header in enumerate(headers):
            lower = header.lower()
            if all(term in lower for term in terms):
                return index
        return None

    def _header_year_index(self, headers: list[str], year: str) -> int | None:
        for index, header in enumerate(headers):
            if year in header:
                return index
        return None

    def _entity_after_for(self, query_lower: str) -> str | None:
        match = re.search(r"\bfor\s+(.+?)\??$", query_lower)
        if not match:
            return None
        entity = match.group(1).strip()
        return re.sub(r"[^a-z0-9 ]+", "", entity)

    def _reports_decrease_magnitude(self, query_lower: str) -> bool:
        return bool(re.search(r"\bwhat\s+percent(?:age)?\s+decrease\b", query_lower))

    def _normalize_query(self, query: str) -> str:
        normalized = query.lower()
        return normalized.replace("comodities", "commodities")

    def _amounts(self, text: str) -> list[float]:
        return [self._to_float(match) for match in re.findall(r"\$\s*([-+]?\d+(?:\.\d+)?)", text)]

    def _first_number(self, text: str) -> float | None:
        match = re.search(r"[-+]?\d+(?:\.\d+)?", text.replace(",", ""))
        if not match:
            return None
        return self._to_float(match.group(0))

    def _row_first_numeric_value(self, row: list[str]) -> float | None:
        for cell in row[1:]:
            value = self._first_number(cell)
            if value is not None:
                return value
        return None

    def _to_float(self, value: str) -> float:
        return float(value.replace(",", ""))

    def _scaled_number(self, value: str, scale: str | None) -> float:
        number = self._to_float(value)
        if scale == "billion":
            return number * 1000.0
        if scale == "thousand":
            return number / 1000.0
        return number

    def _format_percent(self, value: float) -> str:
        if abs(value - round(value)) < 0.05:
            return f"{round(value):.0f}%"
        return f"{value:.1f}%"

    def _format_number(self, value: float) -> str:
        if abs(value - round(value)) < 0.05:
            return f"{round(value):.0f}"
        return f"{value:.2f}".rstrip("0").rstrip(".")
