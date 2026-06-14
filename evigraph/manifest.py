from __future__ import annotations

import csv
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from evigraph.experiment_report import ExperimentReport
from evigraph.experiment_card import ExperimentCard
from evigraph.failure_analysis import FailureAnalyzer
from evigraph.indexing import LocalIndexBuilder
from evigraph.dataset_adapter import DatasetAdapter
from evigraph.dataset_inspector import BenchmarkGate, DatasetInspector
from evigraph.methods import METHODS, MethodRunner
from evigraph.metrics import summarize_result


DEFAULT_ABLATION_METHODS = [
    "topk",
    "utility_only",
    "evigraph_wo_risk",
    "evigraph_wo_verifier",
    "evigraph_wo_support",
    "full_evigraph",
]


class ManifestRunner:
    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest_path = Path(manifest_path)
        self.root = self.manifest_path.resolve().parents[1] if self.manifest_path.parent.name == "configs" else Path.cwd()
        self.manifest = self._read_manifest(self.manifest_path)
        self.output_dir = self._resolve(self.manifest.get("output_dir", "outputs/eval/manifest"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict[str, Any]:
        config = self._read_config(self.manifest.get("config", "configs/default.yaml"))
        artifacts: dict[str, Any] = {
            "converted": [],
            "inspections": [],
            "gates": [],
            "indexes": [],
            "evaluations": [],
            "summary": None,
            "card": None,
            "failure_reports": [],
        }
        summary_inputs: list[Path] = []

        for dataset in self.manifest.get("datasets", []):
            dataset_name = dataset["name"]
            questions_path = self._prepare_questions(dataset)
            corpus_path = self._prepare_corpus(dataset)
            inspection_artifacts = self._inspect_dataset(dataset, questions_path, corpus_path)
            artifacts["inspections"].append(str(inspection_artifacts["inspection"]))
            artifacts["gates"].append(str(inspection_artifacts["gate"]))
            for experiment in self.manifest.get("experiments", []):
                output_path = self.output_dir / f"{dataset_name}_{experiment['name']}.csv"
                retrieval_mode = experiment.get("retrieval_mode", dataset.get("retrieval_mode", "oracle_doc"))
                self._run_experiment(
                    experiment,
                    dataset_name,
                    questions_path,
                    corpus_path,
                    config,
                    output_path,
                    retrieval_mode,
                )
                artifacts["evaluations"].append(str(output_path))
                summary_inputs.append(output_path)
                if experiment.get("type", "batch") != "pareto":
                    failure_path = self.output_dir / f"{dataset_name}_{experiment['name']}_failures.md"
                    FailureAnalyzer().write(output_path, failure_path, method="full_evigraph")
                    artifacts["failure_reports"].append(str(failure_path))
            if dataset.get("build_index"):
                artifacts["indexes"].append(str(self._resolve(dataset["index"])))
            if dataset.get("raw_questions"):
                artifacts["converted"].append(str(questions_path))

        if summary_inputs:
            summary_path = self.output_dir / "summary.md"
            ExperimentReport().write(summary_inputs, summary_path, title=self.manifest.get("title", "EviGraph Manifest Summary"))
            artifacts["summary"] = str(summary_path)
        card_path = self.output_dir / "experiment_card.md"
        artifacts["card"] = ExperimentCard().write(self.manifest_path, self.manifest, artifacts, card_path)
        return artifacts

    def _run_experiment(
        self,
        experiment: dict[str, Any],
        dataset_name: str,
        questions_path: Path,
        corpus_path: Path | None,
        base_config: dict[str, Any],
        output_path: Path,
        retrieval_mode: str,
    ) -> None:
        kind = experiment.get("type", "batch")
        if kind == "pareto":
            self._run_pareto(experiment, dataset_name, questions_path, corpus_path, base_config, output_path, retrieval_mode)
            return
        self._run_batch(experiment, dataset_name, questions_path, corpus_path, base_config, output_path, retrieval_mode)

    def _run_batch(
        self,
        experiment: dict[str, Any],
        dataset_name: str,
        questions_path: Path,
        corpus_path: Path | None,
        base_config: dict[str, Any],
        output_path: Path,
        retrieval_mode: str,
    ) -> None:
        methods = experiment.get("methods", DEFAULT_ABLATION_METHODS)
        self._validate_methods(methods)
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
            "citation_correct",
            "misleading_acceptance",
            "input_tokens",
            "tool_calls",
            "latency_ms",
            "run_dir",
        ]
        with questions_path.open("r", encoding="utf-8") as input_handle, output_path.open(
            "w", encoding="utf-8", newline=""
        ) as output_handle:
            writer = csv.DictWriter(output_handle, fieldnames=fieldnames)
            writer.writeheader()
            for line in input_handle:
                sample = json.loads(line)
                for method in methods:
                    result = MethodRunner(deepcopy(base_config)).run(
                        sample["query"],
                        method,
                        corpus_path=str(corpus_path) if corpus_path else None,
                        source_doc=sample.get("source_doc"),
                        retrieval_mode=retrieval_mode,
                    )
                    metrics = summarize_result(result, sample.get("answer"))
                    writer.writerow(
                        {
                            "dataset": dataset_name,
                            "experiment": experiment["name"],
                            "id": sample.get("id"),
                            "method": method,
                            "query": sample["query"],
                            "answer": sample.get("answer"),
                            "prediction": result["answer"]["text"],
                            **metrics,
                            "run_dir": result["artifacts"]["run_dir"],
                        }
                    )

    def _run_pareto(
        self,
        experiment: dict[str, Any],
        dataset_name: str,
        questions_path: Path,
        corpus_path: Path | None,
        base_config: dict[str, Any],
        output_path: Path,
        retrieval_mode: str,
    ) -> None:
        budgets = [int(value) for value in experiment.get("budgets", [1, 2, 4, 8])]
        method = experiment.get("method", "full_evigraph")
        self._validate_methods([method])
        fieldnames = [
            "dataset",
            "experiment",
            "id",
            "method",
            "budget_nodes",
            "accuracy",
            "answer_supported",
            "citation_correct",
            "misleading_acceptance",
            "input_tokens",
            "tool_calls",
            "latency_ms",
        ]
        with questions_path.open("r", encoding="utf-8") as input_handle:
            samples = [json.loads(line) for line in input_handle]

        with output_path.open("w", encoding="utf-8", newline="") as output_handle:
            writer = csv.DictWriter(output_handle, fieldnames=fieldnames)
            writer.writeheader()
            for budget in budgets:
                config = deepcopy(base_config)
                config.setdefault("selection", {})["max_nodes"] = budget
                runner = MethodRunner(config)
                for sample in samples:
                    result = runner.run(
                        sample["query"],
                        method,
                        corpus_path=str(corpus_path) if corpus_path else None,
                        source_doc=sample.get("source_doc"),
                        retrieval_mode=retrieval_mode,
                    )
                    metrics = summarize_result(result, sample.get("answer"))
                    writer.writerow(
                        {
                            "dataset": dataset_name,
                            "experiment": experiment["name"],
                            "id": sample.get("id"),
                            "method": method,
                            "budget_nodes": budget,
                            **metrics,
                        }
                    )

    def _prepare_corpus(self, dataset: dict[str, Any]) -> Path | None:
        corpus = dataset.get("corpus")
        if not corpus:
            return None
        corpus_path = self._resolve(corpus)
        if dataset.get("build_index"):
            index_path = self._resolve(dataset.get("index", f"outputs/index/{dataset['name']}.json"))
            LocalIndexBuilder(
                int(dataset.get("chunk_size", 900)),
                int(dataset.get("chunk_overlap", 120)),
            ).build(corpus_path, index_path)
            return index_path
        return corpus_path

    def _prepare_questions(self, dataset: dict[str, Any]) -> Path:
        if not dataset.get("raw_questions"):
            return self._resolve(dataset["questions"])
        output_path = self._resolve(dataset.get("questions", f"outputs/eval/manifest/{dataset['name']}_questions.jsonl"))
        DatasetAdapter().convert(
            self._resolve(dataset["raw_questions"]),
            output_path,
            field_map=dataset.get("field_map"),
            default_task_type=dataset.get("default_task_type"),
            dataset_name=dataset.get("name"),
        )
        return output_path

    def _inspect_dataset(self, dataset: dict[str, Any], questions_path: Path, corpus_path: Path | None) -> dict[str, Path]:
        dataset_name = dataset["name"]
        inspector = DatasetInspector()
        report = inspector.inspect(questions_path, corpus_path)
        report_path = self.output_dir / f"{dataset_name}_inspection.json"
        markdown_path = self.output_dir / f"{dataset_name}_inspection.md"
        gate_path = self.output_dir / f"{dataset_name}_gate.md"
        gate_config = dict(dataset.get("gate", {}))
        gate = BenchmarkGate().evaluate(
            report,
            min_records=int(gate_config.get("min_records", 1)),
            min_source_doc_coverage=float(gate_config.get("min_source_doc_coverage", 1.0)),
            allow_missing_source_doc=bool(gate_config.get("allow_missing_source_doc", False)),
        )
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        inspector.write_markdown(report, markdown_path)
        gate_path.write_text(BenchmarkGate().render_markdown(gate), encoding="utf-8")
        if gate_config.get("fail_on_error", False) and not gate["passed"]:
            raise ValueError(f"Benchmark gate failed for dataset {dataset_name}: {gate}")
        return {"inspection": markdown_path, "gate": gate_path}

    def _validate_methods(self, methods: list[str]) -> None:
        unknown = [method for method in methods if method not in METHODS]
        if unknown:
            raise ValueError(f"Unknown methods: {', '.join(unknown)}")

    def _read_manifest(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Manifest does not exist: {path}")
        if path.suffix.lower() != ".json":
            raise ValueError("Manifest runner currently supports JSON manifests.")
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_config(self, path: str | Path | None) -> dict[str, Any]:
        if path is None:
            return {}
        from scripts.run_query import load_config

        return load_config(str(self._resolve(path)))

    def _resolve(self, path: str | Path) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return self.root / candidate
