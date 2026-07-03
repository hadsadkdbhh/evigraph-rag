from __future__ import annotations

import csv
import json
import re
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

    def test_direct_rag_and_retrieve_then_program_split_planner_use(self) -> None:
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

            direct = MethodRunner(config).run(query, "direct_rag", corpus_path=str(corpus_dir), log_run=False)
            programmed = MethodRunner(config).run(
                query,
                "retrieve_then_program",
                corpus_path=str(corpus_dir),
                log_run=False,
            )

            self.assertNotIn("planned_", " ".join(direct["answer"].get("calculations", [])))
            self.assertIn("planned_product", programmed["answer"]["calculations"][0])

    def test_llm_direct_rag_uses_external_llm_context_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus_dir = root / "corpus"
            corpus_dir.mkdir()
            (corpus_dir / "report.md").write_text(
                "# Report\n\n"
                "Cash paid was 6.9 and estimated purchase price was 220.6.\n",
                encoding="utf-8",
            )

            class FakeLLM:
                def __init__(self) -> None:
                    self.messages: list[dict[str, str]] = []

                def chat_json(self, messages, schema=None, temperature=0.0):
                    self.messages = messages
                    citation = re.search(r"\[(retrieved_[^\]]+)\]", messages[1]["content"]).group(1)
                    return {
                        "answer": "3.1%",
                        "citations": [citation],
                        "calculation": "6.9 / 220.6 * 100 = 3.1%",
                    }

            fake_llm = FakeLLM()
            config = {
                "run": {"output_dir": str(root / "runs")},
                "selection": {"max_nodes": 4},
                "llm_direct_rag": {"provider": "openai_compatible"},
            }
            with patch("evigraph.generator.make_llm_client", return_value=fake_llm):
                result = MethodRunner(config).run(
                    "What percentage of the estimated purchase price was paid in cash?",
                    "llm_direct_rag",
                    corpus_path=str(corpus_dir),
                    log_run=False,
            )

            self.assertEqual(result["answer"]["text"], "3.1%")
            self.assertEqual(result["answer"]["citations"], result["selected_ids"][:1])
            self.assertIn("6.9 / 220.6", result["answer"]["calculations"][0])
            self.assertIn("Retrieved context", fake_llm.messages[1]["content"])
            self.assertNotIn("planned_", " ".join(result["answer"].get("calculations", [])))

    def test_llm_direct_rag_can_continue_after_external_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus_dir = root / "corpus"
            corpus_dir.mkdir()
            (corpus_dir / "report.md").write_text("Cash paid was 6.9.\n", encoding="utf-8")

            class FailingLLM:
                def chat_json(self, messages, schema=None, temperature=0.0):
                    raise RuntimeError("timed out")

            config = {
                "run": {"output_dir": str(root / "runs")},
                "llm_direct_rag": {"provider": "openai_compatible", "continue_on_error": True},
            }
            with patch("evigraph.generator.make_llm_client", return_value=FailingLLM()):
                result = MethodRunner(config).run(
                    "What percentage was paid in cash?",
                    "llm_direct_rag",
                    corpus_path=str(corpus_dir),
                    log_run=False,
                )

            self.assertEqual(result["answer"]["text"], "Insufficient evidence to answer.")
            self.assertIn("llm_error", result["answer"]["calculations"][0])

    def test_manifest_failure_reports_use_llm_direct_rag_method_when_no_full_evigraph(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_questions = root / "raw.jsonl"
            raw_questions.write_text(
                json.dumps({"qid": "q1", "question": "What was revenue?", "gold_answer": "42"}) + "\n",
                encoding="utf-8",
            )
            config_path = root / "config.json"
            config_path.write_text(json.dumps({"run": {"output_dir": str(root / "runs")}}), encoding="utf-8")
            eval_dir = root / "eval"
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "title": "LLM Baseline Manifest",
                        "config": str(config_path),
                        "output_dir": str(eval_dir),
                        "datasets": [
                            {
                                "name": "temp",
                                "raw_questions": str(raw_questions),
                                "questions": str(eval_dir / "questions.jsonl"),
                                "field_map": {"id": "qid", "query": "question", "answer": "gold_answer"},
                            }
                        ],
                        "experiments": [{"name": "llm", "type": "batch", "methods": ["llm_direct_rag"]}],
                    }
                ),
                encoding="utf-8",
            )

            class FakeMethodRunner:
                def __init__(self, config: dict) -> None:
                    self.config = config

                def run(self, *args, **kwargs) -> dict:
                    return {
                        "answer": {"text": "41", "citations": [], "calculations": []},
                        "selected_ids": [],
                        "actions": [],
                        "verification": {"answer_supported": False},
                        "cost": {"selected_tokens": 0.0, "tool_calls": 1.0, "latency_ms": 60.0},
                        "artifacts": {"run_dir": str(root / "runs" / "fake")},
                    }

            with patch("evigraph.manifest.MethodRunner", FakeMethodRunner):
                artifacts = ManifestRunner(manifest_path).run()

            failure_text = Path(artifacts["failure_reports"][0]).read_text(encoding="utf-8")
            diagnostic_text = Path(artifacts["row_operation_diagnostics"][0]).read_text(encoding="utf-8")
            self.assertIn("- Method: `llm_direct_rag`", failure_text)
            self.assertIn("- Total: 1", failure_text)
            self.assertIn("- Method: `llm_direct_rag`", diagnostic_text)
            self.assertIn("- Total rows for method: 1", diagnostic_text)

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

    def test_manifest_resumes_incomplete_batch_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_questions = root / "raw.jsonl"
            raw_questions.write_text(
                "\n".join(
                    [
                        json.dumps({"qid": "q1", "question": "first?", "gold_answer": "42"}),
                        json.dumps({"qid": "q2", "question": "second?", "gold_answer": "42"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps({"run": {"output_dir": str(root / "runs")}, "scoring": {"provider": "rule"}}),
                encoding="utf-8",
            )
            eval_dir = root / "eval"
            eval_dir.mkdir()
            output_csv = eval_dir / "temp_smoke.csv"
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
                "arithmetically_supported",
                "calculation_supported",
                "operation_semantics_checked",
                "row_operation_grounded",
                "semantically_grounded",
                "citation_correct",
                "misleading_acceptance",
                "input_tokens",
                "tool_calls",
                "latency_ms",
                "run_dir",
            ]
            with output_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(
                    {
                        "dataset": "temp",
                        "experiment": "smoke",
                        "id": "q1",
                        "method": "full_evigraph",
                        "query": "first?",
                        "answer": "42",
                        "prediction": "42",
                        "accuracy": "1",
                        "answer_supported": "1",
                        "arithmetically_supported": "1",
                        "calculation_supported": "1",
                        "operation_semantics_checked": "1",
                        "row_operation_grounded": "1",
                        "semantically_grounded": "1",
                        "citation_correct": "1",
                        "misleading_acceptance": "0",
                        "input_tokens": "0",
                        "tool_calls": "0",
                        "latency_ms": "0",
                        "run_dir": str(root / "runs" / "existing"),
                    }
                )
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "title": "Resume Manifest",
                        "config": str(config_path),
                        "output_dir": str(eval_dir),
                        "datasets": [
                            {
                                "name": "temp",
                                "raw_questions": str(raw_questions),
                                "questions": str(eval_dir / "questions.jsonl"),
                                "field_map": {"id": "qid", "query": "question", "answer": "gold_answer"},
                            }
                        ],
                        "experiments": [{"name": "smoke", "type": "batch", "methods": ["full_evigraph"]}],
                    }
                ),
                encoding="utf-8",
            )
            seen_queries: list[str] = []

            class FakeMethodRunner:
                def __init__(self, config: dict) -> None:
                    self.config = config

                def run(self, query: str, *args, **kwargs) -> dict:
                    seen_queries.append(query)
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

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(seen_queries, ["second?"])
            self.assertEqual([(row["id"], row["method"]) for row in rows], [("q1", "full_evigraph"), ("q2", "full_evigraph")])

    def test_default_llm_planner_config_parses_boolean_enabled(self) -> None:
        config = load_config("configs/default_llm_planner.yaml")

        self.assertIs(config["numeric_planner"]["enabled"], True)
        self.assertEqual(config["numeric_planner"]["llm_provider"], "openai_compatible")

    def test_default_llm_direct_rag_config_parses(self) -> None:
        config = load_config("configs/default_llm_direct_rag.yaml")

        self.assertIs(config["numeric_planner"]["enabled"], False)
        self.assertEqual(config["llm_direct_rag"]["provider"], "openai_compatible")
        self.assertEqual(config["llm_direct_rag"]["max_context_chars"], 12000)


if __name__ == "__main__":
    unittest.main()
