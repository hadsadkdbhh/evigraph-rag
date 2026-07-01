from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from argparse import Namespace
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.pipeline import ExperimentClosureGate


@dataclass
class StepResult:
    name: str
    command: list[str]
    returncode: int
    stdout_tail: str
    stderr_tail: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass(frozen=True)
class ExperimentPipeline:
    name: str
    manifest: str
    eval_dir: str
    paper_output_dir: str
    preset: str
    requires_llm: bool = False


MAIN_PIPELINE = (
    ExperimentPipeline(
        name="finqa_300_local",
        manifest="configs/experiments.finqa_300.local_planner.json",
        eval_dir="outputs/eval/finqa_300_local_planner",
        paper_output_dir="paper/generated/finqa_300_local_planner",
        preset="finqa_300_local",
    ),
)


SUBMISSION_PIPELINE = (
    *MAIN_PIPELINE,
    ExperimentPipeline(
        name="finqa_300_local_ablation",
        manifest="configs/experiments.finqa_300.local_planner_ablation.json",
        eval_dir="outputs/eval/finqa_300_local_planner_ablation",
        paper_output_dir="paper/generated/finqa_300_local_planner_ablation",
        preset="finqa_300_local_ablation",
    ),
    ExperimentPipeline(
        name="finqa_300_retrieval_baselines",
        manifest="configs/experiments.finqa_300.local_planner_retrieval_baselines.json",
        eval_dir="outputs/eval/finqa_300_local_planner_retrieval_baselines",
        paper_output_dir="paper/generated/finqa_300_local_planner_retrieval_baselines",
        preset="finqa_300_local_retrieval_baselines",
    ),
    ExperimentPipeline(
        name="finqa_600_local",
        manifest="configs/experiments.finqa_600.local_planner.json",
        eval_dir="outputs/eval/finqa_600_local_planner",
        paper_output_dir="paper/generated/finqa_600_local_planner",
        preset="finqa_600_local",
    ),
    ExperimentPipeline(
        name="finqa_300_llm_direct_rag",
        manifest="configs/experiments.finqa_300.llm_direct_rag.json",
        eval_dir="outputs/eval/finqa_300_llm_direct_rag",
        paper_output_dir="paper/generated/finqa_300_llm_direct_rag",
        preset="finqa_300_llm_direct_rag",
        requires_llm=True,
    ),
    ExperimentPipeline(
        name="finqa_600_llm_direct_rag",
        manifest="configs/experiments.finqa_600.llm_direct_rag.json",
        eval_dir="outputs/eval/finqa_600_llm_direct_rag",
        paper_output_dir="paper/generated/finqa_600_llm_direct_rag",
        preset="finqa_600_llm_direct_rag",
        requires_llm=True,
    ),
)


LLM_ENV_VARS = ("LLM_PROVIDER", "LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local EviGraph-RAG reproducibility pipeline.")
    parser.add_argument(
        "--suite",
        choices=("main", "submission"),
        default="main",
        help="Run the main FinQA-300 closure or the full submission experiment suite.",
    )
    parser.add_argument(
        "--manifest",
        default=str(ROOT / "configs" / "experiments.finqa_300.local_planner.json"),
        help="Manifest to refresh when --refresh-results is set and --suite=main.",
    )
    parser.add_argument(
        "--eval-dir",
        default=str(ROOT / "outputs" / "eval" / "finqa_300_local_planner"),
        help="Evaluation directory used for paper assets.",
    )
    parser.add_argument(
        "--paper-output-dir",
        default=str(ROOT / "paper" / "generated" / "finqa_300_local_planner"),
        help="Output directory for generated paper assets.",
    )
    parser.add_argument(
        "--report-dir",
        default=str(ROOT / "outputs" / "pipeline"),
        help="Directory for pipeline reports.",
    )
    parser.add_argument("--refresh-results", action="store_true", help="Run the manifest before building assets.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip unittest discovery.")
    parser.add_argument("--skip-paper-assets", action="store_true", help="Skip paper asset generation.")
    parser.add_argument("--skip-closure", action="store_true", help="Skip experiment artifact closure checks.")
    parser.add_argument(
        "--skip-llm-direct-rag",
        action="store_true",
        help="Skip API-backed LLM Direct RAG baselines in the submission suite.",
    )
    args = parser.parse_args()

    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    steps: list[StepResult] = []

    steps.append(run_preflight(args))
    if not steps[-1].ok:
        return write_report(args, report_dir, steps)

    if not args.skip_tests:
        steps.append(run_step("unit_tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests"]))

    for experiment in experiment_pipelines(args):
        if experiment.requires_llm:
            if args.skip_llm_direct_rag:
                steps.append(skipped_step(f"{experiment.name}_llm_preflight", "LLM Direct RAG skipped by flag."))
                continue
            steps.append(run_llm_preflight(experiment.name))
            if not steps[-1].ok:
                continue

        if args.refresh_results:
            steps.append(
                run_step(
                    f"{experiment.name}_manifest",
                    [sys.executable, "scripts/run_manifest.py", "--manifest", str(ROOT / experiment.manifest)],
                )
            )

        if not args.skip_paper_assets:
            steps.append(
                run_step(
                    f"{experiment.name}_paper_assets",
                    [
                        sys.executable,
                        "scripts/build_paper_assets.py",
                        "--eval-dir",
                        str(ROOT / experiment.eval_dir),
                        "--output-dir",
                        str(ROOT / experiment.paper_output_dir),
                        "--preset",
                        experiment.preset,
                    ],
                )
            )

        if not args.skip_closure:
            steps.append(run_experiment_closure_for(experiment, report_dir / experiment.name))

    return write_report(args, report_dir, steps)


