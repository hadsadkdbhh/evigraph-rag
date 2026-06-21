from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from evigraph.row_operation_diagnostics import RowOperationDiagnosticAnalyzer


class RowOperationDiagnosticAnalyzerTest(unittest.TestCase):
    def test_diagnoses_wrong_numerator_from_ratio_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self._write_run(
                root,
                "ratio_percent row=tower cash flow for the three months ended december 31 2005 "
                "denominator_row=adjusted consolidated cash flow for the twelve months ended december 31 2005: "
                "139590 / 531822 * 100 = 26.2%",
                "tower cash flow for the twelve months ended december 31 2005 | 558360\n"
                "adjusted consolidated cash flow for the twelve months ended december 31 2005 | 531822",
            )
            csv_path = self._write_csv(
                root,
                [
                    {
                        "id": "case-ratio",
                        "query": "what portion of adjusted consolidated cash flow for the twelve months ended december 31 2005 is related to tower cash flow?",
                        "answer": "105.0%",
                        "prediction": "26.2%",
                        "accuracy": "0.0",
                        "run_dir": str(run_dir),
                    }
                ],
            )

            analysis = RowOperationDiagnosticAnalyzer().analyze(csv_path)

        diagnostic = analysis["diagnostics"][0]
        self.assertIn("wrong_numerator", diagnostic["labels"])
        self.assertIn("wrong_year_or_period", diagnostic["labels"])
        self.assertEqual(analysis["label_counts"]["wrong_numerator"], 1)

    def test_diagnoses_wrong_operation_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self._write_run(
                root,
                "ratio_percent row=net commodities denominator_row=total commodities: 1 / 200 * 100 = 0.5%",
                "net commodities | 211 | 2016\nnet commodities | 136 | 2017",
            )
            csv_path = self._write_csv(
                root,
                [
                    {
                        "id": "case-operation",
                        "query": "what is the percentage change in net commodities from 2016 to 2017?",
                        "answer": "-35.6%",
                        "prediction": "0.5%",
                        "accuracy": "0.0",
                        "run_dir": str(run_dir),
                    }
                ],
            )

            analysis = RowOperationDiagnosticAnalyzer().analyze(csv_path)

        self.assertEqual(analysis["primary_counts"]["wrong_operation_type"], 1)
        self.assertIn("wrong_operation_type", analysis["diagnostics"][0]["labels"])

    def test_planned_percent_change_matches_percent_of_change_query(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self._write_run(
                root,
                "planned_percent_change target=segment revenue/2009 base=segment revenue/2008: "
                "(6305 - 6197) / 6197 * 100 = 1.7%",
                "segment revenue | 2008 | 6197\nsegment revenue | 2009 | 6305",
            )
            csv_path = self._write_csv(
                root,
                [
                    {
                        "id": "case-planned-percent-change",
                        "query": "what was the percent of the change in segment revenue from 2008 2009",
                        "answer": "1.6%",
                        "prediction": "1.7%",
                        "accuracy": "0.0",
                        "run_dir": str(run_dir),
                    }
                ],
            )

            analysis = RowOperationDiagnosticAnalyzer().analyze(csv_path)

        self.assertNotIn("wrong_operation_type", analysis["diagnostics"][0]["labels"])

    def test_diagnoses_missing_row_label_trace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self._write_run(
                root,
                "percent_change: (211 - 254) / 254 * 100 = -16.9%",
                "rental expense | 2008 | 100\nrental expense | 2009 | 117",
            )
            csv_path = self._write_csv(
                root,
                [
                    {
                        "id": "case-row",
                        "query": "what was the percentage change in rental expense from 2008 to 2009?",
                        "answer": "17%",
                        "prediction": "-16.9%",
                        "accuracy": "0.0",
                        "run_dir": str(run_dir),
                    }
                ],
            )

            analysis = RowOperationDiagnosticAnalyzer().analyze(csv_path)

        self.assertIn("wrong_row_label", analysis["diagnostics"][0]["labels"])

    def _write_run(self, root: Path, calculation: str, context: str) -> Path:
        run_dir = root / f"run_{len(list(root.glob('run_*')))}"
        run_dir.mkdir()
        (run_dir / "answer.md").write_text(
            f"# Answer\n\n1\n## Calculations\n- {calculation}\n\n## Query\nq\n",
            encoding="utf-8",
        )
        (run_dir / "support_graph.json").write_text(
            json.dumps({"nodes": [{"node_id": "n1", "content": context}], "edges": []}),
            encoding="utf-8",
        )
        return run_dir

    def _write_csv(self, root: Path, rows: list[dict[str, str]]) -> Path:
        path = root / "results.csv"
        fieldnames = ["id", "method", "query", "answer", "prediction", "accuracy", "run_dir"]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({"method": "full_evigraph", **row})
        return path


if __name__ == "__main__":
    unittest.main()
