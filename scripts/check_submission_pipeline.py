from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class RequiredArtifact:
    name: str
    path: str


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class CommandResult:
    name: str
    command: tuple[str, ...]
    returncode: int
    stdout_tail: str
    stderr_tail: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0


REQUIRED_ARTIFACTS = (
    RequiredArtifact("AAAI main paper", "paper/main.tex"),
    RequiredArtifact("AAAI supplement wrapper", "paper/supplement.tex"),
    RequiredArtifact("AAAI appendix", "paper/appendix.tex"),
    RequiredArtifact("Official AAAI style", "paper/aaai2027.sty"),
    RequiredArtifact("Official AAAI bibliography style", "paper/aaai2027.bst"),
    RequiredArtifact("Main pipeline figure", "paper/figures/evigraph_pipeline.pdf"),
    RequiredArtifact("Retrieval portfolio figure", "paper/figures/retrieval_portfolio_mechanism.pdf"),
    RequiredArtifact(
        "FinQA-600 main closure table",
        "paper/generated/finqa_600_submission_component_closure_v48/finqa_main_tables.tex",
    ),
    RequiredArtifact(
        "FinQA-600 full diagnostic tables",
        "paper/generated/finqa_600_submission_component_closure_v48/finqa_results_tables.tex",
    ),
    RequiredArtifact(
        "FinQA-600 closure summary",
        "paper/generated/finqa_600_submission_component_closure_v48/finqa_results_summary.md",
    ),
    RequiredArtifact(
        "Retrieval portfolio ablation table",
        "paper/generated/retrieval_portfolio_ablation/finqa_retrieval_portfolio_ablation.tex",
    ),
    RequiredArtifact(
        "Statistical confidence table",
        "paper/generated/statistical_confidence/main_confidence_table.tex",
    ),
    RequiredArtifact("TAT-QA-50 portability table", "paper/generated/tatqa_50_cross_benchmark/tatqa_50_results.tex"),
    RequiredArtifact("TAT-QA-100 portability table", "paper/generated/tatqa_100_portability_v50/tatqa_100_results.tex"),
    RequiredArtifact("Submission artifact index", "docs/submission_artifact_index.md"),
    RequiredArtifact("Experiment closure definition", "docs/experiments/submission_closure.md"),
    RequiredArtifact("Experiment closure check report", "docs/experiments/submission_closure_check.md"),
    RequiredArtifact("Experiment results index", "docs/experiments/results_index.md"),
    RequiredArtifact("Code/data release note", "docs/code_data_release_note.md"),
)


LATEX_LOGS = (
    "outputs/latex_sandbox/build/main.log",
    "outputs/latex_sandbox/build/supplement.log",
)


LATEX_BLOCKERS = (
    "undefined references",
    "undefined citations",
    "there were undefined references",
    "citation `",
    "reference `",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the final no-API engineering gate for the EviGraph-RAG submission package."
    )
    parser.add_argument("--output", default="docs/submission_pipeline_check.md")
    parser.add_argument("--skip-tests", action="store_true", help="Skip unittest discovery.")
    parser.add_argument("--skip-page-budget", action="store_true", help="Skip the official AAAI page-budget compile.")
    parser.add_argument(
        "--include-output",
        action="store_true",
        help="Include command output tails even when all gates pass.",
    )
    args = parser.parse_args()

    commands: list[CommandResult] = []
    checks: list[CheckResult] = []

    if not args.skip_tests:
        commands.append(run_command("unit tests", (sys.executable, "-m", "unittest", "discover", "-s", "tests")))

    commands.append(
        run_command(
            "submission experiment closure",
            (sys.executable, "scripts/check_experiment_closure.py", "--output", "docs/experiments/submission_closure_check.md"),
        )
    )

    if not args.skip_page_budget:
        commands.append(
            run_command(
                "official AAAI page budget",
                (
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    "scripts/check_aaai_page_budget.ps1",
                    "-AlsoCompileSupplement",
                ),
            )
        )

    checks.extend(check_required_artifacts(ROOT))
    if not args.skip_page_budget:
        checks.extend(check_latex_logs(ROOT))

    passed = all(command.passed for command in commands) and all(check.passed for check in checks)
    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(commands, checks, passed, include_output=args.include_output), encoding="utf-8")
    print(str(output_path))
    return 0 if passed else 1


