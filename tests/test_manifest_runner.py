from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evigraph.manifest import ManifestRunner


class ManifestRunnerTest(unittest.TestCase):
    def test_manifest_runs_conversion_index_eval_summary_and_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus_dir = root / "corpus"
            corpus_dir.mkdir()
            (corpus_dir / "report.md").write_text(
                "# Report\n\n| year | value |\n| --- | ---: |\n| 2022 | 87.5 |\n| 2023 | 100.0 |\n",
                encoding="utf-8",
            )
            raw_questions = root / "raw.jsonl"
            raw_questions.write_text(
                json.dumps(
                    {
                        "qid": "q1",
                        "question": "According to the chart, how much higher was 2023 than 2022?",
                        "gold_answer": "12.5",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "run": {"output_dir": str(root / "runs")},
                        "selection": {"max_nodes": 4, "risk_threshold": 0.65},
                        "scoring": {"provider": "rule"},
                    }
                ),
                encoding="utf-8",
            )
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "title": "Temp Manifest",
                        "config": str(config_path),
                        "output_dir": str(root / "eval"),
                        "datasets": [
                            {
                                "name": "temp",
                                "raw_questions": str(raw_questions),
                                "questions": str(root / "eval" / "questions.jsonl"),
                                "field_map": {"id": "qid", "query": "question", "answer": "gold_answer"},
                                "corpus": str(corpus_dir),
                                "build_index": True,
                                "index": str(root / "index.json"),
                            }
                        ],
                        "experiments": [
                            {"name": "smoke", "type": "batch", "methods": ["full_evigraph"]},
                            {"name": "budget", "type": "pareto", "method": "full_evigraph", "budgets": [1]},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            artifacts = ManifestRunner(manifest_path).run()

            self.assertTrue(Path(artifacts["converted"][0]).exists())
            self.assertTrue(Path(artifacts["indexes"][0]).exists())
            self.assertEqual(len(artifacts["evaluations"]), 2)
            for evaluation in artifacts["evaluations"]:
                self.assertTrue(Path(evaluation).exists())
            self.assertTrue(Path(artifacts["summary"]).exists())
            self.assertTrue(Path(artifacts["card"]).exists())
            self.assertIn("Temp Manifest", Path(artifacts["card"]).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
