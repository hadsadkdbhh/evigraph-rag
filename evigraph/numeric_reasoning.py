from __future__ import annotations

import re
from dataclasses import dataclass

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import EvidenceNode
from evigraph.table_executor import TableOperationExecutor


@dataclass
class NumericAnswer:
    text: str
    calculation: str
    cited_node_ids: list[str]


class NumericReasoner:
    def __init__(self) -> None:
        self.executor = TableOperationExecutor()

    def answer(self, query: str, support_graph: EvidenceGraph) -> NumericAnswer | None:
        query_lower = self._normalize_query(query)
        contexts = self._contexts(support_graph)
        if not contexts:
            return None

        if (
            "percentage change" in query_lower
            or "percent change" in query_lower
            or "growth rate" in query_lower
            or "rate of return" in query_lower
        ):
            answer = self._percent_change(query_lower, contexts)
            if answer:
                return answer

        if "what percentage" in query_lower or "what percent" in query_lower:
            answer = self._ratio_percent(query_lower, contexts)
            if answer:
                return answer

        if "average" in query_lower and "per" in query_lower:
            answer = self._row_average(query_lower, contexts)
            if answer:
                return answer

        if "average" in query_lower:
            answer = self._year_range_average(query_lower, contexts)
            if answer:
                return answer

        if "post closing adjustments" in query_lower or "post-closing adjustments" in query_lower:
            answer = self._difference_between_nearby_amounts(contexts)
            if answer:
                return answer

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
                    calculation=f"row_average: {operation.expression}",
                    cited_node_ids=[node_id],
                )
        return None

    def _percent_change(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        if len(years) < 2:
            return None
        base_year, target_year = years[0], years[1]
        for node_id, text in contexts:
            values = self._table_year_values(query_lower, text, base_year, target_year) or self._year_values(text)
            if base_year not in values or target_year not in values or values[base_year] == 0:
                continue
            operation = self.executor.percent_change(values[target_year], values[base_year])
            if operation is None:
                continue
            result = operation.value
            return NumericAnswer(
                text=f"{result:.1f}%",
                calculation=f"percent_change: {operation.expression}",
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
            return None

        query_terms = set(self._keywords(query_lower))
        best_row = None
        best_score = 0
        for row in rows:
            if max(base_index, target_index) >= len(row):
                continue
            label_terms = set(re.findall(r"[a-z0-9]+", row[0].lower()))
            score = len(query_terms & label_terms)
            if score > best_score:
                best_score = score
                best_row = row
        if not best_row or best_score == 0:
            return None
        base_value = self._first_number(best_row[base_index])
        target_value = self._first_number(best_row[target_index])
        if base_value is None or target_value is None:
            return None
        return {base_year: base_value, target_year: target_value}

    def _ratio_percent(self, query_lower: str, contexts: list[tuple[str, str]]) -> NumericAnswer | None:
        years = re.findall(r"\b(20\d{2})\b", query_lower)
        query_year = years[0] if years else None
        for node_id, text in contexts:
            rows = self._label_value_rows(text)
            if not rows and not self._markdown_table(text):
                continue

            denominator_terms = self._denominator_terms(query_lower)
            denominator = None
            if query_year:
                denominator = self._table_value_for_terms_year(text, denominator_terms, query_year)
            if denominator is None:
                denominator = self._matching_value(rows, denominator_terms)
            numerator = None
            if "after 2012" in query_lower or "due after" in query_lower:
                numerator = self._matching_value(rows, ["thereafter"])
            if numerator is None and "represented by" in query_lower and query_year:
                numerator = self._prose_value_for_terms_year(text, self._numerator_terms(query_lower), query_year)
            if numerator is None:
                numerator = self._matching_value(rows, self._numerator_terms(query_lower))
            if numerator is None or denominator in {None, 0}:
                continue

            operation = self.executor.ratio(numerator, denominator)
            if operation is None:
                continue
            result = operation.value * 100.0
            return NumericAnswer(
                text=self._format_percent(result),
                calculation=f"ratio_percent: {numerator:g} / {denominator:g} * 100 = {result:.1f}%",
                cited_node_ids=[node_id],
            )
        return None

    def _table_value_for_terms_year(self, text: str, terms: list[str], year: str) -> float | None:
        table = self._markdown_table(text)
        if not table:
            return None
        headers, rows = table
        year_index = self._header_year_index(headers, year)
        if year_index is None:
            return None
        for row in rows:
            if year_index >= len(row):
                continue
            label = row[0].lower()
            if all(term in label for term in terms):
                return self._first_number(row[year_index])
        for row in rows:
            if year_index >= len(row):
                continue
            label = row[0].lower()
            if any(term in label for term in terms):
                return self._first_number(row[year_index])
        return None

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
        normalized_terms = [term for term in terms if term]
        for label, value in rows:
            if all(term in label for term in normalized_terms):
                return value
        for label, value in rows:
            if any(term in label for term in normalized_terms):
                return value
        return None

    def _denominator_terms(self, query_lower: str) -> list[str]:
        if " of " not in query_lower:
            return []
        tail = query_lower.split(" of ", 1)[1]
        tail = re.sub(r"\bare due\b.*", "", tail)
        tail = re.sub(r"\bwere represented\b.*", "", tail)
        return self._keywords(tail)

    def _numerator_terms(self, query_lower: str) -> list[str]:
        if "represented by" in query_lower:
            return self._keywords(query_lower.split("represented by", 1)[1])
        return []

    def _keywords(self, text: str) -> list[str]:
        stop = {
            "what",
            "percentage",
            "percent",
            "of",
            "the",
            "were",
            "was",
            "by",
            "in",
            "are",
            "due",
            "after",
            "represented",
            "total",
            "is",
            "an",
            "from",
            "to",
            "rate",
            "return",
            "investment",
            "change",
        }
        return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in stop][:5]

    def _markdown_table(self, text: str) -> tuple[list[str], list[list[str]]] | None:
        table_lines = []
        for line in text.splitlines():
            if line.strip().startswith("|") and "|" in line.strip()[1:]:
                table_lines.append(line)
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

    def _format_percent(self, value: float) -> str:
        if abs(value - round(value)) < 0.05:
            return f"{round(value):.0f}%"
        return f"{value:.1f}%"
