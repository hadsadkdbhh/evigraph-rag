from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from evigraph.version_compare import EvalVersionComparator


class EvalVersionComparatorTest(unittest.TestCase):
    def test_compares_matched_retrieval_mode_csvs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "v34"
            target = root / "v35"
            baseline.mkdir()
            target.mkdir()
            self._write_csv(
                baseline / "finqa_open_bm25_full_local_planner_v34.csv",
                [
                    {"id": "a", "answer": "1", "prediction": "0", "accuracy": "0"},
                    {"id": "b", "answer": "2", "prediction": "2", "accuracy": "1"},
                    {"id": "c", "answer": "3", "prediction": "3", "accuracy": "1"},
                ],
            )
            self._write_csv(
                target / "finqa_open_bm25_full_local_planner_v35.csv",
                [
                    {"id": "a", "answer": "1", "prediction": "1", "accuracy": "1"},
                    {"id": "b", "answer": "2", "prediction": "0", "accuracy": "0"},
                    {"id": "c", "answer": "3", "prediction": "3", "accuracy": "1"},
                ],
            )

            report = EvalVersionComparator().compare_dirs(
                baseline,
                target,
                baseline_label="v34",
                target_label="v35",
            )

            self.assertEqual(len(report["rows"]), 1)
            row = report["rows"][0]
            self.assertEqual(row["mode"], "open_bm25")
            self.assertAlmostEqual(row["baseline_accuracy"], 2 / 3)
            self.assertAlmostEqual(row["target_accuracy"], 2 / 3)
            self.assertEqual(row["target_only"], 1)
            self.assertEqual(row["baseline_only"], 1)
            self.assertEqual(row["ties"], 1)
            self.assertEqual(row["target_only_examples"][0]["id"], "a")

    def test_skips_empty_target_csv(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "v34"
            target = root / "v35"
            baseline.mkdir()
            target.mkdir()
            self._write_csv(
                baseline / "finqa_source_rerank_full_local_planner_v34.csv",
                [{"id": "a", "answer": "1", "prediction": "1", "accuracy": "1"}],
            )
            (target / "finqa_source_rerank_full_local_planner_v35.csv").write_text("", encoding="utf-8")

            report = EvalVersionComparator().compare_dirs(baseline, target)

            self.assertEqual(report["rows"], [])

    def test_renders_markdown_report(self) -> None:
        report = {
            "baseline_dir": "old",
            "target_dir": "new",
            "baseline_label": "v34",
            "target_label": "v35",
            "rows": [
                {
                    "mode": "oracle_doc",
                    "n": 1,
                    "baseline_accuracy": 0.0,
                    "target_accuracy": 1.0,
                    "delta_accuracy": 1.0,
                    "target_only": 1,
                    "baseline_only": 0,
                    "ties": 0,
                    "target_only_examples": [
                        {"id": "x", "answer": "388", "baseline_prediction": "250", "target_prediction": "388"}
                    ],
                }
            ],
        }

        markdown = EvalVersionComparator().render_markdown(report)

        self.assertIn("| oracle_doc | 1 | 0.000 | 1.000 | 1.000 | 1 | 0 | 0 |", markdown)
        self.assertIn("`x`", markdown)

    def _write_csv(self, path: Path, rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["id", "query", "answer", "prediction", "accuracy"])
            writer.writeheader()
            for row in rows:
                writer.writerow({"query": "", **row})


if __name__ == "__main__":
    unittest.main()
