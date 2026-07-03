from __future__ import annotations

import csv
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ExperimentCard:
    def write(
        self,
        manifest_path: str | Path,
        manifest: dict[str, Any],
        artifacts: dict[str, Any],
        output_path: str | Path,
    ) -> str:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render(manifest_path, manifest, artifacts), encoding="utf-8")
        return str(output)

    def render(self, manifest_path: str | Path, manifest: dict[str, Any], artifacts: dict[str, Any]) -> str:
        lines = [
            f"# {manifest.get('title', 'EviGraph Experiment Card')}",
            "",
            "## Run Metadata",
            "",
            f"- Created UTC: `{datetime.now(timezone.utc).isoformat()}`",
            f"- Manifest: `{manifest_path}`",
            f"- Git commit: `{self._git_commit()}`",
            f"- Python: `{sys.version.split()[0]}`",
            f"- Platform: `{platform.platform()}`",
            "",
            "## Datasets",
            "",
            self._datasets_table(manifest),
            "",
            "## Experiments",
            "",
            self._experiments_table(manifest),
            "",
            "## Artifacts",
            "",
            self._artifacts_table(artifacts),
            "",
            "## Result Files",
            "",
            self._result_files_table(artifacts.get("evaluations", [])),
            "",
            "## Reproducibility Notes",
            "",
            "- The default mock setup is deterministic and uses no external model calls.",
            "- Outputs under `outputs/` are generated artifacts and are intentionally not committed.",
            "- JSON manifests are used to avoid non-standard dependencies in the current MVP.",
            "",
            "## Current Limitations",
            "",
            *[self._limitation_line(item) for item in manifest.get("limitations", self._default_limitations())],
            "",
        ]
        return "\n".join(lines).rstrip() + "\n"

    def _datasets_table(self, manifest: dict[str, Any]) -> str:
        datasets = manifest.get("datasets", [])
        if not datasets:
            return "No datasets declared."
        lines = [
            "| dataset | questions | raw_questions | corpus | index |",
            "| --- | --- | --- | --- | --- |",
        ]
        for dataset in datasets:
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(dataset.get("name", "")),
                        str(dataset.get("questions", "")),
                        str(dataset.get("raw_questions", "")),
                        str(dataset.get("corpus", "")),
                        str(dataset.get("index", "")),
                    ]
                )
                + " |"
            )
        return "\n".join(lines)

    def _experiments_table(self, manifest: dict[str, Any]) -> str:
        experiments = manifest.get("experiments", [])
        if not experiments:
            return "No experiments declared."
        lines = [
            "| experiment | type | methods | budgets |",
            "| --- | --- | --- | --- |",
        ]
        for experiment in experiments:
            methods = experiment.get("methods", experiment.get("method", ""))
            budgets = experiment.get("budgets", "")
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(experiment.get("name", "")),
                        str(experiment.get("type", "batch")),
                        self._join(methods),
                        self._join(budgets),
                    ]
                )
                + " |"
            )
        return "\n".join(lines)

    def _artifacts_table(self, artifacts: dict[str, Any]) -> str:
        lines = [
            "| kind | path |",
            "| --- | --- |",
        ]
        for key in (
            "converted",
            "inspections",
            "gates",
            "indexes",
            "evaluations",
            "failure_reports",
            "row_operation_diagnostics",
            "process_traces",
        ):
            for path in artifacts.get(key, []):
                lines.append(f"| {key} | `{self._display_path(path)}` |")
        if artifacts.get("summary"):
            lines.append(f"| summary | `{self._display_path(artifacts['summary'])}` |")
        return "\n".join(lines) if len(lines) > 2 else "No artifacts recorded."

    def _result_files_table(self, csv_paths: list[str]) -> str:
        if not csv_paths:
            return "No result CSV files recorded."
        lines = [
            "| file | rows | columns |",
            "| --- | ---: | --- |",
        ]
        for path_text in csv_paths:
            path = Path(path_text)
            if not path.exists():
                lines.append(f"| `{path_text}` | 0 | missing |")
                continue
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
                columns = ", ".join(reader.fieldnames or [])
            lines.append(f"| `{self._display_path(path_text)}` | {len(rows)} | {columns} |")
        return "\n".join(lines)

    def _git_commit(self) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                text=True,
                capture_output=True,
                check=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return "unknown"
        return result.stdout.strip()

    def _join(self, value: Any) -> str:
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return str(value)

    def _display_path(self, path_text: str) -> str:
        path = Path(path_text)
        try:
            return str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(path)

    def _limitation_line(self, item: str) -> str:
        return f"- {item}"

    def _default_limitations(self) -> list[str]:
        return [
            "The mock dataset is too small to support paper-level claims.",
            "The current retrieval backend is lexical and does not yet test embedding retrievers.",
            "Multimodal evidence is represented through text/table surrogates in the MVP.",
            "Metrics are MVP-level and should be expanded before paper submission.",
        ]