def write_report(args: Namespace, report_dir: Path, steps: list[StepResult]) -> int:
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "suite": args.suite,
        "refresh_results": args.refresh_results,
        "steps": [step.__dict__ | {"ok": step.ok} for step in steps],
        "ok": all(step.ok for step in steps),
        "artifacts": {
            "eval_dir": str(Path(args.eval_dir)),
            "paper_output_dir": str(Path(args.paper_output_dir)),
            "markdown_summary": str(Path(args.paper_output_dir) / "finqa_results_summary.md"),
            "latex_tables": str(Path(args.paper_output_dir) / "finqa_results_tables.tex"),
            "experiment_closure": str(report_dir / "experiment_closure_report.md"),
        },
    }
    report_stem = "pipeline_report_full_refresh" if args.refresh_results else "pipeline_report_quick"
    report_json = json.dumps(report, indent=2)
    report_markdown = render_markdown(report)
    (report_dir / "pipeline_report.json").write_text(report_json, encoding="utf-8")
    (report_dir / "pipeline_report.md").write_text(report_markdown, encoding="utf-8")
    (report_dir / f"{report_stem}.json").write_text(report_json, encoding="utf-8")
    (report_dir / f"{report_stem}.md").write_text(report_markdown, encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


def run_preflight(args: Namespace) -> StepResult:
    errors: list[str] = []
    notes: list[str] = []
    for experiment in experiment_pipelines(args):
        if experiment.requires_llm and getattr(args, "skip_llm_direct_rag", False):
            notes.append(f"{experiment.name}: skipped LLM Direct RAG by flag")
            continue
        _validate_manifest_inputs(resolve_path(experiment.manifest), errors)

        if not args.refresh_results and not args.skip_paper_assets and not experiment.requires_llm:
            eval_dir = resolve_path(experiment.eval_dir)
            csvs = list(eval_dir.glob("*.csv")) if eval_dir.exists() else []
            if not csvs:
                if getattr(args, "suite", "main") == "submission":
                    errors.append(
                        f"{experiment.name}: evaluation CSVs are missing; run "
                        "`python scripts/run_pipeline.py --suite submission --refresh-results` "
                        "once before using the quick submission pipeline"
                    )
                else:
                    errors.append(
                        "evaluation CSVs are missing; run `python scripts/run_pipeline.py --refresh-results` "
                        "once on a clean checkout before using the quick pipeline"
                    )
            else:
                notes.append(
                    f"{experiment.name}: found {len(csvs)} evaluation CSV files in {display_path(str(eval_dir))}"
                )

    if args.refresh_results:
        notes.append("refresh mode will rebuild index, evaluation CSVs, diagnostics, and paper assets")

    stdout = "\n".join(notes) if notes else "preflight checks passed"
    stderr = "\n".join(errors)
    return StepResult(
        name="preflight",
        command=["internal", "preflight"],
        returncode=1 if errors else 0,
        stdout_tail=stdout,
        stderr_tail=stderr,
    )


def _validate_manifest_inputs(manifest_path: Path, errors: list[str]) -> None:
    if not manifest_path.exists():
        errors.append(f"manifest not found: {display_path(str(manifest_path))}")
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"manifest is not valid JSON: {display_path(str(manifest_path))}: {exc}")
        return

    config_path = manifest.get("config")
    if config_path and not resolve_path(str(config_path)).exists():
        errors.append(f"config not found: {config_path}")
    for dataset in manifest.get("datasets", []):
        raw_questions = dataset.get("raw_questions")
        corpus = dataset.get("corpus")
        if raw_questions and not resolve_path(str(raw_questions)).exists():
            errors.append(f"raw questions not found: {raw_questions}")
        if corpus and not resolve_path(str(corpus)).exists():
            errors.append(f"corpus not found: {corpus}")