def run_command(name: str, command: tuple[str, ...]) -> CommandResult:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    return CommandResult(
        name=name,
        command=command,
        returncode=completed.returncode,
        stdout_tail=tail(completed.stdout),
        stderr_tail=tail(completed.stderr),
    )


def check_required_artifacts(
    root: Path, artifacts: tuple[RequiredArtifact, ...] = REQUIRED_ARTIFACTS
) -> list[CheckResult]:
    results: list[CheckResult] = []
    for artifact in artifacts:
        path = root / artifact.path
        if path.exists() and path.stat().st_size > 0:
            results.append(CheckResult(artifact.name, True, artifact.path))
        elif path.exists():
            results.append(CheckResult(artifact.name, False, f"empty: {artifact.path}"))
        else:
            results.append(CheckResult(artifact.name, False, f"missing: {artifact.path}"))
    return results


def check_latex_logs(root: Path, logs: tuple[str, ...] = LATEX_LOGS) -> list[CheckResult]:
    results: list[CheckResult] = []
    for log_path in logs:
        path = root / log_path
        if not path.exists():
            results.append(CheckResult(f"LaTeX log {log_path}", False, f"missing: {log_path}"))
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        blockers = latex_blockers(text)
        if blockers:
            results.append(CheckResult(f"LaTeX log {log_path}", False, "; ".join(blockers[:5])))
        else:
            results.append(CheckResult(f"LaTeX log {log_path}", True, "no undefined references or citations"))
    return results


def latex_blockers(text: str) -> list[str]:
    blockers: list[str] = []
    for line in text.splitlines():
        lowered = line.lower()
        if "undefined" in lowered and any(marker in lowered for marker in LATEX_BLOCKERS):
            blockers.append(line.strip())
        elif "latex warning:" in lowered and any(marker in lowered for marker in ("citation `", "reference `")):
            blockers.append(line.strip())
    return blockers


def render_report(commands: list[CommandResult], checks: list[CheckResult], passed: bool, include_output: bool = False) -> str:
    lines = [
        "# Submission Pipeline Check",
        "",
        f"Created UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"Overall status: {'PASS' if passed else 'BLOCKED'}",
        "",
        "## Command Gates",
        "",
        "| Gate | Status | Command |",
        "| --- | --- | --- |",
    ]
    for command in commands:
        lines.append(
            f"| {command.name} | {'PASS' if command.passed else f'FAIL ({command.returncode})'} | "
            f"`{' '.join(command.command)}` |"
        )
    lines.extend(["", "## Artifact And Log Gates", "", "| Gate | Status | Detail |", "| --- | --- | --- |"])
    for check in checks:
        detail = check.detail.replace("|", "\\|")
        lines.append(f"| {check.name} | {'PASS' if check.passed else 'FAIL'} | {detail} |")
    if include_output or not passed:
        lines.extend(["", "## Command Output Tails", ""])
        for command in commands:
            lines.append(f"### {command.name}")
            lines.append("")
            if command.stdout_tail:
                lines.append("stdout:")
                lines.append("")
                lines.append("```text")
                lines.append(command.stdout_tail)
                lines.append("```")
            if command.stderr_tail:
                lines.append("stderr:")
                lines.append("")
                lines.append("```text")
                lines.append(command.stderr_tail)
                lines.append("```")
            if not command.stdout_tail and not command.stderr_tail:
                lines.append("No output.")
            lines.append("")
    return "\n".join(lines)


def tail(text: str, limit: int = 2500) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[-limit:]


if __name__ == "__main__":
    raise SystemExit(main())
