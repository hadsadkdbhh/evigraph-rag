from __future__ import annotations

import argparse
import json
import subprocess
import sys
from argparse import Namespace
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local EviGraph-RAG reproducibility pipeline.")
    parser.add_argument(
        "--manifest",
        default=str(ROOT / "configs" / "experiments.finqa_300.local_planner.json"),
        help="Manifest to refresh when --refresh-results is set.",
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
    args = parser.parse_args()

    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    steps: list[StepResult] = []

    steps.append(run_preflight(args))
    if not steps[-1].ok:
        return write_report(args, report_dir, steps)

    if not args.skip_tests:
        steps.append(run_step("unit_tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests"]))

    if args.refresh_results:
        steps.append(run_step("finqa_300_manifest", [sys.executable, "scripts/run_manifest.py", "--manifest", args.manifest]))

    if not args.skip_paper_assets:
        steps.append(
            run_step(
                "paper_assets",
                [
                    sys.executable,
                    "scripts/build_paper_assets.py",
                    "--eval-dir",
                    args.eval_dir,
                    "--output-dir",
                    args.paper_output_dir,
                    "--preset",
                    "finqa_300_local",
                ],
            )
        )

    return write_report(args, report_dir, steps)


def write_report(args: Namespace, report_dir: Path, steps: list[StepResult]) -> int:
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "refresh_results": args.refresh_results,
        "steps": [step.__dict__ | {"ok": step.ok} for step in steps],
        "ok": all(step.ok for step in steps),
        "artifacts": {
            "eval_dir": str(Path(args.eval_dir)),
            "paper_output_dir": str(Path(args.paper_output_dir)),
            "markdown_summary": str(Path(args.paper_output_dir) / "finqa_results_summary.md"),
            "latex_tables": str(Path(args.paper_output_dir) / "finqa_results_tables.tex"),
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
    manifest_path = resolve_path(args.manifest)
    eval_dir = resolve_path(args.eval_dir)

    if not manifest_path.exists():
        errors.append(f"manifest not found: {display_path(str(manifest_path))}")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"manifest is not valid JSON: {display_path(str(manifest_path))}: {exc}")
        else:
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

    if not args.refresh_results and not args.skip_paper_assets:
        csvs = list(eval_dir.glob("*.csv")) if eval_dir.exists() else []
        if not csvs:
            errors.append(
                "evaluation CSVs are missing; run `python scripts/run_pipeline.py --refresh-results` "
                "once on a clean checkout before using the quick pipeline"
            )
        else:
            notes.append(f"found {len(csvs)} evaluation CSV files in {display_path(str(eval_dir))}")

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
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
