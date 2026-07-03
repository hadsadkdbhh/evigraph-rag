from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PROCESS_STEPS = (
    "evidence_available",
    "period_hit",
    "row_hit",
    "operand_hit",
    "operation_hit",
    "citation_hit",
    "answer_supported",
    "exact_match",
)


class EvidenceCritic:
    """Lightweight process critic for retrieved numerical evidence."""

    def assess(self, query: str, support_context: str, calculation: str) -> dict[str, bool]:
        query_terms = self._terms(query)
        support_terms = self._terms(support_context)
        query_years = self._years(query)
        support_text = f"{support_context}\n{calculation}"
        expression_numbers = self._expression_numbers(calculation)
        support_numbers = self._numbers(support_context)
        return {
            "target_period_present": self._period_present(query_years, support_text),
            "required_row_present": self._row_present(query_terms, support_terms),
            "numeric_operands_present": self._operands_present(expression_numbers, support_numbers),
            "operation_cue_present": self._operation_cue_present(query, calculation),
            "noise_risk": not support_context.strip(),
        }

    def _period_present(self, query_years: list[str], support_text: str) -> bool:
        if not query_years:
            return True
        return all(year in support_text for year in query_years)

    def _row_present(self, query_terms: set[str], support_terms: set[str]) -> bool:
        if not query_terms:
            return bool(support_terms)
        overlap = query_terms & support_terms
        return len(overlap) >= min(2, len(query_terms))

    def _operands_present(self, expression_numbers: list[float], support_numbers: list[float]) -> bool:
        if not expression_numbers:
            return False
        operands = expression_numbers[:-1] if len(expression_numbers) > 1 else expression_numbers
        return all(any(self._close(operand, support_number) for support_number in support_numbers) for operand in operands)

    def _operation_cue_present(self, query: str, calculation: str) -> bool:
        lowered_query = query.lower()
        lowered_calculation = calculation.lower()
        if any(token in lowered_calculation for token in ("ratio", "percent_change", "difference", "average", "sum", "product")):
            return True
        if any(token in lowered_query for token in ("percent", "percentage", "ratio")):
            return "/" in calculation or "*" in calculation
        if any(token in lowered_query for token in ("difference", "change", "higher", "lower")):
            return "-" in calculation
        if any(token in lowered_query for token in ("average", "mean")):
            return "average" in lowered_calculation or "/" in calculation
        if any(token in lowered_query for token in ("total", "sum", "combined")):
            return "+" in calculation or "sum" in lowered_calculation
        return bool(calculation.strip())

    def _expression_numbers(self, calculation: str) -> list[float]:
        if not calculation:
            return []
        expression = calculation.rsplit("=", 1)[0]
        if ":" in expression:
            expression = expression.split(":", 1)[1]
        return self._numbers(expression)

    def _numbers(self, text: str) -> list[float]:
        return [float(match.replace(",", "")) for match in re.findall(r"[-+]?\d[\d,]*(?:\.\d+)?", text)]

    def _years(self, text: str) -> list[str]:
        return re.findall(r"\b(?:19|20)\d{2}\b", text)

    def _terms(self, text: str) -> set[str]:
        stop = {
            "what",
            "was",
            "were",
            "the",
            "and",
            "for",
            "from",
            "with",
            "that",
            "this",
            "how",
            "much",
            "many",
            "did",
            "does",
            "its",
            "their",
            "year",
            "years",
            "percent",
            "percentage",
            "change",
            "total",
        }
        return {
            token
            for token in re.findall(r"[a-z][a-z0-9]+", text.lower())
            if token not in stop and len(token) > 2 and not token.isdigit()
        }

    def _close(self, left: float, right: float) -> bool:
        return abs(left - right) <= max(0.1, abs(right) * 0.001)


