from __future__ import annotations

import json
import os
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from scripts.run_pipeline import experiment_pipelines, run_llm_preflight, run_preflight


class RunPipelinePreflightTest(unittest.TestCase):
    def test_quick_pipeline_requires_existing_evaluation_csvs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            args = self._args(root, refresh_results=False)

            result = run_preflight(args)

        self.assertFalse(result.ok)
        self.assertIn("--refresh-results", result.stderr_tail)

    def test_refresh_pipeline_accepts_manifest_inputs_without_existing_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            args = self._args(root, refresh_results=True)

            result = run_preflight(args)

        self.assertTrue(result.ok, result.stderr_tail)
        self.assertIn("refresh mode", result.stdout_tail)

    def test_quick_pipeline_accepts_existing_evaluation_csvs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_dir = root / "eval"
            eval_dir.mkdir()
            (eval_dir / "results.csv").write_text("dataset,method,accuracy\n", encoding="utf-8")
            args = self._args(root, refresh_results=False, eval_dir=eval_dir)

            result = run_preflight(args)

        self.assertTrue(result.ok, result.stderr_tail)
        self.assertIn("evaluation CSV", result.stdout_tail)

    def test_submission_suite_registers_baselines_ablations_and_llm_direct_rag(self) -> None:
        args = self._args(Path(tempfile.mkdtemp()), refresh_results=True)
        args.suite = "submission"

        names = [experiment.name for experiment in experiment_pipelines(args)]

        self.assertIn("finqa_300_local_ablation", names)
        self.assertIn("finqa_300_retrieval_baselines", names)
        self.assertIn("finqa_300_llm_direct_rag", names)
        self.assertIn("finqa_600_llm_direct_rag", names)

    def test_llm_preflight_reports_missing_api_environment(self) -> None:
        old_values = {key: os.environ.pop(key, None) for key in ("LLM_PROVIDER", "LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")}
        try:
            result = run_llm_preflight("finqa_300_llm_direct_rag")
        finally:
            for key, value in old_values.items():
                if value is not None:
                    os.environ[key] = value

        self.assertFalse(result.ok)
        self.assertIn("LLM_API_KEY", result.stderr_tail)

    def _args(self, root: Path, refresh_results: bool, eval_dir: Path | None = None) -> Namespace:
        corpus = root / "corpus"
        corpus.mkdir()
        (corpus / "report.md").write_text("# Report\n", encoding="utf-8")
        raw_questions = root / "questions.jsonl"
        raw_questions.write_text('{"id":"q1","question":"q?","answer":"1"}\n', encoding="utf-8")
        config = root / "config.yaml"
        config.write_text("run:\n  output_dir: runs\n", encoding="utf-8")
        manifest = root / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "config": str(config),
                    "datasets": [
                        {
                            "raw_questions": str(raw_questions),
                            "corpus": str(corpus),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return Namespace(
            manifest=str(manifest),
            eval_dir=str(eval_dir or root / "missing_eval"),
            paper_output_dir=str(root / "paper"),
            report_dir=str(root / "pipeline"),
            suite="main",
            refresh_results=refresh_results,
            skip_tests=False,
            skip_paper_assets=False,
            skip_llm_direct_rag=False,
        )


if __name__ == "__main__":
    unittest.main()
