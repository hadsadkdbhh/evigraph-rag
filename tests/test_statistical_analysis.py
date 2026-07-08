from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from evigraph.statistical_analysis import StatisticalAnalyzer


class StatisticalAnalyzerTest(unittest.TestCase):
    def test_reports_intervals_and_paired_mcnemar_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            csv_path = root / "results.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["id", "method", "accuracy"])
                writer.writeheader()
                writer.writerows(
                    [
                        {"id": "a", "method": "full_evigraph", "accuracy": "1"},
                        {"id": "b", "method": "full_evigraph", "accuracy": "1"},
                        {"id": "c", "method": "full_evigraph", "accuracy": "0"},
                        {"id": "a", "method": "direct_rag", "accuracy": "0"},
                        {"id": "b", "method": "direct_rag", "accuracy": "1"},
                        {"id": "c", "method": "direct_rag", "accuracy": "1"},
                    ]
                )

            analysis = StatisticalAnalyzer().analyze(
                [csv_path],
                baselines=("direct_rag",),
            )
            markdown = StatisticalAnalyzer().render_markdown(analysis)

        report = analysis["reports"][0]
        full_interval = next(row for row in report["intervals"] if row["method"] == "full_evigraph")
        paired = report["paired"][0]
        self.assertEqual(full_interval["n"], 3)
        self.assertEqual(full_interval["correct"], 2)
        self.assertAlmostEqual(full_interval["accuracy"], 2 / 3)
        self.assertEqual(paired["target_only"], 1)
        self.assertEqual(paired["baseline_only"], 1)
        self.assertEqual(paired["ties"], 1)
        self.assertIn("McNemar p", markdown)


if __name__ == "__main__":
    unittest.main()