class ProcessTraceAnalyzer:
    """Build hop-wise process diagnostics from manifest CSV rows and run artifacts."""

    def __init__(self, critic: EvidenceCritic | None = None) -> None:
        self.critic = critic or EvidenceCritic()

    def analyze(self, csv_path: str | Path, method: str = "full_evigraph") -> dict[str, Any]:
        path = Path(csv_path)
        rows = [row for row in self._read_rows(path) if row.get("method") == method]
        traces = [self._trace_row(row) for row in rows]
        step_counts = {step: sum(int(item[step]) for item in traces) for step in PROCESS_STEPS}
        total = len(traces)
        first_failed = Counter(self._first_failed_step(item) for item in traces)
        return {
            "csv_path": str(path),
            "method": method,
            "total": total,
            "step_counts": step_counts,
            "step_rates": {step: step_counts[step] / max(1, total) for step in PROCESS_STEPS},
            "first_failed_step_counts": dict(first_failed),
            "examples": self._examples(traces),
            "traces": traces,
        }

    def render_markdown(self, analysis: dict[str, Any]) -> str:
        lines = [
            "# Process Trace Diagnostic",
            "",
            f"- CSV: `{self._display_path(analysis['csv_path'])}`",
            f"- Method: `{analysis['method']}`",
            f"- Total rows for method: {analysis['total']}",
            "",
            "## Hop-wise Process Rates",
            "",
            "| step | count | rate |",
            "| --- | ---: | ---: |",
        ]
        for step in PROCESS_STEPS:
            lines.append(
                f"| {step} | {analysis['step_counts'].get(step, 0)} | {analysis['step_rates'].get(step, 0.0):.3f} |"
            )
        lines.extend(["", "## First Failed Step", "", "| step | count |", "| --- | ---: |"])
        for step, count in sorted(analysis["first_failed_step_counts"].items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| {step} | {count} |")
        lines.extend(["", "## Examples", ""])
        for item in analysis["examples"]:
            lines.append(f"- `{item['id']}` first_failed=`{item['first_failed_step']}`")
            lines.append(f"  - query: {self._shorten(item['query'], 180)}")
            lines.append(f"  - gold: `{item['answer']}`")
            lines.append(f"  - prediction: `{self._shorten(item['prediction'], 140)}`")
            if item.get("calculation"):
                lines.append(f"  - calculation: `{self._shorten(item['calculation'], 180)}`")
        return "\n".join(lines).rstrip() + "\n"

    def write(self, csv_path: str | Path, output_path: str | Path, method: str = "full_evigraph") -> str:
        analysis = self.analyze(csv_path, method=method)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render_markdown(analysis), encoding="utf-8")
        return str(output)

    def _trace_row(self, row: dict[str, str]) -> dict[str, Any]:
        run_dir = Path(row.get("run_dir", ""))
        support_context = self._support_context(run_dir)
        calculation = self._calculation_line(run_dir)
        critic = self.critic.assess(row.get("query", ""), support_context, calculation)
        selected_count = self._selected_count(run_dir)
        trace = {
            "id": row.get("id", ""),
            "query": row.get("query", ""),
            "answer": row.get("answer", ""),
            "prediction": row.get("prediction", ""),
            "calculation": calculation,
            "run_dir": row.get("run_dir", ""),
            "evidence_available": selected_count > 0 and not critic["noise_risk"],
            "period_hit": critic["target_period_present"],
            "row_hit": self._truthy(row.get("row_operation_grounded")) or critic["required_row_present"],
            "operand_hit": critic["numeric_operands_present"],
            "operation_hit": self._truthy(row.get("operation_semantics_checked")) or critic["operation_cue_present"],
            "citation_hit": self._truthy(row.get("citation_correct")),
            "answer_supported": self._truthy(row.get("answer_supported")),
            "exact_match": self._to_float(row.get("accuracy")) >= 1.0,
            "critic": critic,
        }
        trace["first_failed_step"] = self._first_failed_step(trace)
        return trace

    def _first_failed_step(self, trace: dict[str, Any]) -> str:
        for step in PROCESS_STEPS:
            if not trace.get(step):
                return step
        return "none"

    def _examples(self, traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
        examples: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in traces:
            step = item["first_failed_step"]
            if step == "none" or step in seen:
                continue
            examples.append(item)
            seen.add(step)
            if len(examples) >= 8:
                break
        return examples

    def _support_context(self, run_dir: Path) -> str:
        graph_path = run_dir / "support_graph.json"
        if not graph_path.exists():
            return ""
        try:
            graph = json.loads(graph_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return ""
        pieces: list[str] = []
        for node in graph.get("nodes", []):
            if node.get("node_type") == "verifier_judgment":
                continue
            pieces.append(self._flatten(node.get("content", "")))
        return "\n".join(piece for piece in pieces if piece)

    def _selected_count(self, run_dir: Path) -> int:
        graph_path = run_dir / "support_graph.json"
        if not graph_path.exists():
            return 0
        try:
            graph = json.loads(graph_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return 0
        return sum(1 for node in graph.get("nodes", []) if node.get("node_type") != "verifier_judgment")

    def _calculation_line(self, run_dir: Path) -> str:
        answer_path = run_dir / "answer.md"
        if not answer_path.exists():
            return ""
        text = answer_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"## Calculations\s*(.*?)(?:\n## |\Z)", text, flags=re.S)
        if not match:
            return ""
        for line in match.group(1).splitlines():
            line = line.strip()
            if line.startswith("- "):
                return line[2:].strip()
        return ""

    def _flatten(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return " ".join(f"{key}: {self._flatten(item)}" for key, item in value.items())
        if isinstance(value, list):
            return " ".join(self._flatten(item) for item in value)
        return str(value)

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def _truthy(self, value: Any) -> bool:
        return str(value).strip().lower() in {"1", "1.0", "true", "yes"}

    def _to_float(self, value: Any) -> float:
        if value in (None, ""):
            return 0.0
        try:
            return float(value)
        except ValueError:
            return 0.0

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
