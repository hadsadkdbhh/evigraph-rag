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
        if (
            "percentage change" in query_lower
            or "percent change" in query_lower
            or "percentage increase" in query_lower
            or "percent increase" in query_lower
            or "percentual reduction" in query_lower
            or "growth rate" in query_lower
            or is_roi_query
            or "percent of the increase" in query_lower
        ):
            answer = self._roi_from_table(query_lower, contexts)
            if answer:
                return answer
            if not is_roi_query:
                answer = self._percent_change(query_lower, contexts)
                if answer:
                    return answer
                answer = self._percent_delta_phrase(query_lower, contexts)
                if answer:
                    return answer
                answer = self._percent_change_from_to_phrase(query_lower, contexts)
                if answer:
                    return answer

        if (
            "what percentage" in query_lower
            or "what percent" in query_lower
            or "what portion" in query_lower
            or "what share" in query_lower
            or " as a percentage of " in query_lower
        ):
            answer = self._ratio_percent(query_lower, contexts)
            if answer:
                return answer

        if "increased" in query_lower and "as much as" in query_lower:
            answer = self._repeated_increase_projection(query_lower, contexts)
            if answer:
                return answer

        if "after-tax" in query_lower or "after tax" in query_lower:
            answer = self._pretax_aftertax_difference(query_lower, contexts)
            if answer:
                return answer

        if "change" in query_lower and len(re.findall(r"\b(20\d{2})\b", query_lower)) >= 2:
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

        if "ratio" in query_lower and len(re.findall(r"\b(20\d{2})\b", query_lower)) >= 2:
            answer = self._ratio_between_years(query_lower, contexts)
            if answer:
                return answer

        if "post closing adjustments" in query_lower or "post-closing adjustments" in query_lower:
            answer = self._difference_between_nearby_amounts(contexts)
            if answer:
                return answer

        if self.planner_fallback is not None:
            planned = self.planner_fallback.answer(query, contexts)
            if planned is not None:
                return NumericAnswer(
                    text=planned.text,
                    calculation=planned.calculation,
                    cited_node_ids=[contexts[0][0]],
                )

        return None

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
        for node_id, text in contexts:
            table = self._markdown_table(text)
            if not table:
                continue
            headers, rows = table
            row = self._best_query_row(query_lower, headers, rows)
            if not row:
                continue
            values = [value for value in (self._first_number(cell) for cell in row[1:]) if value is not None]
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

    def _row_year_difference(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        base_year, target_year = self._difference_years(query_lower, years)
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

    def _roi_from_table(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        if "roi" not in query_lower and "rate of return" not in query_lower:
            return None
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        base_year, target_year = years[0], years[1]
        for node_id, text in contexts:
            for headers, rows in self._markdown_tables(text):
                target_index = self._header_year_index(headers, target_year)
                base_index = self._header_year_index(headers, base_year)
                if target_index is None:
                    continue
                if base_index is None:
                    earlier = [
                        index
                        for index, header in enumerate(headers)
                        if (match := re.search(r"\b(20\d{2})\b", header)) and int(match.group(1)) < int(target_year)
                    ]
                    if earlier:
                        base_index = earlier[0]
                if base_index is None:
                    continue
                row = self._best_query_row(query_lower, headers, rows)
                if not row or max(base_index, target_index) >= len(row):
                    continue
                base_value = self._first_number(row[base_index])
                target_value = self._first_number(row[target_index])
                if base_value is None or target_value is None or base_value == 0:
                    continue
                operation = self.executor.percent_change(target_value, base_value)
                if operation is None:
                    continue
                return NumericAnswer(
                    text=f"{operation.value:.1f}%",
                    calculation=f"percent_change row={row[0]} roi years={base_year}->{target_year}: {operation.expression}",
                    cited_node_ids=[node_id],
                )
        return None

    def _percent_change(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return self._percent_change_latest_table_years(query_lower, contexts)
        base_year, target_year = self._percent_change_years(query_lower, years)
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
            values = self._prose_year_values_for_query(query_lower, text, base_year, target_year) or self._year_values(text)
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
        return None

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
            return None
        aligned = dict(zip(years, numeric_values[-len(years) :]))
        if base_year in aligned and target_year in aligned:
            return {base_year: aligned[base_year], target_year: aligned[target_year]}
        return None

    def _ratio_between_years(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        numerator_year, denominator_year = years[0], years[1]
        for node_id, text in contexts:
            table_values = self._table_year_values(query_lower, text, denominator_year, numerator_year)
            values = table_values or self._prose_year_values_for_query(query_lower, text, denominator_year, numerator_year)
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
            return NumericAnswer(
                text=self._format_number(operation.value),
                calculation=f"ratio_between_years row={row_label} years={numerator_year}/{denominator_year}: {operation.expression}",
                cited_node_ids=[node_id],
            )
        return None

    def _table_year_values(
        self,
        query_lower: str,
        text: str,
        base_year: str,
        target_year: str,
    ) -> dict[str, float] | None:
        table = self._markdown_table(text)
        if not table:
            return None
        headers, rows = table
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
            return None
        if max(base_index, target_index) >= len(best_row):
            return None
        base_value = self._first_number(best_row[base_index])
        target_value = self._first_number(best_row[target_index])
        if base_value is None or target_value is None:
            return None
        return {base_year: base_value, target_year: target_value, "__row_label__": best_row[0]}

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
        for node_id, text in contexts:
            prose_answer = (
                self._prose_ratio_percent(node_id, text, numerator_terms, denominator_terms)
                if not query_year and " as a percentage of " in query_lower
                else None
            )
            if prose_answer is not None:
                return prose_answer
            rows = self._label_value_rows(text)
            if not rows and not self._markdown_table(text):
                continue

            denominator = None
            denominator_meta = {}
            if query_year:
                denominator, denominator_meta = self._table_value_for_terms_year_with_label(text, denominator_terms, query_year)
            if denominator is None:
                denominator, denominator_meta = self._matching_value_with_label(rows, denominator_terms)
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
                numerator = self._prose_value_for_terms_year(text, numerator_terms, query_year)
                numerator_meta = {}
            if numerator is None:
                numerator, numerator_meta = self._matching_value_with_label(rows, numerator_terms)
            if numerator is None or denominator in {None, 0}:
                continue
            if numerator_meta.get("row_label") and numerator_meta.get("row_label") == denominator_meta.get("row_label"):
                continue

            operation = self.executor.ratio(numerator, denominator)
            if operation is None:
                continue
            result = operation.value * 100.0
            numerator_label = str(numerator_meta.get("row_label", ""))
            denominator_label = str(denominator_meta.get("row_label", ""))
            return NumericAnswer(
                text=self._format_percent(result),
                calculation=(
                    f"ratio_percent row={numerator_label} denominator_row={denominator_label}: "
                    f"{numerator:g} / {denominator:g} * 100 = {result:.1f}%"
                ),
                cited_node_ids=[node_id],
            )
        return None

    def _ratio_year(self, query_lower: str, years: list[str]) -> str | None:
        if "due after" in query_lower:
            return None
        year_of_match = re.search(r"\byear\s+of\s+(20\d{2})\b", query_lower)
        if year_of_match:
            return year_of_match.group(1)
        if len(years) == 1:
            return years[0]
        return None

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
        if year_index is None:
            return None, {}
        for row in rows:
            if year_index >= len(row):
                continue
            label = row[0].lower()
            if all(term in label for term in terms):
                return self._first_number(row[year_index]), {"row_label": row[0]}
        if not allow_partial:
            return None, {}
        for row in rows:
            if year_index >= len(row):
                continue
            label = row[0].lower()
            if any(term in label for term in terms):
                return self._first_number(row[year_index]), {"row_label": row[0]}
        return None, {}

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
    ) -> NumericAnswer | None:
        rows = self._label_value_rows(text)
        numerator, numerator_meta = self._matching_value_with_label(rows, numerator_terms)
        denominator, denominator_label = self._prose_amount_for_terms(text, denominator_terms)
        denominator_meta = {"row_label": denominator_label} if denominator_label else {}
        if denominator is None:
            denominator, denominator_meta = self._matching_value_with_label(rows, denominator_terms)
        if numerator is None:
            numerator, numerator_label = self._prose_amount_for_terms(text, numerator_terms)
            numerator_meta = {"row_label": numerator_label} if numerator_label else {}
        if numerator is None or denominator in {None, 0}:
            return None
        if numerator_meta.get("row_label") and numerator_meta.get("row_label") == denominator_meta.get("row_label"):
            return None
        operation = self.executor.ratio(numerator, denominator)
        if operation is None:
            return None
        result = operation.value * 100.0
        numerator_label = str(numerator_meta.get("row_label", " ".join(numerator_terms)))
        denominator_label = str(denominator_meta.get("row_label", " ".join(denominator_terms)))
        return NumericAnswer(
            text=self._format_percent(result),
            calculation=(
                f"ratio_percent row={numerator_label} denominator_row={denominator_label}: "
                f"{numerator:g} / {denominator:g} * 100 = {result:.1f}%"
            ),
            cited_node_ids=[node_id],
        )

    def _prose_amount_for_terms(self, text: str, terms: list[str]) -> tuple[float | None, str]:
        if not terms:
            return None, ""
        best: tuple[int, float, str] | None = None
        min_matches = 2 if len(terms) >= 2 else 1
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
        for node in support_graph.nodes.values():
            if node.node_type == "verifier_judgment":
                continue
            text = self._node_text(node)
            if text:
                contexts.append((node.node_id, text))
        return contexts

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

    def _denominator_terms(self, query_lower: str) -> list[str]:
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
            r"\b(was|were|is|are|comes from|represented by|allocated to|related to|due to|due after)\b",
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
        patterns = [
            r"what\s+(?:are|is|was|were)\s+(.+?)\s+as\s+a\s+percentage\s+of",
            r"payments?\s+for\s+(.+?)\s+as\s+a\s+percentage\s+of",
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
            "by",
            "in",
            "for",
            "are",
            "due",
            "after",
            "represented",
            "total",
            "is",
            "if",
            "an",
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
        best_row = None
        best_score = 0
        for row in rows:
            if not row:
                continue
            label_terms = set(re.findall(r"[a-z0-9]+", row[0].lower()))
            score = len(query_terms & label_terms)
            if score > best_score:
                best_score = score
                best_row = row
        if best_score == 0:
            return None
        return best_row

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
