from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from evigraph.retrieval_diagnostics import RetrievalDiagnosticAnalyzer


class PaperCaseSelector:
    """Select compact, paper-readable examples from paired manifest CSVs."""

    def select(
        self,
        evigraph_csv: str | Path,
        questions_path: str | Path,
        corpus_path: str | Path | None,
        retrieval_mode: str,
        gpt_csv: str | Path | None = None,
        top_k: int = 8,
    ) -> dict[str, Any]:
        evigraph_rows = self._read_rows(evigraph_csv)
        by_method = self._by_method(evigraph_rows)
        questions = self._read_questions(questions_path)
        retrieval = RetrievalDiagnosticAnalyzer().analyze(
            evigraph_csv,
            questions_path=questions_path,
            corpus_path=corpus_path,
            retrieval_mode=retrieval_mode,
            method="full_evigraph",
            top_k=top_k,
        )
        retrieval_by_id = {row["id"]: row for row in retrieval["diagnostics"]}
        cases = {
            "evigraph_over_direct": self._first_case(
                by_method,
                target="full_evigraph",
                baseline="direct_rag",
                retrieval_by_id=retrieval_by_id,
                questions=questions,
            ),
            "graph_selection_over_utility": self._first_case(
                by_method,
                target="full_evigraph",
                baseline="utility_only",
                retrieval_by_id=retrieval_by_id,
                questions=questions,
            ),
            "planner_over_no_planner": self._first_case(
                by_method,
                target="full_evigraph",
                baseline="evigraph_wo_operation_planner",
                retrieval_by_id=retrieval_by_id,
                questions=questions,
            ),
            "open_retrieval_failure": self._first_failure(
                list(by_method.get("full_evigraph", {}).values()),
                retrieval_by_id=retrieval_by_id,
                questions=questions,
            ),
        }
        if gpt_csv:
            cases["gpt_correct_but_unsupported"] = self._gpt_unsupported_case(gpt_csv, questions)
        return {
            "evigraph_csv": str(evigraph_csv),
            "gpt_csv": str(gpt_csv or ""),
            "questions_path": str(questions_path),
            "corpus_path": str(corpus_path or ""),
            "retrieval_mode": retrieval_mode,
            "cases": cases,
        }

    def render_markdown(self, selection: dict[str, Any]) -> str:
        lines = [
            "# Paper Case Studies",
            "",
            f"- EviGraph CSV: `{self._display_path(selection['evigraph_csv'])}`",
            f"- GPT CSV: `{self._display_path(selection['gpt_csv'])}`" if selection.get("gpt_csv") else "- GPT CSV: `n/a`",
            f"- Retrieval mode: `{selection['retrieval_mode']}`",
            "",
        ]
        titles = {
            "evigraph_over_direct": "EviGraph Win Over Direct RAG",
            "graph_selection_over_utility": "Graph Selection Win Over Utility-Only",
            "planner_over_no_planner": "Operation Planner Win",
            "open_retrieval_failure": "Open Retrieval / Operand Failure",
            "gpt_correct_but_unsupported": "GPT-5.4 Correct But Unsupported",
        }
        for key, title in titles.items():
            case = selection["cases"].get(key)
            lines.extend([f"## {title}", ""])
            if not case:
                lines.extend(["No case found.", ""])
                continue
            lines.extend(
                [
                    f"- id: `{case.get('id', '')}`",
                    f"- query: {case.get('query', '')}",
                    f"- gold: `{case.get('answer', '')}`",
                ]
            )
            if "target_prediction" in case:
                lines.append(f"- full EviGraph: `{self._shorten(case['target_prediction'], 180)}`")
                lines.append(f"- baseline `{case['baseline_method']}`: `{self._shorten(case['baseline_prediction'], 180)}`")
            if "gpt_prediction" in case:
                lines.append(f"- GPT prediction: `{self._shorten(case['gpt_prediction'], 180)}`")
                lines.append(f"- GPT answer_supported: `{case.get('gpt_answer_supported')}`")
            if "prediction" in case and "target_prediction" not in case and "gpt_prediction" not in case:
                lines.append(f"- prediction: `{self._shorten(case['prediction'], 180)}`")
            lines.append(
                "- retrieval: "
                f"source_hit={case.get('source_hit', 'n/a')}, "
                f"source_rank={case.get('source_rank', 'n/a')}, "
                f"gold_number_hit={case.get('gold_answer_number_hit', 'n/a')}, "
                f"query_year_hit={case.get('query_year_hit', 'n/a')}"
            )
            if case.get("paper_use"):
                lines.append(f"- paper use: {case['paper_use']}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def write(
        self,
        evigraph_csv: str | Path,
        questions_path: str | Path,
        corpus_path: str | Path | None,
        retrieval_mode: str,
        output_path: str | Path,
        gpt_csv: str | Path | None = None,
        top_k: int = 8,
    ) -> str:
        selection = self.select(
            evigraph_csv,
            questions_path=questions_path,
            corpus_path=corpus_path,
            retrieval_mode=retrieval_mode,
            gpt_csv=gpt_csv,
            top_k=top_k,
        )
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render_markdown(selection), encoding="utf-8")
        return str(output)

    def _first_case(
        self,
        by_method: dict[str, dict[str, dict[str, str]]],
        target: str,
        baseline: str,
        retrieval_by_id: dict[str, dict[str, Any]],
        questions: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        for sample_id, target_row in by_method.get(target, {}).items():
            baseline_row = by_method.get(baseline, {}).get(sample_id)
            if not baseline_row:
                continue
            if self._is_correct(target_row) and not self._is_correct(baseline_row):
                retrieval = retrieval_by_id.get(sample_id, {})
                return {
                    "id": sample_id,
                    "query": target_row.get("query", ""),
                    "answer": target_row.get("answer", ""),
                    "target_prediction": target_row.get("prediction", ""),
                    "baseline_method": baseline,
                    "baseline_prediction": baseline_row.get("prediction", ""),
                    "source_hit": retrieval.get("source_hit"),
                    "source_rank": retrieval.get("source_rank"),
                    "gold_answer_number_hit": retrieval.get("gold_answer_number_hit"),
                    "query_year_hit": retrieval.get("query_year_hit"),
                    "source_doc": questions.get(sample_id, {}).get("source_doc", ""),
                    "paper_use": "Shows which component changes the final answer on the same retrieval setting.",
                }
        return None

    def _first_failure(
        self,
        rows: list[dict[str, str]],
        retrieval_by_id: dict[str, dict[str, Any]],
        questions: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        for row in rows:
            if self._is_correct(row):
                continue
            retrieval = retrieval_by_id.get(row.get("id", ""), {})
            if retrieval.get("source_hit"):
                return {
                    "id": row.get("id", ""),
                    "query": row.get("query", ""),
                    "answer": row.get("answer", ""),
                    "prediction": row.get("prediction", ""),
                    "source_hit": retrieval.get("source_hit"),
                    "source_rank": retrieval.get("source_rank"),
                    "gold_answer_number_hit": retrieval.get("gold_answer_number_hit"),
                    "query_year_hit": retrieval.get("query_year_hit"),
                    "source_doc": questions.get(row.get("id", ""), {}).get("source_doc", ""),
                    "paper_use": "Shows that retrieval can hit the right source while operand grounding still fails.",
                }
        return None

    def _gpt_unsupported_case(
        self,
        gpt_csv: str | Path,
        questions: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        for row in self._read_rows(gpt_csv):
            if row.get("method") != "llm_direct_rag":
                continue
            if self._is_correct(row) and not self._truthy(row.get("answer_supported")):
                sample_id = row.get("id", "")
                question = questions.get(sample_id, {})
                return {
                    "id": sample_id,
                    "query": row.get("query", ""),
                    "answer": row.get("answer", ""),
                    "gpt_prediction": row.get("prediction", ""),
                    "gpt_answer_supported": row.get("answer_supported", ""),
                    "source_doc": question.get("source_doc", ""),
                    "paper_use": "Shows why exact match and verifier-supported evidence should be reported separately.",
                }
        return None

    def _by_method(self, rows: list[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
        grouped: dict[str, dict[str, dict[str, str]]] = {}
        for row in rows:
            grouped.setdefault(row.get("method", ""), {})[row.get("id", "")] = row
        return grouped

    def _read_rows(self, path: str | Path) -> list[dict[str, str]]:
        with Path(path).open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def _read_questions(self, path: str | Path) -> dict[str, dict[str, Any]]:
        questions: dict[str, dict[str, Any]] = {}
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                payload = json.loads(line)
                questions[str(payload.get("id", ""))] = payload
        return questions

    def _is_correct(self, row: dict[str, str]) -> bool:
        try:
            return float(row.get("accuracy", "0")) >= 1.0
        except ValueError:
            return False

    def _truthy(self, value: Any) -> bool:
        if isinstance(value, str):
            return value.strip().lower() in {"1", "1.0", "true", "yes"}
        return bool(value)

    def _display_path(self, path_text: str) -> str:
        if not path_text:
            return ""
        path = Path(path_text)
        try:
            return str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(path)

    def _shorten(self, text: str, limit: int) -> str:
        compact = " ".join(str(text).split())
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3].rstrip() + "..."
