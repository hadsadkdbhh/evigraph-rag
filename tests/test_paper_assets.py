from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from evigraph.paper_assets import PaperAssetBuilder


class PaperAssetBuilderTest(unittest.TestCase):
    def test_builds_latex_and_markdown_tables_from_finqa_csvs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_dir = root / "eval"
            output_dir = root / "paper"
            eval_dir.mkdir()
            self._write_eval_csv(
                eval_dir / "finqa_subset_oracle_doc_ablation.csv",
                [
                    ("topk", "0.50", "42"),
                    ("utility_only", "0.40", "35"),
                    ("full_evigraph", "0.60", "37"),
                    ("full_evigraph", "0.00", "Based on the selected evidence: no number"),
                ],
            )
            self._write_eval_csv(
                eval_dir / "finqa_subset_open_bm25_ablation.csv",
                [
                    ("topk", "0.30", "7"),
                    ("utility_only", "0.20", "Based on the selected evidence: x"),
                    ("full_evigraph", "0.40", "wrong 5"),
                ],
            )
            self._write_eval_csv(
                eval_dir / "finqa_subset_open_hybrid_ablation.csv",
                [
                    ("topk", "0.35", "7"),
                    ("utility_only", "0.25", "Based on the selected evidence: x"),
                    ("full_evigraph", "0.45", "wrong 5"),
                ],
            )
            self._write_eval_csv(
                eval_dir / "finqa_subset_source_rerank_ablation.csv",
                [
                    ("topk", "0.50", "7"),
                    ("utility_only", "0.45", "7"),
                    ("full_evigraph", "0.55", "9"),
                ],
            )

            paths = PaperAssetBuilder().build(eval_dir, output_dir)

            latex = Path(paths["latex"]).read_text(encoding="utf-8")
            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")

        self.assertIn("\\label{tab:finqa-diagnostic-results}", latex)
        self.assertIn("Oracle-doc & Full EviGraph", latex)
        self.assertIn("Open BM25", markdown)
        self.assertIn("Open hybrid", markdown)
        self.assertIn("Full EviGraph", markdown)
        self.assertIn("supported EM", markdown)
        self.assertIn("SupEM", latex)
        self.assertIn("wrong row/op", markdown)
        self.assertIn("Process Trace Diagnostics", markdown)
        self.assertIn("\\label{tab:finqa-process-diagnostics}", latex)
        self.assertIn("Paper-Safe Claims", markdown)

    def test_builds_tables_from_alternate_finqa_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_dir = root / "eval"
            output_dir = root / "paper"
            eval_dir.mkdir()
            for suffix in [
                "oracle_doc_ablation",
                "open_bm25_ablation",
                "open_hybrid_ablation",
                "source_rerank_ablation",
            ]:
                self._write_eval_csv(
                    eval_dir / f"finqa_300_subset_{suffix}.csv",
                    [("topk", "0.50", "7"), ("utility_only", "0.45", "7"), ("full_evigraph", "0.55", "9")],
                )

            paths = PaperAssetBuilder().build(eval_dir, output_dir)
            latex = Path(paths["latex"]).read_text(encoding="utf-8")

        self.assertIn("\\caption{FinQA diagnostic results.", latex)
        self.assertIn("Oracle-doc & Full EviGraph", latex)

    def test_builds_tables_from_finqa_300_local_planner_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_dir = root / "eval"
            output_dir = root / "paper"
            eval_dir.mkdir()
            for suffix in [
                "oracle_doc_full_local_planner",
                "open_bm25_full_local_planner",
                "source_rerank_full_local_planner",
            ]:
                self._write_eval_csv(
                    eval_dir / f"finqa_300_subset_{suffix}.csv",
                    [("full_evigraph", "0.55", "9")],
                )

            paths = PaperAssetBuilder().build(eval_dir, output_dir, preset="finqa_300_local")
            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")

        self.assertIn("Oracle-doc", markdown)
        self.assertIn("Open BM25", markdown)
        self.assertIn("BM25 + source rerank", markdown)
        self.assertIn("supported EM", markdown)
        self.assertNotIn("Component Contribution Diagnostics", markdown)

    def test_builds_tables_from_finqa_300_retrieval_baseline_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_dir = root / "eval"
            output_dir = root / "paper"
            eval_dir.mkdir()
            for suffix in [
                "open_bm25_baseline",
                "open_dense_baseline",
                "open_hybrid_baseline",
            ]:
                self._write_eval_csv(
                    eval_dir / f"finqa_300_subset_{suffix}.csv",
                    [("topk", "0.40", "7"), ("full_context", "0.35", "8"), ("full_evigraph", "0.45", "9")],
                )

            paths = PaperAssetBuilder().build(
                eval_dir,
                output_dir,
                preset="finqa_300_local_retrieval_baselines",
            )
            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")

        self.assertIn("Open dense", markdown)
        self.assertIn("Full context", markdown)
        self.assertIn("Top-k Program", markdown)

    def test_builds_tables_from_finqa_300_strong_retrieval_baseline_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_dir = root / "eval"
            output_dir = root / "paper"
            eval_dir.mkdir()
            for suffix in [
                "open_bm25_baseline",
                "open_tfidf_baseline",
                "open_hybrid_baseline",
            ]:
                self._write_eval_csv(
                    eval_dir / f"finqa_300_subset_{suffix}.csv",
                    [("topk", "0.40", "7"), ("full_context", "0.35", "8"), ("full_evigraph", "0.45", "9")],
                )

            paths = PaperAssetBuilder().build(
                eval_dir,
                output_dir,
                preset="finqa_300_local_strong_retrieval_baselines",
            )
            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")

        self.assertIn("Open TF-IDF", markdown)
        self.assertIn("Open hybrid", markdown)

    def test_builds_tables_from_finqa_300_neural_retrieval_baseline_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_dir = root / "eval"
            output_dir = root / "paper"
            eval_dir.mkdir()
            for suffix in [
                "open_bm25_baseline",
                "open_neural_dense_baseline",
                "open_neural_hybrid_baseline",
            ]:
                self._write_eval_csv(
                    eval_dir / f"finqa_300_subset_{suffix}.csv",
                    [("direct_rag", "0.38", "7"), ("retrieve_then_program", "0.42", "8"), ("full_evigraph", "0.46", "9")],
                )

            paths = PaperAssetBuilder().build(
                eval_dir,
                output_dir,
                preset="finqa_300_neural_retrieval_baselines",
            )
            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")

        self.assertIn("Open neural dense", markdown)
        self.assertIn("Open neural hybrid", markdown)
        self.assertIn("Retrieve-then-program", markdown)

    def test_builds_tables_from_finqa_300_llm_direct_rag_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_dir = root / "eval"
            output_dir = root / "paper"
            eval_dir.mkdir()
            for suffix in [
                "oracle_doc_llm_direct_rag",
                "open_bm25_llm_direct_rag",
                "source_rerank_llm_direct_rag",
            ]:
                self._write_eval_csv(
                    eval_dir / f"finqa_300_subset_{suffix}.csv",
                    [("llm_direct_rag", "0.42", "7")],
                )

            paths = PaperAssetBuilder().build(
                eval_dir,
                output_dir,
                preset="finqa_300_llm_direct_rag",
            )
            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")

        self.assertIn("LLM Direct RAG", markdown)
        self.assertIn("BM25 + source rerank", markdown)
        self.assertIn("| Oracle-doc | 1 |", markdown)

    def test_builds_tables_from_split_gpt54_direct_rag_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_root = root / "eval"
            base_dir = eval_root / "paper_anchor"
            oracle_source_dir = eval_root / "finqa_300_gpt54_direct_rag_oracle_source"
            open_dir = eval_root / "finqa_300_gpt54_direct_rag_open_bm25"
            output_dir = root / "paper"
            base_dir.mkdir(parents=True)
            oracle_source_dir.mkdir()
            open_dir.mkdir()
            self._write_eval_csv(
                oracle_source_dir / "finqa_300_subset_oracle_doc_gpt54_direct_rag.csv",
                [("llm_direct_rag", "0.69", "7")],
            )
            self._write_eval_csv(
                open_dir / "finqa_300_subset_open_bm25_gpt54_direct_rag.csv",
                [("llm_direct_rag", "0.52", "7")],
            )
            self._write_eval_csv(
                oracle_source_dir / "finqa_300_subset_source_rerank_gpt54_direct_rag.csv",
                [("llm_direct_rag", "0.68", "7")],
            )

            paths = PaperAssetBuilder().build(
                base_dir,
                output_dir,
                preset="finqa_300_gpt54_direct_rag",
            )
            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")

        self.assertIn("LLM Direct RAG", markdown)
        self.assertIn("| Open BM25 | LLM Direct RAG | 0.52", markdown)
        self.assertIn("BM25 + source rerank", markdown)

    def test_builds_tables_from_finqa_600_local_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_dir = root / "eval"
            output_dir = root / "paper"
            eval_dir.mkdir()
            for suffix in [
                "oracle_doc_full_local_planner",
                "open_bm25_full_local_planner",
                "source_rerank_full_local_planner",
            ]:
                self._write_eval_csv(
                    eval_dir / f"finqa_600_subset_{suffix}.csv",
                    [("full_evigraph", "0.41", "7")],
                )

            paths = PaperAssetBuilder().build(eval_dir, output_dir, preset="finqa_600_local")
            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")

        self.assertIn("Oracle-doc", markdown)
        self.assertIn("Full EviGraph", markdown)

    def test_builds_tables_from_finqa_600_llm_direct_rag_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            eval_dir = root / "eval"
            output_dir = root / "paper"
            eval_dir.mkdir()
            for suffix in [
                "oracle_doc_llm_direct_rag",
                "open_bm25_llm_direct_rag",
                "source_rerank_llm_direct_rag",
            ]:
                self._write_eval_csv(
                    eval_dir / f"finqa_600_subset_{suffix}.csv",
                    [("llm_direct_rag", "0.38", "7")],
                )

            paths = PaperAssetBuilder().build(eval_dir, output_dir, preset="finqa_600_llm_direct_rag")
            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")

        self.assertIn("LLM Direct RAG", markdown)
        self.assertIn("BM25 + source rerank", markdown)

    def _write_eval_csv(self, path: Path, rows: list[tuple[str, str, str]]) -> None:
        fieldnames = [
            "dataset",
            "method",
            "id",
            "query",
            "answer",
            "prediction",
            "accuracy",
            "answer_supported",
            "calculation_supported",
            "operation_semantics_checked",
            "row_operation_grounded",
            "input_tokens",
        ]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for index, (method, accuracy, prediction) in enumerate(rows):
                writer.writerow(
                    {
                        "dataset": "finqa_subset",
                        "method": method,
                        "id": f"case-{index}",
                        "query": "what percent changed?",
                        "answer": "10",
                        "prediction": prediction,
                        "accuracy": accuracy,
                        "answer_supported": "1",
                        "calculation_supported": "1",
                        "operation_semantics_checked": "1",
                        "row_operation_grounded": "1",
                        "input_tokens": "100",
                    }
                )


if __name__ == "__main__":
    unittest.main()
