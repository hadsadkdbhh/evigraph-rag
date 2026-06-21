from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DIAGNOSTIC_LABELS = (
    "wrong_numerator",
    "wrong_denominator",
    "wrong_year_or_period",
    "wrong_row_label",
    "wrong_operation_type",
    "ambiguous_supported_wrong_number",
)

_PRIMARY_PRIORITY = {
    "wrong_operation_type": 0,
    "wrong_year_or_period": 1,
    "wrong_numerator": 2,
    "wrong_denominator": 3,
    "wrong_row_label": 4,
    "ambiguous_supported_wrong_number": 5,
}


class RowOperationDiagnosticAnalyzer:
    """Diagnose wrong numeric answers into row/operation error families."""

    def analyze(self, csv_path: str | Path, method: str = "full_evigraph") -> dict[str, Any]:
        path = Path(csv_path)
        rows = self._read_rows(path)
        scoped = [row for row in rows if row.get("method") == method]
        wrong_rows = [row for row in scoped if self._is_wrong_numeric(row)]
        diagnostics = [self._diagnose(row) for row in wrong_rows]
        label_counts = Counter(label for item in diagnostics for label in item["labels"])
        primary_counts = Counter(item["primary"] for item in diagnostics)
        return {
            "csv_path": str(path),
            "method": method,
            "total": len(scoped),
            "wrong_numeric_operation_or_row": len(wrong_rows),
            "label_counts": {label: label_counts.get(label, 0) for label in DIAGNOSTIC_LABELS},
            "primary_counts": {label: primary_counts.get(label, 0) for label in DIAGNOSTIC_LABELS},
            "examples": self._examples_by_primary(diagnostics),
            "diagnostics": diagnostics,
        }

    def render_markdown(self, analysis: dict[str, Any]) -> str:
        lines = [
            "# Row/Operation Diagnostic",
            "",
            f"- CSV: `{self._display_path(analysis['csv_path'])}`",
            f"- Method: `{analysis['method']}`",
            f"- Total rows for method: {analysis['total']}",
            f"- Wrong numeric operation/row rows: {analysis['wrong_numeric_operation_or_row']}",
            "",
            "## Label Counts",
            "",
            "| label | count |",
            "| --- | ---: |",
        ]
        for label in DIAGNOSTIC_LABELS:
            lines.append(f"| {label} | {analysis['label_counts'].get(label, 0)} |")
        lines.extend(
            [
                "",
                "## Primary Error Counts",
                "",
                "| primary error | count |",
                "| --- | ---: |",
            ]
        )
        for label in DIAGNOSTIC_LABELS:
            lines.append(f"| {label} | {analysis['primary_counts'].get(label, 0)} |")
        lines.extend(["", "## Examples", ""])
        for label in DIAGNOSTIC_LABELS:
            examples = analysis["examples"].get(label, [])
            if not examples:
                continue
            lines.extend([f"### {label}", ""])
            for item in examples:
                lines.append(f"- `{item['id']}`")
                lines.append(f"  - query: {item['query']}")
                lines.append(f"  - gold: `{item['gold']}`")
                lines.append(f"  - prediction: `{item['prediction']}`")
                if item.get("calculation"):
                    lines.append(f"  - calculation: `{self._shorten(item['calculation'], 180)}`")
                lines.append(f"  - labels: {', '.join(item['labels'])}")
                if item.get("signals"):
                    lines.append(f"  - signals: {self._shorten('; '.join(item['signals']), 220)}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def write(
        self,
        csv_path: str | Path,
        output_path: str | Path,
        method: str = "full_evigraph",
        json_output_path: str | Path | None = None,
    ) -> str:
        analysis = self.analyze(csv_path, method=method)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render_markdown(analysis), encoding="utf-8")
        if json_output_path:
            json_output = Path(json_output_path)
            json_output.parent.mkdir(parents=True, exist_ok=True)
            json_output.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(output)

    def _diagnose(self, row: dict[str, str]) -> dict[str, Any]:
        query = row.get("query", "")
        gold = row.get("answer", "")
        prediction = row.get("prediction", "")
        run_dir = Path(row.get("run_dir", ""))
        calculation = self._calculation_line(run_dir)
        context = self._support_context(run_dir)
        labels: set[str] = set()
        signals: list[str] = []

        expected_operation = self._expected_operation(query, gold)
        actual_operation = self._actual_operation(calculation)
        if expected_operation and actual_operation and not self._operation_matches(expected_operation, actual_operation):
            labels.add("wrong_operation_type")
            signals.append(f"expected_operation={expected_operation}, actual_operation={actual_operation}")

        if self._year_or_period_mismatch(query, calculation):
            labels.add("wrong_year_or_period")
            signals.append("calculation year/period cues differ from query cues")

        operand_labels, operand_signals = self._operand_labels(actual_operation, calculation, gold, context)
        labels.update(operand_labels)
        signals.extend(operand_signals)

        if self._row_label_mismatch(query, calculation):
            labels.add("wrong_row_label")
            signals.append("calculation row labels have weak overlap with query terms")

        if not labels:
            labels.add("ambiguous_supported_wrong_number")
            signals.append("numeric answer is supported by selected evidence but differs from gold")

        primary = sorted(labels, key=lambda label: _PRIMARY_PRIORITY[label])[0]
        return {
            "id": row.get("id", ""),
            "query": query,
            "gold": gold,
            "prediction": prediction,
            "calculation": calculation,
            "expected_operation": expected_operation,
            "actual_operation": actual_operation,
            "labels": [label for label in DIAGNOSTIC_LABELS if label in labels],
            "primary": primary,
            "signals": signals,
            "run_dir": row.get("run_dir", ""),
        }

    def _operand_labels(
        self,
        actual_operation: str,
        calculation: str,
        gold: str,
        context: str,
    ) -> tuple[set[str], list[str]]:
        labels: set[str] = set()
        signals: list[str] = []
        operands = self._expression_numbers(calculation)
        gold_numbers = self._numbers(gold)
        if len(operands) < 2 or not gold_numbers:
            return labels, signals
        gold_value = gold_numbers[0]

        if actual_operation == "ratio_percent" and not self._close(gold_value, 0.0):
            numerator, denominator = operands[0], operands[1]
            expected_numerator = denominator * gold_value / 100.0
            expected_denominator = numerator * 100.0 / gold_value
            if self._context_contains_value(context, expected_numerator) and not self._close(numerator, expected_numerator):
                labels.add("wrong_numerator")
                signals.append(f"same denominator implies numerator≈{expected_numerator:.4g} appears in support")
            if self._context_contains_value(context, expected_denominator) and not self._close(denominator, expected_denominator):
                labels.add("wrong_denominator")
                signals.append(f"same numerator implies denominator≈{expected_denominator:.4g} appears in support")

        if actual_operation == "percent_change" and len(operands) >= 2 and not self._close(1 + gold_value / 100.0, 0.0):
            current, base = operands[0], operands[1]
            expected_current = base * (1 + gold_value / 100.0)
            expected_base = current / (1 + gold_value / 100.0)
            if self._context_contains_value(context, expected_current) and not self._close(current, expected_current):
                labels.add("wrong_numerator")
                signals.append(f"same base implies current value≈{expected_current:.4g} appears in support")
            if self._context_contains_value(context, expected_base) and not self._close(base, expected_base):
                labels.add("wrong_denominator")
                signals.append(f"same current value implies base value≈{expected_base:.4g} appears in support")
            predicted_numbers = self._numbers(calculation.split("=")[-1] if "=" in calculation else "")
            if predicted_numbers and self._close(predicted_numbers[-1], -gold_value):
                labels.add("wrong_operation_type")
                signals.append("predicted percent change has the opposite sign of the gold answer")

        if actual_operation in {"row_year_difference", "difference"} and len(operands) >= 2:
            left, right = operands[0], operands[1]
            expected_left = right + gold_value
            expected_right = left - gold_value
            if self._context_contains_value(context, expected_left) and not self._close(left, expected_left):
                labels.add("wrong_numerator")
                signals.append(f"same right operand implies left operand≈{expected_left:.4g} appears in support")
            if self._context_contains_value(context, expected_right) and not self._close(right, expected_right):
                labels.add("wrong_denominator")
                signals.append(f"same left operand implies right operand≈{expected_right:.4g} appears in support")

        return labels, signals

    def _expected_operation(self, query: str, gold: str) -> str:
        lowered = query.lower()
        has_percent_answer = "%" in gold or any(token in lowered for token in ("percent", "percentage", "percentual", "portion"))
        if any(token in lowered for token in ("average", "mean")):
            return "average"
        if any(
            token in lowered
            for token in (
                "percent of the change",
                "percentage of the change",
                "percent of change",
                "percentage of change",
                "percentual increase",
                "percentual decrease",
                "percentual growth",
            )
        ):
            return "percent_change"
        if has_percent_answer and any(
            token in lowered
            for token in ("percentage change", "percent change", "growth", "increase", "decrease", "reduction", "from")
        ):
            if not any(token in lowered for token in ("portion", "percent of", "percentage of", "represented", "allocated", "comes from")):
                return "percent_change"
        if any(token in lowered for token in ("portion", "percent of", "percentage of", "represented", "allocated", "comes from", "ratio")):
            return "ratio_percent"
        if any(token in lowered for token in ("difference", "change in", "higher", "lower")):
            return "difference"
        if any(token in lowered for token in ("total", "sum", "combined")):
            return "sum_or_lookup"
        return ""

    def _operation_matches(self, expected: str, actual: str) -> bool:
        compatible = {
            "average": {"average", "planned_average", "row_values_average", "year_range_average"},
            "percent_change": {"percent_change", "planned_percent_change", "roi"},
            "ratio_percent": {"ratio_percent"},
            "difference": {"difference", "planned_difference", "row_year_difference"},
            "sum_or_lookup": {"sum", "planned_sum", "lookup", "planned_lookup", "row_lookup"},
        }
        return actual in compatible.get(expected, {expected})

    def _actual_operation(self, calculation: str) -> str:
        match = re.match(r"([A-Za-z_]+)", calculation.strip())
        return match.group(1) if match else ""

    def _year_or_period_mismatch(self, query: str, calculation: str) -> bool:
        query_years = set(re.findall(r"\b(?:19|20)\d{2}\b", query))
        calc_years = set(re.findall(r"\b(?:19|20)\d{2}\b", calculation))
        if query_years and calc_years and not query_years.issubset(calc_years):
            return True

        query_periods = self._period_cues(query)
        calc_periods = self._period_cues(calculation)
        if query_periods and calc_periods and not calc_periods.issubset(query_periods):
            return True
        return False

    def _period_cues(self, text: str) -> set[str]:
        lowered = text.lower()
        cues = set()
        for cue in ("three months", "six months", "nine months", "twelve months", "quarter", "annual", "year ended"):
            if cue in lowered:
                cues.add(cue)
        return cues

    def _row_label_mismatch(self, query: str, calculation: str) -> bool:
        row_labels = self._row_labels(calculation)
        if not row_labels:
            return self._actual_operation(calculation) in {"ratio_percent", "percent_change", "row_year_difference"}
        query_terms = self._content_terms(query)
        if not query_terms:
            return False
        label_terms = set()
        for label in row_labels:
            label_terms.update(self._content_terms(label))
        overlap = len(query_terms & label_terms) / max(1, len(query_terms))
        return overlap < 0.2

    def _row_labels(self, calculation: str) -> list[str]:
        labels = []
        row_match = re.search(r"\brow=(.*?)(?:\s+denominator_row=|:)", calculation)
        if row_match:
            labels.append(row_match.group(1).strip())
        denominator_match = re.search(r"\bdenominator_row=(.*?):", calculation)
        if denominator_match:
            labels.append(denominator_match.group(1).strip())
        return [label for label in labels if label]

    def _content_terms(self, text: str) -> set[str]:
        stopwords = {
            "what",
            "was",
            "were",
            "the",
            "for",
            "from",
            "between",
            "and",
            "that",
            "this",
            "with",
            "into",
            "million",
            "millions",
            "dollars",
            "percent",
            "percentage",
            "portion",
            "change",
            "increase",
            "decrease",
            "total",
            "average",
            "year",
            "years",
            "ended",
            "months",
            "month",
            "december",
            "january",
        }
        return {
            token
            for token in re.findall(r"[a-zA-Z][a-zA-Z0-9]+", text.lower())
            if token not in stopwords and not re.fullmatch(r"(?:19|20)\d{2}", token)
        }

    def _calculation_line(self, run_dir: Path) -> str:
        answer_path = run_dir / "answer.md"
        if not answer_path.exists():
            return ""
        text = answer_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"## Calculations\n(.*?)(?:\n## |\Z)", text, re.S)
        if not match:
            return ""
        for raw_line in match.group(1).splitlines():
            line = raw_line.strip()
            if line.startswith("- "):
                return line[2:].strip()
        return ""

    def _support_context(self, run_dir: Path) -> str:
        graph_path = run_dir / "support_graph.json"
        if not graph_path.exists():
            return ""
        try:
            payload = json.loads(graph_path.read_text(encoding="utf-8", errors="ignore"))
        except json.JSONDecodeError:
            return ""
        chunks = []
        for node in payload.get("nodes", []):
            content = node.get("content", "")
            if isinstance(content, (dict, list)):
                chunks.append(json.dumps(content, ensure_ascii=False))
            else:
                chunks.append(str(content))
        return "\n".join(chunks)

    def _expression_numbers(self, calculation: str) -> list[float]:
        if ":" in calculation:
            calculation = calculation.split(":", 1)[1]
        expression = calculation.split("=", 1)[0]
        return self._numbers(expression)

    def _numbers(self, text: str) -> list[float]:
        values = []
        for raw in re.findall(r"[-+]?\d[\d,]*(?:\.\d+)?", text):
            try:
                values.append(float(raw.replace(",", "")))
            except ValueError:
                continue
        return values

    def _context_contains_value(self, context: str, value: float) -> bool:
        if not math.isfinite(value):
            return False
        return any(self._close(candidate, value, relative=0.003, absolute=1.0) for candidate in self._numbers(context))

    def _close(self, left: float, right: float, relative: float = 0.01, absolute: float = 0.5) -> bool:
        return abs(left - right) <= max(absolute, abs(right) * relative)

    def _is_wrong_numeric(self, row: dict[str, str]) -> bool:
        if self._to_float(row.get("accuracy")) >= 1.0:
            return False
        prediction = row.get("prediction", "")
        if prediction.startswith("Based on the selected evidence:"):
            return False
        return bool(self._numbers(prediction) and self._numbers(row.get("answer", "")))

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def _examples_by_primary(self, diagnostics: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in diagnostics:
            if len(grouped[item["primary"]]) < 5:
                grouped[item["primary"]].append(item)
        return dict(grouped)

    def _to_float(self, value: Any) -> float:
        if value in (None, ""):
            return 0.0
        return float(value)

    def _shorten(self, text: str, limit: int = 220) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3] + "..."

    def _display_path(self, path_text: str) -> str:
        path = Path(path_text)
        try:
            return str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(path)
