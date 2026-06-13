from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from evigraph.experiment_card import ExperimentCard


class ExperimentCardTest(unittest.TestCase):
    def test_renders_audit_card_with_result_file_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result_path = root / "results.csv"
            with result_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["dataset", "method", "accuracy"])
                writer.writeheader()
                writer.writerow({"dataset": "mock", "method": "full_evigraph", "accuracy": "1"})

            manifest = {
                "title": "Smoke Card",
                "datasets": [{"name": "mock", "questions": "questions.jsonl"}],
                "experiments": [{"name": "ablation", "type": "batch", "methods": ["full_evigraph"]}],
                "limitations": ["mock-only"],
            }
            artifacts = {"evaluations": [str(result_path)], "summary": str(root / "summary.md")}

            text = ExperimentCard().render("manifest.json", manifest, artifacts)

            self.assertIn("# Smoke Card", text)
            self.assertIn("## Run Metadata", text)
            self.assertIn("| mock | questions.jsonl", text)
            self.assertIn("full_evigraph", text)
            self.assertIn("dataset, method, accuracy", text)
            self.assertIn("- mock-only", text)


if __name__ == "__main__":
    unittest.main()
