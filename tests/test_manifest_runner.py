from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evigraph.manifest import ManifestRunner
from evigraph.methods import MethodRunner
from scripts.run_query import load_config


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
            self.assertEqual(len(artifacts["row_operation_diagnostics"]), 1)
            self.assertTrue(Path(artifacts["row_operation_diagnostics"][0]).exists())
            self.assertTrue(Path(artifacts["summary"]).exists())
            self.assertTrue(Path(artifacts["card"]).exists())
            self.assertIn("Temp Manifest", Path(artifacts["card"]).read_text(encoding="utf-8"))
            self.assertIn("row_operation_diagnostics", Path(artifacts["card"]).read_text(encoding="utf-8"))

    def test_full_evigraph_handles_non_default_year_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus_dir = root / "corpus"
            corpus_dir.mkdir()
            (corpus_dir / "case_beta_report.md").write_text(
                "# Case Beta Official Report\n\n| year | value |\n| --- | ---: |\n| 2023 | 42.0 |\n| 2024 | 57.5 |\n",
                encoding="utf-8",
            )

            result = MethodRunner({"run": {"output_dir": str(root / "runs")}}).run(
                "In Case Beta, how much higher was 2024 than 2023?",
                "full_evigraph",
                corpus_path=str(corpus_dir),
            )

            self.assertEqual(result["answer"]["text"], "2024 is higher than 2023 by 15.5.")
            self.assertIn("calc_2024_minus_2023", result["selected_ids"])

    def test_operation_planner_ablation_disables_planned_numeric_fallback_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus_dir = root / "corpus"
            corpus_dir.mkdir()
            (corpus_dir / "report.md").write_text(
                "# Report\n\n"
                "| metric | amount |\n"
                "| --- | ---: |\n"
                "| average daily volume | 2.5 |\n"
                "| average price | 4.0 |\n",
                encoding="utf-8",
            )
            config = {
                "run": {"output_dir": str(root / "runs")},
                "numeric_planner": {
                    "enabled": True,
                    "llm_provider": "heuristic",
                    "primary_enabled": False,
                },
            }
            query = "compute the annualized traded value using 365 days"

            full = MethodRunner(config).run(query, "full_evigraph", corpus_path=str(corpus_dir), log_run=False)
            ablated = MethodRunner(config).run(
                query,
                "evigraph_wo_operation_planner",
                corpus_path=str(corpus_dir),
                log_run=False,
            )

            self.assertIn("planned_product", full["answer"]["calculations"][0])
            self.assertNotIn("planned_", " ".join(ablated["answer"].get("calculations", [])))

    def test_manifest_passes_configured_retrieval_top_k_to_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus_dir = root / "corpus"
            corpus_dir.mkdir()
            (corpus_dir / "report.md").write_text("target value 42\n", encoding="utf-8")
            raw_questions = root / "raw.jsonl"
            raw_questions.write_text(
                json.dumps({"qid": "q1", "question": "target value?", "gold_answer": "42"}) + "\n",
                encoding="utf-8",
            )
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "run": {"output_dir": str(root / "runs")},
                        "retrieval": {"top_k": 13},
                        "selection": {"max_nodes": 4},
                        "scoring": {"provider": "rule"},
                    }
                ),
                encoding="utf-8",
            )
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "title": "Top K Manifest",
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
                        "experiments": [{"name": "smoke", "type": "batch", "methods": ["full_evigraph"]}],
                    }
                ),
                encoding="utf-8",
            )
            seen_top_k: list[int] = []

            class FakeMethodRunner:
                def __init__(self, config: dict) -> None:
                    self.config = config

                def run(self, *args, **kwargs) -> dict:
                    seen_top_k.append(kwargs["top_k"])
                    return {
                        "answer": {"text": "42", "citations": [], "calculations": []},
                        "selected_ids": [],
                        "actions": [],
                        "verification": {"answer_supported": True},
                        "cost": {"selected_tokens": 0.0, "tool_calls": 0.0, "latency_ms": 0.0},
                        "artifacts": {"run_dir": str(root / "runs" / "fake")},
                    }

            with patch("evigraph.manifest.MethodRunner", FakeMethodRunner):
                ManifestRunner(manifest_path).run()

            self.assertEqual(seen_top_k, [13])

    def test_default_llm_planner_config_parses_boolean_enabled(self) -> None:
        config = load_config("configs/default_llm_planner.yaml")

        self.assertIs(config["numeric_planner"]["enabled"], True)
        self.assertEqual(config["numeric_planner"]["llm_provider"], "openai_compatible")


if __name__ == "__main__":
    unittest.main()
