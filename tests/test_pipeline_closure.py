from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from evigraph.pipeline import ExperimentClosureGate


class ExperimentClosureGateTest(unittest.TestCase):
    def test_accepts_complete_finqa_style_artifact_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path, eval_dir, paper_dir, report_dir = self._complete_artifacts(root)

            result = ExperimentClosureGate().evaluate(manifest_path, eval_dir, paper_dir, report_dir)

            self.assertTrue(result["ok"])
            self.assertTrue((report_dir / "experiment_closure_report.md").exists())
            self.assertEqual(len(result["metrics"]), 3)
            self.assertIn("oracle_doc_full_local_planner", result["metrics"][0]["experiment"])

    def test_rejects_missing_row_operation_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path, eval_dir, paper_dir, report_dir = self._complete_artifacts(root)
            (eval_dir / "finqa_300_subset_source_rerank_full_local_planner_row_operation_diagnostics.md").unlink()

            result = ExperimentClosureGate().evaluate(manifest_path, eval_dir, paper_dir, report_dir)

            self.assertFalse(result["ok"])
            failures = [check["name"] for check in result["checks"] if not check["ok"]]
            self.assertIn("finqa_300_subset_source_rerank_full_local_planner_row_operation_diagnostics", failures)

    def _complete_artifacts(self, root: Path) -> tuple[Path, Path, Path, Path]:
        eval_dir = root / "eval"
        paper_dir = root / "paper"
        report_dir = root / "pipeline"
        data_dir = root / "data"
        corpus_dir = root / "corpus"
        index_path = root / "index.json"
        eval_dir.mkdir()
        paper_dir.mkdir()
        data_dir.mkdir()
        corpus_dir.mkdir()
        report_dir.mkdir()
        raw_questions = data_dir / "raw.jsonl"
        questions = eval_dir / "questions.jsonl"
        records = [
            {"id": "q1", "question": "q1?", "answer": "1", "source_doc": "a.md"},
            {"id": "q2", "question": "q2?", "answer": "2", "source_doc": "b.md"},
        ]
        raw_questions.write_text("\n".join(json.dumps(row) for row in records) + "\n", encoding="utf-8")
        questions.write_text(raw_questions.read_text(encoding="utf-8"), encoding="utf-8")
        index_path.write_text("[]", encoding="utf-8")
        (eval_dir / "summary.md").write_text("# Summary\n", encoding="utf-8")
        (eval_dir / "experiment_card.md").write_text("# Card\n", encoding="utf-8")
        (eval_dir / "finqa_300_subset_inspection.json").write_text("{}", encoding="utf-8")
        (eval_dir / "finqa_300_subset_inspection.md").write_text("# Inspection\n", encoding="utf-8")
        (eval_dir / "finqa_300_subset_gate.md").write_text("# Gate\n", encoding="utf-8")
        (paper_dir / "finqa_results_summary.md").write_text("# Paper Summary\n", encoding="utf-8")
        (paper_dir / "finqa_results_tables.tex").write_text("\\begin{table}\\end{table}\n", encoding="utf-8")

        experiments = [
            "oracle_doc_full_local_planner",
            "open_bm25_full_local_planner",
            "source_rerank_full_local_planner",
        ]
        for experiment in experiments:
            csv_path = eval_dir / f"finqa_300_subset_{experiment}.csv"
            self._write_csv(csv_path, experiment, rows=2)
            csv_path.with_name(f"{csv_path.stem}_failures.md").write_text("# Failures\n", encoding="utf-8")
            csv_path.with_name(f"{csv_path.stem}_row_operation_diagnostics.md").write_text(
                "# Diagnostics\n", encoding="utf-8"
            )

        manifest_path = root / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "title": "Closure Test",
                    "config": str(root / "config.yaml"),
                    "output_dir": str(eval_dir),
                    "datasets": [
                        {
                            "name": "finqa_300_subset",
                            "raw_questions": str(raw_questions),
                            "questions": str(questions),
                            "corpus": str(corpus_dir),
                            "build_index": True,
                            "index": str(index_path),
                        }
                    ],
                    "experiments": [
                        {"name": name, "type": "batch", "methods": ["full_evigraph"]} for name in experiments
                    ],
                }
            ),
            encoding="utf-8",
        )
        return manifest_path, eval_dir, paper_dir, report_dir

    def _write_csv(self, path: Path, experiment: str, rows: int) -> None:
        fieldnames = [
            "dataset",
            "experiment",
            "id",
            "method",
            "query",
            "answer",
            "prediction",
            "accuracy",
            "answer_supported",
            "calculation_supported",
            "operation_semantics_checked",
            "row_operation_grounded",
        ]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for index in range(rows):
                writer.writerow(
                    {
                        "dataset": "finqa_300_subset",
                        "experiment": experiment,
                        "id": f"q{index}",
                        "method": "full_evigraph",
                        "query": "q?",
                        "answer": "1",
                        "prediction": "1",
                        "accuracy": "1",
                        "answer_supported": "1",
                        "calculation_supported": "1",
                        "operation_semantics_checked": "1",
                        "row_operation_grounded": "1",
                    }
                )


if __name__ == "__main__":
    unittest.main()