def run_experiment_closure(args: Namespace, report_dir: Path) -> StepResult:
    experiment = ExperimentPipeline(
        name="finqa_300_local",
        manifest=str(Path(args.manifest)),
        eval_dir=str(Path(args.eval_dir)),
        paper_output_dir=str(Path(args.paper_output_dir)),
        preset="finqa_300_local",
    )
    return run_experiment_closure_for(experiment, report_dir)


def run_experiment_closure_for(experiment: ExperimentPipeline, report_dir: Path) -> StepResult:
    result = ExperimentClosureGate().evaluate(
        manifest_path=str(resolve_path(experiment.manifest)),
        eval_dir=str(resolve_path(experiment.eval_dir)),
        paper_output_dir=str(resolve_path(experiment.paper_output_dir)),
        report_dir=report_dir,
    )
    failed = [check for check in result["checks"] if not check["ok"]]
    metrics = [
        f"{item['experiment']}/{item['method']}: accuracy={item['accuracy']:.3f}, rows={item['rows']}"
        for item in result["metrics"]
    ]
    stdout = "\n".join(metrics + [f"closure report: {display_path(result['artifacts']['closure_report_markdown'])}"])
    stderr = "\n".join(f"{check['name']}: {check['detail']}" for check in failed)
    return StepResult(
        name=f"{experiment.name}_experiment_closure",
        command=["internal", "experiment_closure"],
        returncode=0 if result["ok"] else 1,
        stdout_tail=stdout,
        stderr_tail=stderr,
    )


def experiment_pipelines(args: Namespace) -> tuple[ExperimentPipeline, ...]:
    if getattr(args, "suite", "main") == "submission":
        return SUBMISSION_PIPELINE
    return (
        ExperimentPipeline(
            name="finqa_300_local",
            manifest=str(Path(args.manifest)),
            eval_dir=str(Path(args.eval_dir)),
            paper_output_dir=str(Path(args.paper_output_dir)),
            preset="finqa_300_local",
        ),
    )


def run_llm_preflight(name: str) -> StepResult:
    missing = [key for key in LLM_ENV_VARS if not os.environ.get(key)]
    if missing:
        return StepResult(
            name=f"{name}_llm_preflight",
            command=["internal", "llm_preflight"],
            returncode=1,
            stdout_tail="",
            stderr_tail="missing LLM environment variables: " + ", ".join(missing),
        )
    return StepResult(
        name=f"{name}_llm_preflight",
        command=["internal", "llm_preflight"],
        returncode=0,
        stdout_tail="LLM Direct RAG environment is configured.",
        stderr_tail="",
    )


def skipped_step(name: str, reason: str) -> StepResult:
    return StepResult(name=name, command=["internal", "skip"], returncode=0, stdout_tail=reason, stderr_tail="")


def run_step(name: str, command: list[str]) -> StepResult:
    print(f"[pipeline] {name}: {' '.join(command)}", flush=True)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    stdout_tail = tail(completed.stdout)
    stderr_tail = tail(completed.stderr)
    if stdout_tail:
        print(stdout_tail, flush=True)
    if stderr_tail:
        print(stderr_tail, file=sys.stderr, flush=True)
    print(f"[pipeline] {name}: exit {completed.returncode}", flush=True)
    return StepResult(name, command, completed.returncode, stdout_tail, stderr_tail)


def tail(text: str, lines: int = 40) -> str:
    parts = text.splitlines()
    return "\n".join(parts[-lines:])


def display_path(value: str) -> str:
    path = Path(value)
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def display_command(command: list[str]) -> str:
    return " ".join(display_path(part) if str(part).startswith(str(ROOT)) else str(part) for part in command)


def render_markdown(report: dict) -> str:
    lines = [
        "# EviGraph-RAG Pipeline Report",
        "",
        f"- Created UTC: `{report['created_utc']}`",
        f"- Root: `.`",
        f"- Suite: `{report['suite']}`",
        f"- Refresh results: `{report['refresh_results']}`",
        f"- Overall status: `{'PASS' if report['ok'] else 'FAIL'}`",
        "",
        "## Steps",
        "",
        "| step | status | command |",
        "| --- | --- | --- |",
    ]
    for step in report["steps"]:
        command = display_command(step["command"])
        lines.append(f"| {step['name']} | {'PASS' if step['ok'] else 'FAIL'} | `{command}` |")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Evaluation directory: `{display_path(report['artifacts']['eval_dir'])}`",
            f"- Paper output directory: `{display_path(report['artifacts']['paper_output_dir'])}`",
            f"- Markdown summary: `{display_path(report['artifacts']['markdown_summary'])}`",
            f"- LaTeX tables: `{display_path(report['artifacts']['latex_tables'])}`",
            f"- Experiment closure: `{display_path(report['artifacts']['experiment_closure'])}`",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
