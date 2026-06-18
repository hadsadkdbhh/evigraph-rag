from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class CheckResult:
    name: str
    command: list[str]
    passed: bool
    returncode: int
    duration_seconds: float


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the MVP0 acceptance checks for EviGraph-RAG.")
    parser.add_argument(
        "--with-finqa",
        action="store_true",
        help="Also run the 100-example FinQA manifest. This is slower but verifies the real-subset loop.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "outputs" / "eval" / "mvp0_acceptance"),
        help="Directory for the JSON and Markdown acceptance reports.",
    )
    args = parser.parse_args()

    python = sys.executable
    checks: list[tuple[str, list[str]]] = [
        ("unit_tests", [python, "scripts/run_tests.py"]),
        (
            "feasibility_suite",
            [
                python,
                "scripts/run_feasibility.py",
                "--corpus",
                "data/corpus",
                "--report",
                "outputs/eval/mvp0_acceptance/feasibility_report.json",
            ],
        ),
        ("mock_manifest", [python, "scripts/run_manifest.py", "--manifest", "configs/experiments.mock.json"]),
        ("stress_manifest", [python, "scripts/run_manifest.py", "--manifest", "configs/experiments.stress.json"]),
    ]
    if args.with_finqa:
        checks.append(("finqa_manifest", [python, "scripts/run_manifest.py", "--manifest", "configs/experiments.finqa.json"]))

    results = [_run_check(name, command) for name, command in checks]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_reports(output_dir, results, args.with_finqa)

    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    print(f"[mvp0] acceptance complete: {passed} passed, {failed} failed")
    print(f"[mvp0] report: {output_dir / 'acceptance_report.md'}")
    return 0 if failed == 0 else 1


def _run_check(name: str, command: Sequence[str]) -> CheckResult:
    printable = " ".join(command)
    print(f"[mvp0] running {name}: {printable}", flush=True)
    start = time.perf_counter()
    completed = subprocess.run(list(command), cwd=ROOT)
    duration = time.perf_counter() - start
    passed = completed.returncode == 0
    status = "passed" if passed else "failed"
    print(f"[mvp0] {name} {status} in {duration:.1f}s", flush=True)
    return CheckResult(
        name=name,
        command=list(command),
        passed=passed,
        returncode=completed.returncode,
        duration_seconds=round(duration, 3),
    )


def _write_reports(output_dir: Path, results: list[CheckResult], with_finqa: bool) -> None:
    passed = sum(1 for result in results if result.passed)
    payload = {
        "summary": {
            "passed": passed,
            "failed": len(results) - passed,
            "with_finqa": with_finqa,
        },
        "checks": [asdict(result) for result in results],
    }
    (output_dir / "acceptance_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# MVP0 Acceptance Report",
        "",
        f"- Passed: {payload['summary']['passed']}",
        f"- Failed: {payload['summary']['failed']}",
        f"- FinQA manifest included: {with_finqa}",
        "",
        "| check | status | seconds |",
        "| --- | --- | ---: |",
    ]
    for result in results:
        status = "PASS" if result.passed else f"FAIL ({result.returncode})"
        lines.append(f"| {result.name} | {status} | {result.duration_seconds:.1f} |")
    lines.extend(["", "## Commands", ""])
    for result in results:
        lines.append(f"- `{result.name}`: `{' '.join(result.command)}`")
    lines.append("")
    (output_dir / "acceptance_report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
