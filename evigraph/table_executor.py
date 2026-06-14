from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TableOperationResult:
    operation: str
    value: float
    expression: str


class TableOperationExecutor:
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

    def select_column(self, headers: list[str], rows: list[list[str]], terms: list[str]) -> list[str]:
        if not terms:
            return []
        normalized_terms = [term.lower() for term in terms if term]
        column_index = None
        for index, header in enumerate(headers):
            lower = header.lower()
            if all(term in lower for term in normalized_terms):
                column_index = index
                break
        if column_index is None:
            for index, header in enumerate(headers):
                lower = header.lower()
                if any(term in lower for term in normalized_terms):
                    column_index = index
                    break
        if column_index is None:
            return []
        return [row[column_index] for row in rows if column_index < len(row)]

    def sum(self, values: list[float]) -> TableOperationResult | None:
        if not values:
            return None
        result = sum(values)
        return TableOperationResult("sum", result, " + ".join(f"{value:g}" for value in values) + f" = {result:g}")

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
