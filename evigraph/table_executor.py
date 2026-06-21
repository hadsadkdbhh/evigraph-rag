from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


@dataclass
class TableOperationResult:
    operation: str
    value: float
    expression: str


@dataclass
class TableValue:
    value: float
    row_label: str
    column_label: str


class TableOperationExecutor:
    def markdown_tables(self, text: str) -> list[tuple[list[str], list[list[str]]]]:
        blocks: list[list[str]] = []
        current: list[str] = []
        for line in text.splitlines():
            if "|" in line and self._is_separator_line(line):
                if current:
                    continue
            elif "|" in line:
                current.append(line)
            elif current:
                blocks.append(current)
                current = []
        if current:
            blocks.append(current)

        tables = []
        for block in blocks:
            parsed = self._parse_markdown_table_block(block)
            if parsed is not None:
                tables.append(parsed)
        return tables

    def select_rows(
        self,
        headers: list[str],
        rows: list[list[str]],
        terms: list[str],
        label_column: int = 0,
    ) -> list[list[str]]:
        if label_column < 0 or not terms:
            return []
        normalized_terms = [term.lower() for term in terms if term]
        exact_rows = []
        partial_rows = []
        for row in rows:
            if label_column >= len(row):
                continue
            label = row[label_column].lower()
            if all(term in label for term in normalized_terms):
                exact_rows.append(row)
            elif any(term in label for term in normalized_terms):
                partial_rows.append(row)
        return exact_rows or partial_rows

    def select_best_row(
        self,
        headers: list[str],
        rows: list[list[str]],
        terms: list[str],
        label_column: int = 0,
    ) -> list[str] | None:
        if label_column < 0 or not terms:
            return None
        normalized_terms = self._terms(terms)
        best: tuple[int, int, int, list[str]] | None = None
        for index, row in enumerate(rows):
            if label_column >= len(row):
                continue
            label = row[label_column].lower()
            matched = sum(1 for term in normalized_terms if term in label)
            if matched == 0:
                continue
            all_matched = 1 if matched == len(normalized_terms) else 0
            value_count = sum(1 for cell in row[1:] if self.first_number(cell) is not None)
            candidate = (all_matched, matched, value_count, row)
            if best is None or candidate[:3] > best[:3]:
                best = (all_matched, matched, value_count, row)
        return best[3] if best else None

    def select_column(self, headers: list[str], rows: list[list[str]], terms: list[str]) -> list[str]:
        if not terms:
            return []
        normalized_terms = [term.lower() for term in terms if term]
        column_index = self.column_index(headers, normalized_terms)
        if column_index is None:
            return []
        return [row[column_index] for row in rows if column_index < len(row)]

    def column_index(self, headers: list[str], terms: list[str]) -> int | None:
        normalized_terms = self._terms(terms)
        for index, header in enumerate(headers):
            lower = header.lower()
            if all(term in lower for term in normalized_terms):
                return index
        for index, header in enumerate(headers):
            lower = header.lower()
            if any(term in lower for term in normalized_terms):
                return index
        return None

    def resolve_value(self, spec: Any, context_text: str, support_text: str | None = None) -> TableValue | None:
        if not isinstance(spec, dict):
            return None
        explicit = self._explicit_value(spec, context_text, support_text=support_text)
        if explicit is not None:
            return explicit

        row_terms = self._selector_terms(spec, "row_terms", "label", "row", "metric")
        column_terms = self._selector_terms(spec, "column_terms", "column", "year", "period")
        if not row_terms or not column_terms:
            return None

        for headers, rows in self.markdown_tables(context_text):
            column_index = self.column_index(headers, column_terms)
            if column_index is None:
                continue
            row = self.select_best_row(headers, rows, row_terms)
            if row is None or column_index >= len(row):
                continue
            value = self.first_number(row[column_index])
            if value is None:
                continue
            row_label = row[0] if row else ""
            return TableValue(value=value, row_label=row_label, column_label=headers[column_index])
        return None

    def sum(self, values: list[float]) -> TableOperationResult | None:
        if not values:
            return None
        result = sum(values)
        return TableOperationResult("sum", result, " + ".join(f"{value:g}" for value in values) + f" = {result:g}")

    def product(self, values: list[float]) -> TableOperationResult | None:
        if not values:
            return None
        result = 1.0
        for value in values:
            result *= value
        return TableOperationResult(
            "product",
            result,
            " * ".join(f"{value:g}" for value in values) + f" = {result:g}",
        )

    def difference(self, target: float, base: float) -> TableOperationResult:
        result = target - base
        return TableOperationResult("difference", result, f"{target:g} - {base:g} = {result:g}")

    def ratio(self, numerator: float, denominator: float) -> TableOperationResult | None:
        if denominator == 0:
            return None
        result = numerator / denominator
        return TableOperationResult("ratio", result, f"{numerator:g} / {denominator:g} = {result:g}")

    def percent_change(self, target: float, base: float) -> TableOperationResult | None:
        if base == 0:
            return None
        result = (target - base) / abs(base) * 100.0
        return TableOperationResult(
            "percent_change",
            result,
            f"({target:g} - {base:g}) / {abs(base):g} * 100 = {result:.1f}%",
        )

    def average(self, values: list[float]) -> TableOperationResult | None:
        if not values:
            return None
        result = sum(values) / len(values)
        return TableOperationResult(
            "average",
            result,
            f"({' + '.join(f'{value:g}' for value in values)}) / {len(values)} = {result:g}",
        )

    def first_number(self, text: str) -> float | None:
        match = re.search(r"[-+]?\(?\d[\d,]*(?:\.\d+)?\)?", text)
        if not match:
            return None
        raw = match.group(0)
        negative = raw.startswith("(") and raw.endswith(")")
        raw = raw.strip("()").replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            return None
        return -value if negative else value

    def _parse_markdown_table_block(self, table_lines: list[str]) -> tuple[list[str], list[list[str]]] | None:
        rows = []
        for line in table_lines:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2 or self._is_separator_cells(cells):
                continue
            rows.append(cells)
        if len(rows) < 2:
            return None
        width = len(rows[0])
        body = [row for row in rows[1:] if len(row) == width]
        if not body:
            return None
        return rows[0], body

    def _explicit_value(
        self,
        spec: dict[str, Any],
        context_text: str,
        support_text: str | None = None,
    ) -> TableValue | None:
        if "value" not in spec:
            return None
        try:
            value = float(spec["value"])
        except (TypeError, ValueError):
            return None
        support = context_text if support_text is None else f"{context_text}\n{support_text}"
        if not self._value_supported(value, support):
            return None
        row_label = str(spec.get("label") or spec.get("row") or "")
        column_label = str(spec.get("year") or spec.get("column") or spec.get("period") or "")
        return TableValue(value=value, row_label=row_label, column_label=column_label)

    def _value_supported(self, value: float, context_text: str) -> bool:
        for number in re.findall(r"[-+]?\(?\d[\d,]*(?:\.\d+)?\)?", context_text):
            parsed = self.first_number(number)
            if parsed is not None and abs(parsed - value) < 0.05:
                return True
        return False

    def _selector_terms(self, spec: dict[str, Any], *keys: str) -> list[str]:
        terms: list[str] = []
        for key in keys:
            value = spec.get(key)
            if isinstance(value, list):
                terms.extend(str(item) for item in value if str(item).strip())
            elif value is not None and str(value).strip():
                terms.append(str(value))
        return self._terms(terms)

    def _terms(self, terms: list[str]) -> list[str]:
        normalized: list[str] = []
        for term in terms:
            normalized.extend(re.findall(r"[a-z0-9&]+", term.lower()))
        return [term for term in normalized if term]

    def _is_separator_line(self, line: str) -> bool:
        return bool(re.fullmatch(r"\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*", line))

    def _is_separator_cells(self, cells: list[str]) -> bool:
        return all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells)
